from dataclasses import dataclass, field
from typing import List

@dataclass
class TicketInput:
    subject: str
    description: str
    requester: str = ""
    channel: str = "web_portal"

@dataclass
class RetrievedChunk:
    source_title: str
    text: str
    score: float
    source_type: str = "knowledge_article"
    source_id: str = ""


@dataclass
class TriageDecision:
    summary: str
    missing_information: List[str]
    category: str
    priority: str
    confidence: float = 0.0
    assigned_team: str = "Enterprise Service Desk"
    issue_type: str = "Internal service request"


@dataclass
class DraftDecision:
    grounded_reply: str
    confidence_note: str
    citations: List[str] = field(default_factory=list)


@dataclass
class ValidationDecision:
    approved: bool
    action: str
    quality_score: float
    issues: List[str] = field(default_factory=list)


@dataclass
class AgentTraceStep:
    agent: str
    role: str
    status: str
    decision: str
    latency_ms: float

@dataclass
class GuardrailResult:
    pii_found: bool
    redacted_text: str
    injection_flag: bool
    injection_reasons: List[str]
    truncation_applied: bool

@dataclass
class CopilotOutput:
    summary: str
    missing_information: List[str]
    category: str
    priority: str
    grounded_reply: str
    citations: List[str] = field(default_factory=list)
    confidence_note: str = ""
    refused: bool = False
    fallback_used: bool = False
    guardrail_notes: List[str] = field(default_factory=list)
    raw_provider: str = "mock"
    workflow_id: str = ""
    workflow_status: str = "completed"
    requires_human_review: bool = True
    human_review_reason: str = "All customer-facing replies require agent approval."
    retrieval_confidence: float = 0.0
    quality_score: float = 0.0
    agent_trace: List[AgentTraceStep] = field(default_factory=list)
    assigned_team: str = "Enterprise Service Desk"
    issue_type: str = "Internal service request"
    retrieved_evidence: List[RetrievedChunk] = field(default_factory=list)
