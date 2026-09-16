from __future__ import annotations

from .agents import WorkflowOrchestrator
from .config import Settings
from .llm import get_provider
from .models import TicketInput, CopilotOutput
from .retrieval import Retriever

class TicketCopilot:
    """Compatibility facade for the bounded multi-agent workflow."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self.retriever = Retriever()
        self.provider = get_provider(self.settings)
        self.orchestrator = WorkflowOrchestrator(
            settings=self.settings,
            provider=self.provider,
            retriever=self.retriever,
        )

    def run(self, ticket: TicketInput) -> CopilotOutput:
        return self.orchestrator.run(ticket)
