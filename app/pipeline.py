from __future__ import annotations

from dataclasses import asdict
from time import perf_counter
from typing import Dict, Any

from .config import Settings
from .guardrails import apply_input_guardrails
from .llm import get_provider, MockLLMProvider
from .models import TicketInput, CopilotOutput
from .retrieval import Retriever
from .telemetry import log_event

class TicketCopilot:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self.retriever = Retriever()
        self.provider = get_provider(self.settings)

    def run(self, ticket: TicketInput) -> CopilotOutput:
        start = perf_counter()
        combined = "\n".join([ticket.subject.strip(), ticket.description.strip()])
        guardrails = apply_input_guardrails(combined, max_chars=self.settings.max_input_chars)

        guardrail_notes = []
        if guardrails.truncation_applied:
            guardrail_notes.append("Input was truncated to the configured maximum length.")
        if guardrails.pii_found:
            guardrail_notes.append("PII-like content was redacted for telemetry.")
        if guardrails.injection_flag:
            guardrail_notes.append("Suspicious prompt-injection language was detected.")

        prompt_text = guardrails.redacted_text if self.settings.redact_before_cloud else combined
        safe_ticket = TicketInput(
            subject=ticket.subject,
            description=prompt_text,
            requester=ticket.requester,
            channel=ticket.channel,
        )
        retrieved = self.retriever.search(prompt_text, top_k=self.settings.retrieval_top_k)

        refused = False
        if guardrails.injection_flag and any("reveal" in reason or "hidden" in reason for reason in guardrails.injection_reasons):
            refused = True
            output = CopilotOutput(
                summary="Request refused due to prompt-injection indicators.",
                missing_information=[],
                category="general_inquiry",
                priority="P3",
                grounded_reply="I cannot follow instructions that try to reveal hidden prompts or override safety rules. Please submit a normal IT support issue.",
                citations=[],
                confidence_note="Refused by input guardrails.",
                refused=True,
                fallback_used=False,
                guardrail_notes=guardrail_notes,
                raw_provider="guardrail",
            )
        else:
            fallback_used = False
            try:
                output = self.provider.generate(safe_ticket, retrieved)
            except Exception as exc:
                fallback_used = True
                output = MockLLMProvider().generate(safe_ticket, retrieved)
                output.fallback_used = True
                guardrail_notes.append(f"Cloud provider failed; fell back to mock mode: {exc.__class__.__name__}")

            if not retrieved:
                output.confidence_note = "Low confidence: no relevant approved knowledge found."
                output.grounded_reply += "\n\nPlease add more detail or route this ticket to an agent for manual review."

            output.guardrail_notes = guardrail_notes
            output.refused = refused

        latency_ms = round((perf_counter() - start) * 1000, 2)
        log_event(
            {
                "prompt_version": self.settings.prompt_version,
                "provider": output.raw_provider,
                "model": self.settings.llm_model,
                "latency_ms": latency_ms,
                "retrieval_hits": [chunk.source_title for chunk in retrieved],
                "injection_flag": guardrails.injection_flag,
                "pii_found": guardrails.pii_found,
                "refused": output.refused,
                "fallback_used": output.fallback_used,
            }
        )
        return output
