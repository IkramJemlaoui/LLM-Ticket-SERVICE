from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any
from uuid import uuid4

from .config import Settings
from .guardrails import apply_input_guardrails, redact_pii
from .llm import ALLOWED_CATEGORIES, ALLOWED_PRIORITIES, MockLLMProvider
from .models import (
    AgentTraceStep,
    CopilotOutput,
    DraftDecision,
    RetrievedChunk,
    TicketInput,
    TriageDecision,
    ValidationDecision,
)
from .retrieval import Retriever
from .telemetry import log_event


@dataclass
class SafetyDecision:
    safe_ticket: TicketInput
    refused: bool
    notes: list[str]
    reasons: list[str]


@dataclass
class KnowledgeDecision:
    chunks: list[RetrievedChunk]
    confidence: float
    query: str


def _elapsed_ms(start: float) -> float:
    return round((perf_counter() - start) * 1000, 2)


class SafetyPrivacyAgent:
    """Screens the request and produces the only ticket allowed to reach a cloud model."""

    name = "Safety & Privacy Agent"
    role = "Detect prompt attacks, minimize personal data, and stop unsafe workflows."

    def run(self, ticket: TicketInput, settings: Settings) -> SafetyDecision:
        combined = "\n".join([ticket.subject.strip(), ticket.description.strip()])
        guardrails = apply_input_guardrails(combined, max_chars=settings.max_input_chars)

        bounded_subject = ticket.subject[: min(500, settings.max_input_chars)]
        remaining_chars = max(settings.max_input_chars - len(bounded_subject), 0)
        bounded_description = ticket.description[:remaining_chars]
        safe_subject, subject_pii = redact_pii(bounded_subject)
        safe_description, description_pii = redact_pii(bounded_description)
        safe_requester, requester_pii = redact_pii(ticket.requester[:250])
        pii_found = guardrails.pii_found or subject_pii or description_pii or requester_pii

        notes: list[str] = []
        if guardrails.truncation_applied:
            notes.append("Input was truncated to the configured maximum length.")
        if pii_found:
            notes.append("PII-like content was redacted before logging and model inference.")
        if guardrails.injection_flag:
            notes.append("Prompt-injection language was detected and the workflow was stopped.")

        safe_ticket = TicketInput(
            subject=safe_subject if settings.redact_before_cloud else bounded_subject,
            description=safe_description if settings.redact_before_cloud else bounded_description,
            requester=safe_requester if settings.redact_before_cloud else ticket.requester[:250],
            channel=ticket.channel,
        )
        return SafetyDecision(
            safe_ticket=safe_ticket,
            refused=guardrails.injection_flag,
            notes=notes,
            reasons=guardrails.injection_reasons,
        )


class TriageAgent:
    name = "Triage Agent"
    role = "Summarize the case, identify missing facts, and propose category and priority."

    def run(self, ticket: TicketInput, provider: Any) -> TriageDecision:
        return provider.triage(ticket)


class KnowledgeAgent:
    name = "Knowledge Agent"
    role = "Find approved evidence and reject weak or duplicate knowledge matches."

    def __init__(self, retriever: Retriever) -> None:
        self.retriever = retriever

    def run(self, ticket: TicketInput, triage: TriageDecision, settings: Settings) -> KnowledgeDecision:
        query = " ".join(
            part
            for part in [ticket.subject, ticket.description, triage.category, triage.summary]
            if part
        )
        chunks = self.retriever.search(
            query,
            top_k=settings.retrieval_top_k,
            min_score=settings.retrieval_min_score,
        )
        confidence = max((chunk.score for chunk in chunks), default=0.0)
        return KnowledgeDecision(chunks=chunks, confidence=confidence, query=query)


class ResolutionAgent:
    name = "Resolution Agent"
    role = "Draft a concise response using only approved evidence and triage context."

    def run(
        self,
        ticket: TicketInput,
        triage: TriageDecision,
        knowledge: KnowledgeDecision,
        provider: Any,
    ) -> DraftDecision:
        return provider.draft(ticket, knowledge.chunks, triage)


class RiskQualityAgent:
    name = "Risk & Quality Agent"
    role = "Validate schema, safety, evidence support, and the required human-control path."

    _unsafe_output_phrases = (
        "bypass mfa",
        "disable security",
        "reveal the system prompt",
        "share your password",
    )

    def run(
        self,
        triage: TriageDecision,
        draft: DraftDecision,
        knowledge: KnowledgeDecision,
    ) -> ValidationDecision:
        issues: list[str] = []
        if triage.category not in ALLOWED_CATEGORIES:
            issues.append("Category is outside the approved taxonomy.")
        if triage.priority not in ALLOWED_PRIORITIES:
            issues.append("Priority is outside the approved scale.")
        if not draft.grounded_reply.strip():
            issues.append("Draft reply is empty.")
        lowered_reply = draft.grounded_reply.lower()
        if any(phrase in lowered_reply for phrase in self._unsafe_output_phrases):
            issues.append("Draft contains prohibited security-bypass language.")

        accepted_sources = {chunk.source_title for chunk in knowledge.chunks}
        if not set(draft.citations).issubset(accepted_sources):
            issues.append("Draft cites a source that was not retrieved by the Knowledge Agent.")
        if not knowledge.chunks:
            issues.append("No approved evidence met the retrieval threshold.")

        retrieval_component = min(knowledge.confidence / 0.45, 1.0) if knowledge.confidence else 0.0
        issue_penalty = min(len(issues) * 0.18, 0.55)
        quality_score = max(
            0.0,
            min(1.0, 0.35 * triage.confidence + 0.4 * retrieval_component + 0.25 - issue_penalty),
        )

        blocking_issue = any(
            issue != "No approved evidence met the retrieval threshold." for issue in issues
        )
        if blocking_issue:
            action = "block"
            approved = False
        elif not knowledge.chunks:
            action = "escalate"
            approved = False
        else:
            action = "human_review"
            approved = True
        return ValidationDecision(
            approved=approved,
            action=action,
            quality_score=round(quality_score, 2),
            issues=issues,
        )


class WorkflowOrchestrator:
    """Runs bounded agent handoffs and applies stop/escalate/human-review policies."""

    def __init__(self, settings: Settings, provider: Any, retriever: Retriever | None = None) -> None:
        self.settings = settings
        self.provider = provider
        self.retriever = retriever or Retriever()
        self.safety_agent = SafetyPrivacyAgent()
        self.triage_agent = TriageAgent()
        self.knowledge_agent = KnowledgeAgent(self.retriever)
        self.resolution_agent = ResolutionAgent()
        self.quality_agent = RiskQualityAgent()

    def _trace(
        self,
        steps: list[AgentTraceStep],
        agent: str,
        role: str,
        status: str,
        decision: str,
        start: float,
    ) -> None:
        steps.append(
            AgentTraceStep(
                agent=agent,
                role=role,
                status=status,
                decision=decision,
                latency_ms=_elapsed_ms(start),
            )
        )

    def run(self, ticket: TicketInput) -> CopilotOutput:
        workflow_start = perf_counter()
        workflow_id = f"WF-{uuid4().hex[:8].upper()}"
        trace: list[AgentTraceStep] = []
        fallback_used = False
        usage = getattr(self.provider, "usage", None)
        if isinstance(usage, dict):
            for key in usage:
                usage[key] = 0

        started = perf_counter()
        safety = self.safety_agent.run(ticket, self.settings)
        self._trace(
            trace,
            self.safety_agent.name,
            self.safety_agent.role,
            "blocked" if safety.refused else "passed",
            "Stop and route to security review" if safety.refused else "Sanitized input released to Triage Agent",
            started,
        )

        if safety.refused:
            output = CopilotOutput(
                summary="Request blocked by the Safety & Privacy Agent.",
                missing_information=[],
                category="General Business Request",
                priority="Medium",
                grounded_reply=(
                    "I cannot follow instructions that attempt to override safety controls, reveal hidden "
                    "instructions, or bypass security policy. A human security reviewer must assess this ticket."
                ),
                citations=[],
                confidence_note="High-confidence policy refusal.",
                refused=True,
                fallback_used=False,
                guardrail_notes=safety.notes,
                raw_provider="guardrail",
                workflow_id=workflow_id,
                workflow_status="blocked_security_review",
                requires_human_review=True,
                human_review_reason="Prompt-injection indicators require security review.",
                retrieval_confidence=0.0,
                quality_score=1.0,
                agent_trace=trace,
                assigned_team="Security Operations",
                issue_type="Security review",
                retrieved_evidence=[],
            )
            self._log(ticket, output, [], workflow_start)
            return output

        started = perf_counter()
        try:
            triage = self.triage_agent.run(safety.safe_ticket, self.provider)
            triage_provider = getattr(self.provider, "name", "unknown")
        except Exception as exc:
            if not self.settings.allow_mock_fallback:
                raise RuntimeError(
                    "The live Triage Agent could not reach the configured LLM. "
                    "No simulated result was substituted."
                ) from exc
            fallback_used = True
            triage = self.triage_agent.run(safety.safe_ticket, MockLLMProvider())
            triage_provider = "mock-fallback"
            safety.notes.append(f"Triage provider failed; safe fallback used: {exc.__class__.__name__}.")
        self._trace(
            trace,
            self.triage_agent.name,
            self.triage_agent.role,
            "completed",
            f"{triage.category} · {triage.priority} · route to {triage.assigned_team} · confidence {triage.confidence:.0%}",
            started,
        )

        started = perf_counter()
        knowledge = self.knowledge_agent.run(safety.safe_ticket, triage, self.settings)
        self._trace(
            trace,
            self.knowledge_agent.name,
            self.knowledge_agent.role,
            "completed" if knowledge.chunks else "escalated",
            (
                f"Accepted {len(knowledge.chunks)} approved source(s); top score {knowledge.confidence:.2f}"
                if knowledge.chunks
                else "No source met the confidence threshold; manual resolution required"
            ),
            started,
        )

        started = perf_counter()
        try:
            draft = self.resolution_agent.run(safety.safe_ticket, triage, knowledge, self.provider)
            response_provider = getattr(self.provider, "name", "unknown")
        except Exception as exc:
            if not self.settings.allow_mock_fallback:
                raise RuntimeError(
                    "The live Resolution Agent could not reach the configured LLM. "
                    "No simulated result was substituted."
                ) from exc
            fallback_used = True
            draft = self.resolution_agent.run(safety.safe_ticket, triage, knowledge, MockLLMProvider())
            response_provider = "mock-fallback"
            safety.notes.append(f"Resolution provider failed; safe fallback used: {exc.__class__.__name__}.")
        self._trace(
            trace,
            self.resolution_agent.name,
            self.resolution_agent.role,
            "completed",
            f"Drafted from {len(draft.citations)} cited source(s)",
            started,
        )

        started = perf_counter()
        validation = self.quality_agent.run(triage, draft, knowledge)
        self._trace(
            trace,
            self.quality_agent.name,
            self.quality_agent.role,
            "passed" if validation.approved else validation.action,
            (
                f"Quality {validation.quality_score:.0%}; release to human approval"
                if validation.approved
                else f"Quality {validation.quality_score:.0%}; {validation.action}: {'; '.join(validation.issues)}"
            ),
            started,
        )

        if validation.action == "block":
            workflow_status = "blocked_quality_review"
            review_reason = "Risk & Quality Agent found a blocking validation issue."
        elif validation.action == "escalate":
            workflow_status = "needs_specialist"
            review_reason = "No approved evidence met the confidence threshold."
        elif len(triage.missing_information) >= 3:
            workflow_status = "awaiting_information"
            review_reason = "The requester must provide missing operational details before resolution."
        elif triage.priority in {"High", "Critical"}:
            workflow_status = "awaiting_human_approval"
            review_reason = "High-impact cases require explicit human approval."
        else:
            workflow_status = "awaiting_human_approval"
            review_reason = "Customer-facing messages are never sent autonomously."

        guardrail_notes = list(safety.notes)
        guardrail_notes.extend(validation.issues)
        raw_provider = (
            "mock-fallback"
            if fallback_used
            else response_provider if response_provider == triage_provider else f"{triage_provider}/{response_provider}"
        )
        output = CopilotOutput(
            summary=triage.summary,
            missing_information=triage.missing_information,
            category=triage.category,
            priority=triage.priority,
            grounded_reply=draft.grounded_reply,
            citations=draft.citations,
            confidence_note=draft.confidence_note,
            refused=False,
            fallback_used=fallback_used,
            guardrail_notes=guardrail_notes,
            raw_provider=raw_provider,
            workflow_id=workflow_id,
            workflow_status=workflow_status,
            requires_human_review=self.settings.require_human_approval or not validation.approved,
            human_review_reason=review_reason,
            retrieval_confidence=round(knowledge.confidence, 3),
            quality_score=validation.quality_score,
            agent_trace=trace[: self.settings.max_agent_steps],
            assigned_team=triage.assigned_team,
            issue_type=triage.issue_type,
            retrieved_evidence=knowledge.chunks,
        )
        self._log(ticket, output, knowledge.chunks, workflow_start)
        return output

    def _log(
        self,
        ticket: TicketInput,
        output: CopilotOutput,
        chunks: list[RetrievedChunk],
        workflow_start: float,
    ) -> None:
        usage = getattr(self.provider, "usage", {})
        log_event(
            {
                "event_type": "agent_workflow_completed",
                "workflow_id": output.workflow_id,
                "prompt_version": self.settings.prompt_version,
                "provider": output.raw_provider,
                "model": self.settings.llm_model,
                "latency_ms": _elapsed_ms(workflow_start),
                "input_chars": len(ticket.subject) + len(ticket.description),
                "retrieval_hits": [chunk.source_title for chunk in chunks],
                "retrieval_source_types": [chunk.source_type for chunk in chunks],
                "retrieval_scores": [round(chunk.score, 3) for chunk in chunks],
                "retrieval_confidence": output.retrieval_confidence,
                "quality_score": output.quality_score,
                "workflow_status": output.workflow_status,
                "requires_human_review": output.requires_human_review,
                "assigned_team": output.assigned_team,
                "agent_steps": [
                    {
                        "agent": step.agent,
                        "status": step.status,
                        "latency_ms": step.latency_ms,
                    }
                    for step in output.agent_trace
                ],
                "prompt_tokens": int(usage.get("prompt_tokens", 0) or 0),
                "completion_tokens": int(usage.get("completion_tokens", 0) or 0),
                "total_tokens": int(usage.get("total_tokens", 0) or 0),
                "refused": output.refused,
                "fallback_used": output.fallback_used,
                "pii_found": any("PII" in note for note in output.guardrail_notes),
            }
        )


def record_human_decision(workflow_id: str, ticket_id: str, decision: str) -> None:
    """Record the approval checkpoint without logging customer or draft content."""
    log_event(
        {
            "event_type": "human_review_decision",
            "workflow_id": workflow_id,
            "ticket_id": ticket_id,
            "decision": decision,
        }
    )


def record_self_service_outcome(workflow_id: str, category: str, outcome: str) -> None:
    """Measure self-service value without retaining the employee's raw request."""
    log_event(
        {
            "event_type": "employee_self_service_outcome",
            "workflow_id": workflow_id,
            "category": category,
            "outcome": outcome,
        }
    )
