# CHANGELOG

## v2.0.0 — Agentic assignment release

### Added
- SQLite-backed ticket, activity, knowledge metadata, and verified-resolution persistence
- Jira-style ticket creation with business-impact, urgency, affected-user and SLA inputs
- urgency-ranked smart feed using transparent 0–100 priority scoring
- reproducible fixtures with 27 synthetic tickets, 15 approved articles and 16 verified solutions
- ecommerce-company routing for IT, Security, Ecommerce Platform, Data Engineering, and BI & Analytics
- prominent similar-case solution and approved diagnostic guidance immediately after ticket submission
- light sky-blue high-contrast interface replacing the previous dark-on-dark theme
- dual-source RAG over approved articles and human-verified resolved cases
- human-controlled resolution publishing into reusable case memory
- five role-separated agents with typed decisions and visible handoffs
- bounded workflow orchestrator with stop, escalate, await-information, and human-review states
- field-level PII minimization before optional cloud inference
- thresholded and source-deduplicated retrieval
- deterministic risk/quality and citation-provenance validation
- explicit human approve/escalate checkpoint and privacy-safe decision logging
- investor-oriented AegisDesk UI with KPI targets, agent trace, evidence, and controls
- twelve-test workflow, data, retrieval, privacy, safety, escalation, audit, and UI suite
- assignment-compliant one-slide PPTX and five-page DOCX/PDF architecture deliverables
- reproducible deliverable generation and verification scripts

### Changed
- provider contract now separates Triage and Resolution model roles
- documentation now maps directly to the assignment's six required layers
- all business figures are labelled as pilot targets rather than measured results
- optional investor deck and demo script now match the implemented multi-agent workflow

### Fixed
- cloud-bound subject and requester could previously bypass redaction
- refusal output previously used category/priority values outside the approved UI taxonomy
- duplicate KB source titles and weak positive retrieval matches could be presented as grounding
- non-functional draft action replaced with an auditable human approval control

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
