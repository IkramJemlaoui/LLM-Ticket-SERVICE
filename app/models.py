from dataclasses import dataclass, field
from typing import List, Dict

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
