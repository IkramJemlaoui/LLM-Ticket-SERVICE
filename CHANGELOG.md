# CHANGELOG

## v1.0.0

Initial investor-ready demo release.

### Added
- Jira-style three-pane Streamlit workspace
- queue filters, ticket list, ticket detail view, and AI Copilot panel
- demo ticket fixtures including a visible guardrail example
- grounded retrieval over approved KB articles
- prompt-injection and PII guardrails
- Windows launcher script `scripts/run_demo.ps1`
- smoke tests for normal flow and refusal flow

### Notes
- Default provider remains `mock` for reproducibility
- UI is a service-desk-style simulation, not a real Jira integration
