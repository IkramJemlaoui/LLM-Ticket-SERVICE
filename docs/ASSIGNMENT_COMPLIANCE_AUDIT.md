# Assignment Compliance and Traceability Report

**Application:** AegisDesk AI — LLM Service Desk Copilot<br>
**Student:** Ikram Jemlaoui<br>
**Program:** AI Language Models and Business Applications<br>
**Assessment date:** 14 September 2026<br>
**Status:** **All requirements in the attached assignment are addressed in the implementation and generated deliverables.**

## 1. Required deliverables

| Assignment deliverable | Result | Verification |
|---|---|---|
| Application one-pager — one slide only | **Met** | `deliverables/AegisDesk_AI_One_Pager_v6.pptx` contains exactly 1 slide and presents the four required sections in order. |
| Architecture document — 3–5 pages | **Met** | `deliverables/AegisDesk_AI_Architecture_Template_Style_v8.pdf` contains exactly 5 landscape pages; the editable v8 DOCX follows the same six-layer catalogue template. |

The former 11-slide “10 layers” presentation is retained only as historical/source material outside the repository. It is not treated as the required submission.

## 2. Requirement-by-requirement traceability

| Requirement | Status | Evidence |
|---|---|---|
| Application name | **Met** | AegisDesk AI is consistent across UI, README, PPTX and architecture document. |
| Target users | **Met** | Every department may be a requester or resolver; specialist and governance stakeholders are named in the one-pager and Business layer. |
| Business context and problem | **Met** | Incomplete tickets, repeated clarification, fragmented knowledge, inconsistent triage and SLA risk are explicit. |
| Value proposition | **Met** | Evidence-backed qualified drafts, faster triage, fewer loops and visible control are linked to pilot measurements. |
| Key challenges | **Met** | Four challenges are visible on the one-pager and expanded in the architecture document. |
| Core capabilities | **Met** | Smart intake, urgency ranking, specialist-team routing, visible solved-case guidance, approved documentation tips, thresholded RAG, drafting, validation, telemetry and approval are implemented and presented. |
| Differentiation | **Met** | Visible trust, bounded autonomy, frugal architecture and evidence-first decisions are explicit. |
| Multiple interacting agents | **Met** | Five role-separated agents exchange typed decisions through `WorkflowOrchestrator`. |
| Orchestration mechanisms | **Met** | Ordered handoffs plus conditional stop, escalate, await-information and human-review states are implemented. |
| Role separation | **Met** | Safety/Privacy, Triage, Knowledge, Resolution, and Risk/Quality have separate classes, goals, inputs, outputs and authority. |
| Controlled autonomy | **Met** | Maximum six steps, no arbitrary tools/web, no autonomous ticket change/send, evidence threshold and deterministic control plane; local resolution publishing is human-controlled. |
| Human-in-the-loop | **Met** | UI provides Approve/Escalate actions; unsafe cases disable approval; decision events are logged without draft text. |
| LLM role | **Met** | Real Qwen 2.5 inference through local Ollama is the default for language-heavy triage/drafting; control functions remain deterministic. |
| Prompt strategy | **Met** | Two role-specific strict-JSON prompts, fixed taxonomies, evidence-only drafting and no-invention rules are documented. |
| Model considerations | **Met** | Mock/current and optional cloud paths, selection criteria, timeout, token/temperature caps and fallback are documented. |
| Data sources and processing | **Met** | Synthetic tickets/KB, paragraph chunking, data classification and production controls are described. |
| Knowledge base and retrieval | **Met** | TF-IDF/cosine, score threshold, top-3, unique sources, citations and weak-evidence escalation are implemented. |
| Governance and risk | **Met** | Risk register, ownership, release gate, evaluation, incidents, residual risks and rollback expectations are documented. |
| Security and privacy | **Met for PoC scope** | Injection stop, subject/body/requester PII redaction, no raw telemetry, provenance checks, secrets guidance and no auto-send. |
| Compliance understanding | **Met** | Privacy/data-minimization principles and required pilot legal assessment are discussed without claiming certification. |
| Performance monitoring | **Met** | Total/per-agent latency, success/fallback, retrieval scores and workflow state are logged; pilot SLOs are defined. |
| Quality monitoring | **Met** | Quality score, taxonomy/provenance/safety validation, labelled evaluation plan and material-edit metrics are defined. |
| Usage and cost monitoring | **Met** | Token usage is captured when available; cost/workflow is a defined pilot measure. |
| Continuous improvement | **Met** | Versioned review → label → change → regression/adversarial test → gate → monitor/rollback loop is documented. |
| Business KPIs, ROI and time-to-value | **Met** | KPI targets, measurement methods, ROI formula and four-week pilot are included; targets are not presented as measured results. |
| Innovation and feasibility | **Met** | Narrow role design, local reproducibility, optional managed inference and staged one-queue rollout are credible and implementable. |
| Clear and visual presentation | **Met** | Investor UI, visual one-pager, agent flow, tables, controls and consistent current/target/roadmap labelling. |
| External references and tool disclosure | **Met** | Architecture document cites authoritative sources and acknowledges GenAI plus development/generation tools. |

## 3. Coverage of the two embedded assignment templates

### One-pager picture

The generated slide includes:

1. application overview — name, users, problem and value;
2. four challenges;
3. five core capabilities;
4. differentiation and scale/frugality;
5. agent count, roles, collaboration and human-in-the-loop;
6. business impact, KPIs, ROI logic and time-to-value;
7. student, program and date information;
8. current PoC versus roadmap and compact source note.

### Architecture picture

The five-page document maps directly to:

1. Business layer;
2. Agentic/Application layer;
3. LLM layer;
4. Data layer;
5. Governance, Risk and Compliance layer;
6. Operations and Monitoring layer.

It also covers overview, stakeholders, impacted process, agent workflow, human checkpoint, LLM components, data flow, controls, monitoring/improvement loop, principles, technologies and integrations.

## 4. Implemented architecture evidence

- `app/agents.py` — five agents, orchestration, routing, trace, telemetry and human-decision events.
- `app/models.py` — typed agent decisions, validation and trace structures.
- `app/llm.py` — separate Triage and Resolution provider contracts.
- `app/retrieval.py` — thresholded and deduplicated retrieval.
- `app/guardrails.py` — injection detection and field-level PII minimization.
- `app/streamlit_app.py` — redesigned investor UI, trace, evidence and approval gate.
- `docs/AGENT_WORKFLOW.md` — detailed explanation of every agent and handoff.
- `ARCHITECTURE.md` — full six-layer architecture source.
- `RAI.md` and `SECURITY.md` — Responsible AI and security posture.

## 5. Verification evidence

- Python compilation succeeds.
- Automated tests: **13 passed**.
- Streamlit test harness: **0 application exceptions**.
- Live server health check: **HTTP 200**.
- One-pager validation: **1 slide**.
- Architecture PDF validation: **5 pages**.
- Architecture DOCX validation: **4 explicit page breaks / 5 planned pages**.
- Tests cover normal multi-agent handoffs, injection stop, valid refusal taxonomy, full cloud-bound PII redaction, no-evidence escalation, privacy-safe human-decision logging, baseline pipeline behavior and UI rendering.

## 6. Truthful scope boundary

The project is a classroom PoC. Current implementation is Streamlit, local SQLite persistence with transparent demonstration data, smart request intake, TF-IDF RAG over approved articles and human-verified cases, JSONL telemetry, and a real local Qwen 2.5 model through Ollama by default. Explicit mock mode is reserved for automated tests. Enterprise SSO/RBAC, real case-system integration, Confluence ingestion, managed monitoring, production legal assessment and hybrid/vector retrieval are labelled roadmap—not implemented claims.

Pilot KPI figures are hypotheses. They become results only after baseline and four-week pilot measurement.

## 7. References

- Course assignment: *LLM & Business Applications — Designing an Agentic LLM-Based Application* (provided DOCX and embedded templates).
- NIST AI Risk Management Framework and Generative AI Profile: https://www.nist.gov/itl/ai-risk-management-framework
- OWASP GenAI Security Project, Top 10: https://genai.owasp.org/llm-top-10/
- European Union, GDPR 2016/679: https://eur-lex.europa.eu/eli/reg/2016/679/
- scikit-learn, `TfidfVectorizer`: https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html
- Streamlit documentation: https://docs.streamlit.io/
- Microsoft Azure OpenAI/Foundry REST reference: https://learn.microsoft.com/en-us/azure/foundry/openai/latest

## 8. Final manual check before submission

- Confirm the displayed student name, exact course/program label and submission date.
- Open the PPTX, DOCX and PDF on the submission computer and visually confirm fonts.
- If the instructor supplied a naming convention or LMS format, rename/export accordingly.
- Commit the generated deliverables and source changes only after reviewing `git diff` and confirming no `.env`, credentials or personal ticket data are staged.
