import json as json_module
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.config import Settings
from app.llm import (
    LLMConfigurationError,
    OpenAICompatibleProvider,
    filter_missing_information,
    get_provider,
)
from app.models import TicketInput


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_openai_provider_uses_responses_api_and_strict_schema(monkeypatch):
    captured = {}
    model_output = {
        "summary": "Operations cannot use the data team's delivery.",
        "missing_information": ["Which data product and business process are affected?"],
        "category": "Data & Analytics",
        "priority": "High",
        "confidence": 0.91,
    }

    def fake_post(url, headers, json, timeout):
        captured.update(url=url, headers=headers, payload=json, timeout=timeout)
        return FakeResponse(
            {
                "output": [
                    {
                        "type": "message",
                        "content": [
                            {"type": "output_text", "text": json_module.dumps(model_output)}
                        ],
                    }
                ],
                "usage": {"input_tokens": 80, "output_tokens": 40, "total_tokens": 120},
            }
        )

    monkeypatch.setattr("app.llm.requests.post", fake_post)
    settings = Settings(
        llm_provider="openai",
        llm_base_url="https://api.openai.com/v1",
        llm_api_key="test-key-never-logged",
        llm_model="test-live-model",
    )
    provider = OpenAICompatibleProvider(settings)
    result = provider.triage(
        TicketInput(
            subject="Operations cannot use the daily delivery report",
            description="The data team released an update and the totals no longer match our process.",
        )
    )

    assert captured["url"] == "https://api.openai.com/v1/responses"
    assert captured["payload"]["store"] is False
    assert captured["payload"]["text"]["format"]["type"] == "json_schema"
    assert captured["payload"]["text"]["format"]["strict"] is True
    assert captured["headers"]["Authorization"] == "Bearer test-key-never-logged"
    assert result.assigned_team == "Data & Analytics Team"
    assert provider.usage["total_tokens"] == 120


def test_live_mode_never_silently_becomes_mock():
    with pytest.raises(LLMConfigurationError):
        get_provider(
            Settings(
                llm_provider="openai",
                llm_base_url="https://api.openai.com/v1",
                llm_api_key="",
                llm_model="test-live-model",
            )
        )


def test_ollama_provider_uses_local_endpoint_and_strict_schema(monkeypatch):
    captured = {}

    def fake_post(url, headers, json, timeout):
        captured.update(url=url, headers=headers, payload=json, timeout=timeout)
        return FakeResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": json_module.dumps(
                                {
                                    "summary": "A daily operations report is incomplete.",
                                    "missing_information": ["Which report date is affected?"],
                                    "category": "Data & Analytics",
                                    "priority": "High",
                                    "confidence": 0.9,
                                }
                            )
                        }
                    }
                ],
                "usage": {"prompt_tokens": 50, "completion_tokens": 25, "total_tokens": 75},
            }
        )

    monkeypatch.setattr("app.llm.requests.post", fake_post)
    settings = Settings(
        llm_provider="ollama",
        llm_base_url="http://localhost:11434/v1",
        llm_api_key="ollama",
        llm_model="qwen2.5:latest",
    )
    provider = get_provider(settings)
    result = provider.triage(
        TicketInput(
            subject="Missing orders in the morning report",
            description="Operations is blocked because today's report is incomplete.",
        )
    )

    assert captured["url"] == "http://localhost:11434/v1/chat/completions"
    assert captured["payload"]["response_format"]["type"] == "json_schema"
    assert captured["payload"]["response_format"]["json_schema"]["strict"] is True
    assert captured["headers"]["Authorization"] == "Bearer ollama"
    assert result.assigned_team == "Data & Analytics Team"
    assert provider.usage["total_tokens"] == 75


def test_ollama_mode_does_not_require_a_paid_api_key():
    provider = get_provider(
        Settings(
            llm_provider="ollama",
            llm_base_url="http://localhost:11434/v1",
            llm_api_key="",
            llm_model="qwen2.5:latest",
        )
    )
    assert isinstance(provider, OpenAICompatibleProvider)


def test_explicit_service_owner_overrides_model_impact_routing(monkeypatch):
    def fake_post(url, headers, json, timeout):
        return FakeResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": json_module.dumps(
                                {
                                    "summary": "Operations is blocked by a dashboard issue.",
                                    "missing_information": [],
                                    "category": "Operations & Fulfillment",
                                    "priority": "High",
                                    "confidence": 0.88,
                                }
                            )
                        }
                    }
                ]
            }
        )

    monkeypatch.setattr("app.llm.requests.post", fake_post)
    provider = OpenAICompatibleProvider(
        Settings(
            llm_provider="ollama",
            llm_base_url="http://localhost:11434/v1",
            llm_api_key="ollama",
            llm_model="qwen2.5:latest",
        )
    )
    result = provider.triage(
        TicketInput(
            subject="Orders missing from the daily dashboard",
            description="The Data team owns this dashboard, which currently blocks Operations.",
        )
    )

    assert result.category == "Data & Analytics"
    assert result.assigned_team == "Data & Analytics Team"


def test_reconciliation_discrepancy_uses_data_analytics_policy(monkeypatch):
    def fake_post(url, headers, json, timeout):
        return FakeResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": json_module.dumps(
                                {
                                    "summary": "Sales and Finance totals differ.",
                                    "missing_information": ["Which reporting date is affected?"],
                                    "category": "Business Applications",
                                    "priority": "Medium",
                                    "confidence": 0.7,
                                }
                            )
                        }
                    }
                ]
            }
        )

    monkeypatch.setattr("app.llm.requests.post", fake_post)
    provider = OpenAICompatibleProvider(
        Settings(
            llm_provider="ollama",
            llm_base_url="http://localhost:11434/v1",
            llm_api_key="ollama",
            llm_model="qwen2.5:0.5b-instruct",
        )
    )
    result = provider.triage(
        TicketInput(
            subject="Sales total does not match Finance total",
            description="Yesterday's sales total is lower. Which orders are included?",
        )
    )

    assert result.category == "Data & Analytics"
    assert result.assigned_team == "Data & Analytics Team"


def test_missing_information_does_not_repeat_ticket_description(monkeypatch):
    description = (
        "Completed orders from today are missing from the daily operations dashboard. "
        "The Paris warehouse cannot prepare the dispatch plan."
    )

    def fake_post(url, headers, json, timeout):
        return FakeResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": json_module.dumps(
                                {
                                    "summary": "Warehouse orders are missing from a dashboard.",
                                    "missing_information": [
                                        "Completed orders from today are missing from the daily operations dashboard.",
                                        "The Paris warehouse cannot prepare the dispatch plan.",
                                    ],
                                    "category": "Business Applications",
                                    "priority": "High",
                                    "confidence": 0.8,
                                }
                            )
                        }
                    }
                ]
            }
        )

    monkeypatch.setattr("app.llm.requests.post", fake_post)
    provider = OpenAICompatibleProvider(
        Settings(
            llm_provider="ollama",
            llm_base_url="http://localhost:11434/v1",
            llm_api_key="ollama",
            llm_model="qwen2.5:0.5b-instruct",
        )
    )
    result = provider.triage(
        TicketInput(subject="Missing warehouse orders", description=description)
    )

    assert result.category == "Data & Analytics"
    assert result.assigned_team == "Data & Analytics Team"
    assert result.missing_information
    assert all(question not in description for question in result.missing_information)
    assert all(question.endswith("?") for question in result.missing_information)


def test_ui_defence_filters_cached_repeated_context():
    ticket = TicketInput(
        subject="Data pipeline delay",
        description=(
            "The daily sales dataset has not been updated since 06:00. "
            "Marketing and Operations are using yesterday's figures.\n"
            "Operational context: business impact=Department; urgency=High; affected users=30."
        ),
    )
    repeated = [
        "The daily sales dataset has not been updated since 06:00. Marketing and Operations are using yesterday's figures.",
        "Operational context: business impact=Department; urgency=High; affected users=30.",
    ]

    questions = filter_missing_information(ticket, "Data & Analytics", repeated)

    assert questions
    assert all("operational context" not in question.lower() for question in questions)
    assert all("not been updated since 06:00" not in question.lower() for question in questions)
