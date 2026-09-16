import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from app.config import Settings
from app.models import TicketInput
from app.pipeline import TicketCopilot


USE_CASES = json.loads(
    (PROJECT_ROOT / "data" / "use_case_evaluations.json").read_text(encoding="utf-8")
)


@pytest.mark.parametrize("case", USE_CASES, ids=[case["name"] for case in USE_CASES])
def test_governed_routing_examples(case):
    context = (
        f"\nOperational context: business impact={case['business_impact']}; "
        f"urgency={case['urgency']}; affected users={case['affected_users']}."
    )
    result = TicketCopilot(Settings(llm_provider="mock")).run(
        TicketInput(
            subject=case["subject"],
            description=case["description"] + context,
            requester="evaluation@company.example",
        )
    )

    assert result.assigned_team == case["expected_team"]
    if case.get("expected_outcome"):
        assert result.workflow_status == case["expected_outcome"]
    else:
        assert result.category == case["expected_category"]
