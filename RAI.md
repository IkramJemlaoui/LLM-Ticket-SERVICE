# Responsible and Frugal AI

## Principle

AegisDesk uses generative AI only for language-heavy triage and drafting. Safety, privacy minimization, retrieval, provenance validation, workflow routing, and human release are deterministic controls. This separation limits cost and prevents a model from approving its own high-impact actions.

## Human accountability

- AI outputs are recommendations, not final ticket decisions.
- Every outbound draft requires a visible human approve/escalate action.
- Injection, invalid output, weak evidence, and high-impact cases receive explicit review reasons.
- The PoC cannot send messages or mutate an external ticket.

## Data protection

- email and phone-like values are redacted independently in subject, description, and requester before optional cloud inference;
- raw tickets and drafts are excluded from telemetry;
- the knowledge scope is approved local content only;
- no open-web retrieval or arbitrary model-selected tool is available;
- a pilot requires documented purpose, lawful basis, retention, residency, access, deletion, and incident procedures.

## Model and resource efficiency

- deterministic mock mode supports reproducible evaluation without network calls;
- cloud mode uses two narrow role-specific calls rather than an unconstrained conversation;
- temperature is capped at 0.4 and output at 800 tokens;
- top-k evidence is limited to 3 and weak passages are rejected;
- workflow trace is capped at 6 steps;
- provider failure falls back safely instead of repeated uncontrolled calls;
- embeddings/vector infrastructure is deferred until evaluation demonstrates material value.

## Risk register

| Risk | Current mitigation | Pilot evidence needed |
|---|---|---|
| hallucination / unsupported advice | approved evidence, threshold, citations, quality agent, specialist escalation | groundedness and citation precision |
| wrong category or priority | fixed taxonomy, confidence, human review | labelled accuracy by ticket type |
| prompt injection | pre-agent detection and workflow stop | adversarial false-positive/negative rate |
| sensitive data disclosure | field-level redaction and metadata-only logs | privacy tests and sampled DLP review |
| automation bias | visible trace/evidence and mandatory approval | material-edit and override rate |
| model drift/provider change | prompt/model versions and regression tests | release comparison dashboard |
| cost or latency growth | step limit, token caps, token/latency telemetry | cost per workflow and p95 latency |
| knowledge staleness | synthetic approved KB for PoC | owners, versions, freshness SLA |

## Fairness and accessibility

Ticket priority must be based on operational impact, not requester seniority or sensitive characteristics. Pilot evaluation should compare error and escalation rates across channels, languages, locations, and accessibility needs where legally and ethically appropriate. The interface should be tested for keyboard navigation, contrast, screen-reader labels, and plain-language comprehension.

## Evaluation plan

Create a de-identified, expert-labelled set covering supported categories, missing-information patterns, ambiguous cases, weak/no evidence, multilingual tickets, prompt attacks, and PII. Measure triage accuracy, question usefulness, retrieval precision/coverage, groundedness, safety recall/precision, material edit rate, latency, and cost. Define acceptance thresholds before model or prompt changes are released.

## Transparency

The UI shows provider mode, evidence sources, confidence, quality status, agent decisions, and human-control boundary. Slides and documents must distinguish:

- **implemented now** — demonstrated by code/tests;
- **pilot target** — a measurable hypothesis;
- **roadmap** — not yet implemented.

## References

- NIST, *AI Risk Management Framework* and *Generative AI Profile*: https://www.nist.gov/itl/ai-risk-management-framework
- OWASP GenAI Security Project, *Top 10 for LLM and GenAI Applications*: https://genai.owasp.org/llm-top-10/
- European Union, *General Data Protection Regulation (EU) 2016/679*: https://eur-lex.europa.eu/eli/reg/2016/679/
