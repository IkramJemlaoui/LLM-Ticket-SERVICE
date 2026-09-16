
<img width="1672" height="941" alt="cc410966-5fac-4f23-a8f9-e210a0c36f0a" src="https://github.com/user-attachments/assets/e5eecfa6-8059-450e-b0ca-4c2f74f2825e" />

# AegisDesk AI — Company-Wide Request Intelligence

AegisDesk AI is a cross-department request platform for an ecommerce company. Any department can request support, clarification, correction, or new work from another department. Five specialist agents turn plain-language requests into complete, prioritised and correctly routed cases, retrieve approved company knowledge and verified resolutions, and prepare evidence-backed recommendations while humans retain control of consequential actions.

## Business problem

Internal requests frequently arrive without the context the responsible team needs. Employees and specialists repeatedly clarify requirements, search scattered knowledge and redirect work sent to the wrong department. The result is slow service, duplicated effort and avoidable SLA risk.

## Value proposition

AegisDesk compresses the work between ticket arrival and a qualified first draft:

- faster understanding through structured summaries;
- fewer clarification loops through missing-information detection;
- more consistent category, priority, and specialist-team recommendations;
- evidence-backed drafts from approved internal knowledge and similar human-verified resolutions;
- an immediate “solved before” recommendation and diagnostic explanation when relevant evidence exists;
- visible safety, quality, and human-approval controls.
- a persistent Jira-style intake and urgency-ranked queue.

The four-week pilot target is a **40% reduction in time to first qualified draft**. This is a target, not a measured production result. Baseline and post-pilot measurements are required before an ROI claim is made.

## Agentic design

The application implements five interacting agents coordinated by a bounded workflow:

1. **Safety & Privacy Agent** — detects prompt attacks, minimizes personal data, and can stop the workflow.
2. **Triage Agent** — summarizes the case, identifies missing information, and recommends category, priority, issue type, and the responsible team.
3. **Knowledge Agent** — builds a context-aware query, retrieves approved KB evidence, removes duplicate sources, and rejects weak matches.
4. **Resolution Agent** — drafts a response from the triage result and accepted evidence only.
5. **Risk & Quality Agent** — validates taxonomy, safety, evidence provenance, quality, and release conditions.

The orchestrator applies conditional routing: **stop**, **escalate**, **await information**, or **release to human review**. It allows no more than six steps, exposes the full trace in the UI, and never sends a customer response autonomously.

See [Agent Workflow](docs/AGENT_WORKFLOW.md) for inputs, outputs, handoffs, decision rules, and failure behavior.

## Current PoC versus roadmap

| Capability | Current PoC | Pilot roadmap |
|---|---|---|
| User experience | Streamlit, Jira-style ticket creation and service workspace | Jira/service-management API |
| Agent orchestration | Five bounded roles, typed state, conditional stop/escalation | Durable workflow service and queue |
| Inference | Real Qwen 2.5 model running locally through Ollama; OpenAI/Azure remain optional; explicit mock only for tests | Evaluated local or managed model release process |
| Retrieval | TF-IDF RAG over approved articles + human-verified resolved cases, thresholded top-3 | Evaluated hybrid/vector retrieval if justified |
| Data | Local SQLite; 27 seeded tickets, 20 articles, 16 verified solutions, and 15 governed routing evaluations | Managed relational store, retention and access policies |
| Human control | Approve, escalate, or publish a verified resolution; no automatic send | RBAC-backed release workflow |
| Observability | Redacted JSONL workflow, agent latency, quality and retrieval metrics | Managed dashboards, alerts, SLOs and cost reporting |
| Identity/integration | Local demonstration only | Enterprise SSO, RBAC and ticketing integration |

## Core capabilities

- structured ticket summary;
- missing-information questions;
- category and impact recommendation;
- deterministic routing across IT, Data, Operations, Finance, HR, Security, Ecommerce, and other approved specialist teams;
- prominent similar-case solution and approved diagnostic tips immediately after submission;
- persistent ticket creation and deterministic urgency/impact scoring;
- approved-knowledge and verified-case retrieval with confidence threshold;
- grounded, editable reply draft with citations;
- prompt-injection stop path;
- PII redaction before model inference and telemetry;
- visible provider failure with no silent simulated answer in live mode;
- independent risk and quality validation;
- explicit human approve/escalate checkpoint;
- human-controlled resolution publishing for safe case reuse;
- explicit useful/not-relevant retrieval feedback for a future reviewed evaluation or fine-tuning dataset;
- per-agent decision and latency trace.

## Two user views

- **Employee Help Portal:** analyses the request before submission, shows similar solved cases, safe guidance, approved documentation, missing facts, classification and recommended team, then lets the employee solve through self-service or create a routed ticket.
- **Support Workspace:** provides the queue/SLA, assigned and recommended teams, case evidence, RAG confidence, safety controls, editable final response, and approve/reject/reassign/escalate/resolve actions.

See [User Views](docs/USER_VIEWS.md) for the complete interaction and control boundaries.

## Target users and stakeholders

- Requesters: employees and teams in every department; a resolver team in one workflow may be the requester in another.
- Resolvers: IT, Data, Operations, Finance, HR, Security, Ecommerce, and other specialist departments.
- Control stakeholders: security, privacy/legal, knowledge owners, platform operations, service owners, and the executive sponsor.

## Quick start

### Requirements

- Python 3.11+
- [Ollama](https://docs.ollama.com/quickstart) running locally
- the local `qwen2.5:0.5b-instruct` model (`ollama pull qwen2.5:0.5b-instruct` if it is not already installed)

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
powershell -ExecutionPolicy Bypass -File .\scripts\run_demo_ollama.ps1
```

### Linux or macOS

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./scripts/run_demo.sh
```

Open `http://localhost:8501`. Select ticket `SD-1036` to demonstrate the stopped prompt-injection workflow.

The launcher deliberately uses `.venv\Scripts\python.exe`, even if a different global Streamlit installation is present. It starts at port 8501 and automatically selects the next bindable port when necessary; use the `Local URL` printed in the terminal. To request a particular starting port, set `AEGISDESK_PORT` before launching.

Do not run `pip install sklearn`: that PyPI alias is deprecated. The import name is `sklearn`, but the package installed by `requirements.txt` is `scikit-learn`.

## Configuration

The project is configured for free local inference by default. Ollama requires no API key and no per-request payment. The one-command PowerShell launcher checks that Ollama and the selected model are available before starting the app. Never commit `.env`.

Important controls:

- `LLM_PROVIDER=ollama` activates the real local model at `http://localhost:11434/v1`;
- `OLLAMA_MODEL=qwen2.5:0.5b-instruct` selects the responsive local demo model;
- `LLM_TIMEOUT_SECONDS=60` bounds local generation so the interface does not wait indefinitely;
- use `qwen2.5:latest` with a larger timeout only as an optional higher-quality, slower profile;
- `LLM_PROVIDER=openai` remains an optional paid cloud path;
- `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and `OPENAI_MODEL` configure live inference;
- `LLM_PROVIDER=mock` is an explicit automated-test mode, never a silent live fallback;
- `ALLOW_MOCK_FALLBACK=false` keeps provider failures visible;
- `REDACT_BEFORE_CLOUD=true` minimizes PII in all provider-bound ticket fields;
- `RETRIEVAL_TOP_K=3` limits evidence fan-out;
- `RETRIEVAL_MIN_SCORE=0.08` rejects weak matches;
- `MAX_AGENT_STEPS=6` bounds workflow autonomy;
- `REQUIRE_HUMAN_APPROVAL=true` prevents autonomous customer release.

## Verification

```powershell
python -m pytest -q
```

The tests cover normal orchestration, safety stop, provider-bound PII redaction, evidence-free escalation, human-decision logging, taxonomy consistency, SQLite persistence, priority ordering, dual-source RAG, local Ollama structured output, and UI rendering.

## Architecture and assignment deliverables

- [Six-layer architecture](ARCHITECTURE.md)
- [Agent workflow](docs/AGENT_WORKFLOW.md)
- [Data, RAG, and case memory](docs/DATA_AND_RAG.md)
- [Responsible and frugal AI](RAI.md)
- [Security posture](SECURITY.md)
- [Assignment compliance audit](docs/ASSIGNMENT_COMPLIANCE_AUDIT.md)
- Generated submission files are written to `deliverables/` by `scripts/generate_deliverables.py`.

## Repository structure

```text
app/                    UI, agents, orchestrator, provider, SQLite store, retrieval, controls, telemetry
data/synthetic_tickets.json  Transparent, reproducible ticket and verified-resolution fixtures
data/knowledge_base/    Synthetic approved knowledge used for the PoC
data/aegisdesk.db       Generated local runtime database (gitignored and recreated on first run)
deliverables/           One-slide overview and 3–5 page architecture document
docs/                   Agent workflow, audit, demo and presentation material
scripts/                Demo and deliverable generation commands
tests/                  Workflow, safety, privacy and UI tests
```

## Data and tool disclosure

The repository includes transparent local demonstration tickets, resolutions, and knowledge articles. User-created requests are stored locally in `data/aegisdesk.db`. The UI uses Streamlit; lexical RAG uses scikit-learn TF-IDF. Retrieval does **not** train or fine-tune the LLM: it supplies relevant approved passages and human-verified resolutions as context for each workflow. Live inference runs the configured Qwen 2.5 model locally through Ollama; automated tests explicitly select deterministic mock mode. OpenAI and Azure remain optional deployment paths. Any GenAI assistance used to develop code, writing, or visuals must be reviewed by the team and acknowledged in the final submission.

## Limitations

This is a classroom PoC, not a production Jira integration. SQLite is suitable for a local single-user demonstration, not a concurrent enterprise deployment. The app does not include enterprise identity, outbound messaging, production monitoring, or measured ROI. Those capabilities are explicitly roadmap items.
