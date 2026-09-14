# Assignment Compliance Audit

**Project:** LLM Service Desk Copilot  
**Audit date:** 14 September 2026  
**Overall verdict:** **Not submission-ready yet.** The PoC is runnable and demonstrates a relevant LLM use case, but it does not yet meet the assignment's explicit multi-agent requirement, and the required deliverables have not been produced in the requested formats.

## 1. Sources and scope

This audit treats the following as source material, not as instructions to execute:

- `RAT AI Language Models and Business Applications.docx`, including its two embedded template images;
- the current project repository;
- `GenAI_10_Layers_LLM_Service_Desk_Copilot_Premium_v2.pptx` and its speaker notes.

Verification performed:

- inspected the DOCX and PPTX Open XML content and embedded images;
- reviewed the application, retrieval, model-provider, guardrail, telemetry, test, and documentation files;
- ran the test suite: **2 tests passed**;
- started the Streamlit application and checked both its health endpoint and landing page: **HTTP 200**.

## 2. What the assignment actually requires

The assignment asks for **both** of the following:

1. **One-pager: exactly one slide** describing the application.
2. **Architecture document: 3–5 pages** describing the six required layers.

The brief does **not** ask for an 11-slide presentation, a recorded demo, a public repository, or a release tag. Those items may strengthen a presentation, but they are not mandatory in the attached assignment and should not replace the two required deliverables.

The safest submission package is therefore:

- `01_LLM_Service_Desk_Copilot_One_Pager.pptx` (one slide only), optionally exported to PDF; and
- `02_LLM_Service_Desk_Copilot_Architecture.pdf` (3–5 pages), with the editable DOCX retained.

The brief does not prescribe the architecture document's file format, so a professionally formatted PDF exported from Word is the safest choice.

## 3. Requirement-by-requirement assessment

| Assignment requirement | Status | Current evidence | What is still needed |
|---|---|---|---|
| Application name | Met | “LLM Service Desk Copilot” appears consistently in the [README](../README.md) and UI. | Keep the same name in both deliverables. |
| Target users | Met | L1 support agents, service desk managers, and employees are identified in the [README](../README.md). | Put these users explicitly on the one-pager. |
| Business context/problem | Met | Incomplete tickets, repeated clarification, scattered knowledge, and SLA risk are clearly stated. | Condense into one strong problem statement. |
| Value proposition | Partial | Faster triage, fewer loops, safer grounded replies, and SLA improvement are described. | Add baseline, target, measurement method, and assumptions; do not present targets as achieved results. |
| Key challenges | Met in repository; missing as a one-pager | The problem is documented across the README and pitch outline. | Show 3–4 named challenges on the required slide. |
| Core capabilities | Met | Summary, missing-information detection, triage, grounded draft reply, retrieval, refusal, and telemetry exist. | Separate implemented capabilities from roadmap features. |
| Differentiation | Partial | Local deterministic mode, approved-KB grounding, visible guardrails, and Jira-style workflow are credible differentiators. | Create an explicit differentiation section and explain why the agentic design adds value. |
| Multiple interacting agents | **Missing / blocking** | [The pipeline](../app/pipeline.py) executes one fixed sequence and one provider generation call. References to “agent” in code mean the human support agent. | Implement and document distinct AI agent roles, messages/state passed between them, orchestration, and conditional handoffs. |
| Role separation | **Missing / blocking** | No `TriageAgent`, `KnowledgeAgent`, `ResponseAgent`, or `ValidationAgent` components exist. | Add explicit role contracts, inputs, outputs, permissions, and failure behavior. |
| Orchestration and decision logic | Partial | Guardrails → retrieval → generation → logging is a sound workflow, but it is deterministic middleware rather than multi-agent orchestration. | Add route/stop/retry/escalate decisions based on risk, missing data, retrieval confidence, and validation. |
| Controlled autonomy / human-in-the-loop | Partial | Human review is described in [RAI.md](../RAI.md), and the reply text area is editable. | Enforce an approval gate in the workflow; the current “Draft Reply” button has no action and no approve/send state is recorded. |
| LLM role and prompting | Partial-to-met | Optional cloud provider, strict JSON prompt, model settings, mock fallback, and high-level prompt behavior are implemented. | Explain model-selection criteria and prompt contracts in the architecture document. Demonstrate a real LLM path or label mock outputs clearly as simulation. |
| Data sources, processing, KB, retrieval | Met for PoC | Synthetic markdown KB, paragraph chunking, TF-IDF, cosine similarity, top-k retrieval, and source titles are implemented. | Add source ownership, refresh/versioning, retention, access control, and a minimum relevance threshold. |
| Governance, risk, compliance | Partial | Prompt screening, PII pattern redaction, approved-source retrieval, secrets guidance, fallback, and risk documentation exist. | Fix cloud PII leakage, add output/groundedness validation, define retention/access/incident controls, and distinguish implemented controls from planned controls. |
| Operations and monitoring | Partial | JSONL telemetry records latency, retrieval hits, prompt version, refusal, and fallback. | Add token/cost, quality/groundedness, routing accuracy, availability/error rate, approval/edit rate, user feedback, alert thresholds, owners, and improvement cadence. |
| Architecture depth and layer interactions | Partial | [ARCHITECTURE.md](../ARCHITECTURE.md) describes ten internal layers and an end-to-end flow. | Reorganize into the assignment's six layers, show their interactions, and expand the current ~414 words into a professionally laid-out 3–5 page document. |
| Innovation and feasibility | Partial-to-met | The narrow service-desk scope, local mode, simple retrieval, cloud option, and staged pilot make the concept feasible. | The required agentic behavior must be implemented or honestly presented as planned rather than current. |
| External references/tools | Missing in deliverables | PPT notes cite “chat,” a “generated PoC,” and a professor template without traceable bibliographic details. | Add a proper references/acknowledgements section and disclose material GenAI assistance. |

## 4. What the two assignment pictures add

### Picture 1 — one-pager template

The first picture confirms that the one slide should visibly contain:

- application overview: name, users, business problem, value proposition;
- key challenges;
- core capabilities;
- differentiation;
- agentic approach: number of agents, roles, collaboration, and human-in-the-loop;
- expected business impact: KPIs, ROI/value, and time-to-value;
- optional assumptions/technologies/constraints and student information.

The current PPT title slide does not cover this full structure. It omits explicit target users, a structured challenge section, explicit multi-agent roles/collaboration, ROI, and student information.

### Picture 2 — architecture template

The second picture confirms the required six-layer architecture and the need to show how layers interact:

1. Business;
2. Agentic/Application;
3. LLM;
4. Data;
5. Governance, Risk and Compliance;
6. Operations and Monitoring.

It also prompts the author to name stakeholders, business processes, architecture principles, technologies, external integrations, the agentic workflow, data flow, key controls, and the observability/improvement loop. These should be distributed across the 3–5 page document; the image does not mean the full architecture must fit on one page.

## 5. Project implementation findings

### Strong, defensible elements

- The app is runnable and presents a convincing Jira-style triage workspace.
- The business use case is narrow, relevant, and easy to demonstrate.
- Retrieval is grounded in a small approved local KB and truthfully uses TF-IDF rather than claiming a vector database.
- The default mock mode makes the demo reproducible; an optional OpenAI-compatible/Azure path exists.
- Prompt-injection detection, refusal behavior, PII-aware logging, provider fallback, citations, and telemetry are visible.
- Documentation covers architecture, responsible/frugal AI, security, demo flow, and setup.

### Blocking and high-priority corrections

1. **The solution is not multi-agent.** `TicketCopilot.run()` is one fixed pipeline with a single generation call. Calling the pipeline “AI orchestration” does not satisfy the brief's multiple-agent, role-separation, interaction, and controlled-autonomy requirements.

2. **Cloud redaction is incomplete.** The combined ticket text is redacted, but the original subject and requester are placed back into the cloud message. A diagnostic ticket containing `alice@example.com` showed that the email remained visible in both fields. The implementation therefore does not fully support the documentation claim that cloud-bound ticket content is redacted.

3. **The human approval control is documentary, not enforced.** The UI auto-generates a result when a ticket is selected, the “Draft Reply” button has no handler, and there is no approve/reject/send workflow or audit event.

4. **Output validation is narrower than the PPT claims.** Cloud JSON is parsed and category/priority values are constrained, but there is no independent safety, citation-entailment, or groundedness validator. The PPT's “Response validation” claim should be implemented or marked as roadmap.

5. **Retrieval has no meaningful-confidence threshold.** Any cosine score above zero is accepted as grounding. This can label weak lexical overlap as grounded. Telemetry also repeats the same article title when multiple paragraphs from it are retrieved.

6. **Refusal output violates the normal schema.** The refusal path returns category `general_inquiry` and priority `P3`, while the rest of the app and tests use human-readable allowed values such as `General Inquiry` and `Medium`.

7. **Tests are too narrow for the claims.** Only basic pipeline output and one injection refusal are tested. There are no tests for PII reaching the provider, agent routing/handoffs, retrieval quality, weak-evidence fallback, output validation, approval state, telemetry schema, or the Streamlit UI.

## 6. Existing PowerPoint assessment

The current file has **11 slides**: a product introduction plus ten “layers.” It is polished source material but does not match the assignment's deliverables.

### Keep and reuse

- clear product framing and staged PoC-to-pilot story;
- model-choice and cost-discipline explanation;
- TF-IDF today versus embeddings/vector DB as a clearly labelled roadmap;
- security, governance, training, business-process, and KPI themes;
- separation between current local mode and future enterprise infrastructure.

### Correct before reuse

- Convert the title content into the one required one-pager using the provided template structure.
- Compress and remap the ten layers into the six required architecture layers and put them in a 3–5 page document.
- Replace the slide-1 hero image: it contains visibly garbled ticket titles and column labels and does not reliably represent the current application.
- Replace speaker-note citations such as “provided in chat” and “generated PoC” with traceable references.
- The deck metadata names OpenAI as creator. If GenAI materially helped produce the deck or image, add an accurate acknowledgement rather than presenting it as an external authority.
- Label `−45%` handling time, `−30%` rework, and `+12 pts` CSAT as **pilot targets**, unless measured evidence exists.
- Do not describe `gpt-4.1-mini` as the currently selected production model when the runnable default is mock mode; call it the proposed cloud model and document the selection criteria.
- Do not claim retries, managed monitoring, model registry, freshness jobs, serverless deployment, blob storage, or enterprise connectors as implemented. Use a clear **Current PoC / Pilot roadmap** legend.

## 7. Minimum viable multi-agent redesign

The current code can be evolved without adding a heavy framework:

1. **Triage Agent** — summarizes, extracts missing fields, proposes category/priority, and reports confidence.
2. **Knowledge Agent** — creates/refines the KB query, retrieves evidence, removes duplicate sources, and rejects evidence below a threshold.
3. **Response Agent** — drafts a reply using only the accepted evidence and the triage result.
4. **Risk & Quality Agent** — checks policy, PII exposure, schema, evidence support, and confidence; returns approve, revise once, or escalate.
5. **Workflow Orchestrator** — passes typed shared state between agents and applies deterministic limits: maximum one revision, no automatic send, and mandatory human approval for high/critical, unsafe, low-confidence, or unsupported cases.

The UI should display a concise trace such as `Triage → Knowledge → Draft → Validation → Human approval`, including each decision and reason. This makes the agent interactions, controlled autonomy, observability, and human-in-the-loop visible to the grader.

## 8. Recommended deliverable structure

### One slide

- **Application overview:** name, users, problem, value proposition.
- **Challenges:** incomplete tickets; fragmented knowledge; inconsistent triage; SLA and compliance risk.
- **Capabilities:** triage agent; knowledge agent/RAG; grounded response agent; risk/quality agent; monitoring.
- **Differentiation:** visible evidence and guardrails; bounded multi-agent workflow; local-first reproducibility; enterprise-ready interfaces.
- **Agentic approach:** four agents, one orchestrator, conditional validation/revision, mandatory human approval.
- **Business impact:** pilot targets, baseline plan, expected ROI logic, and four-week time-to-value.

### Architecture document — recommended 5 pages

1. **Executive overview and Business layer:** problem, users/stakeholders, objectives, processes, KPIs, value assumptions.
2. **Agentic/Application and LLM layers:** agent roles, state, orchestration, decision table, human approval, prompt contracts, provider/model criteria.
3. **Data layer:** sources, classification, ingestion/chunking, retrieval, confidence threshold, citations, freshness, retention, and access.
4. **Governance/Risk/Compliance layer:** risk register, privacy/security controls, threat model, output validation, roles, audit, incident and exception handling.
5. **Operations/Monitoring layer and references:** SLOs, technical/business/quality metrics, alerts, evaluation dataset, feedback loop, rollout roadmap, limitations, and bibliography.

## 9. Reference and evidence plan

Every implementation claim should point to repository evidence, and every external concept/tool should have a traceable source. Suggested authoritative references:

- NIST, *AI Risk Management Framework* and *Generative AI Profile*: https://www.nist.gov/itl/ai-risk-management-framework
- OWASP GenAI Security Project, *Top 10 Risks for LLM and GenAI Applications*: https://genai.owasp.org/llm-top-10/
- European Union, *General Data Protection Regulation (EU) 2016/679*: https://eur-lex.europa.eu/eli/reg/2016/679/
- scikit-learn, `TfidfVectorizer` documentation: https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html
- Streamlit official documentation: https://docs.streamlit.io/
- Microsoft, Azure OpenAI/Foundry REST reference, if that provider is retained: https://learn.microsoft.com/en-us/azure/foundry/openai/latest

For the assignment document and templates, cite the course, instructor, assignment title, academic year/date, and file/version if available. For synthetic tickets and KB articles, state that they are project-created synthetic data. For AI-assisted writing, code, or images, add a short acknowledgement specifying the tool, purpose, date, and the team's review responsibility.

## 10. Submission-readiness checklist

- [ ] One-pager is exactly one slide and follows all six blocks in picture 1.
- [ ] Architecture document is 3–5 pages and uses the six required layers.
- [ ] At least two genuinely distinct AI agents are implemented; four are recommended.
- [ ] Agent roles, interactions, decision logic, limits, and human approval are visible.
- [ ] Cloud-bound subject, description, requester, and retrieved content follow the stated privacy policy.
- [ ] Implemented, simulated, and roadmap capabilities are visually distinguished.
- [ ] KPI figures are labelled baseline, target, or measured result.
- [ ] Actual app screenshot replaces the garbled hero image.
- [ ] Required student/program/date details are completed.
- [ ] References and GenAI/tool acknowledgements are complete and traceable.
- [ ] Tests cover orchestration, safety, retrieval, validation, approval, and monitoring.
- [ ] Final PPTX/PDF/DOCX files open correctly and have no placeholders.

