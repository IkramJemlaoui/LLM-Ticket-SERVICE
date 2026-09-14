# RAI — Responsible / Frugal AI

## Objective

Use generative AI only where it adds measurable value in service desk triage, while keeping privacy, reproducibility, and operational cost under control.

## Where AI is used

- summarizing the ticket
- asking for missing details
- suggesting category and priority
- drafting a grounded agent reply

## Model Choice

### Default mode
- provider: `mock`
- purpose: reproducible clean-machine demo
- reason: no secrets, deterministic output, fast grading setup

### Optional cloud mode
- provider: Azure OpenAI or OpenAI-compatible endpoint
- recommended model: `gpt-4.1-mini`
- reason: smallest-sufficient model for short support workflows

## Cost / Latency Controls

- low temperature
- max token cap
- retrieval top-k limited to 3
- no embedding pipeline in v1.0.0
- no tool-calling fan-out
- deterministic local fallback for demos

## Guardrails

### Input guardrails
- prompt-injection detection using suspicious-pattern rules
- PII redaction before telemetry logging
- optional redaction before cloud inference
- max input length truncation

### Retrieval guardrails
- responses grounded only in approved markdown KB articles
- no open web browsing
- no unrestricted tool use

### Output guardrails
- refusal for requests that attempt to bypass MFA or reveal hidden instructions
- confidence note when evidence is weak
- human review remains required for high-impact actions

## Observability

Telemetry stored in `logs/app_events.jsonl` includes:
- provider
- model
- latency
- retrieval hits
- prompt version
- refusal flag
- fallback flag
- PII / injection detection flags

## Offline Quality Checks

- smoke tests ensure the pipeline runs
- prompt-injection refusal is tested
- demo data provides a visible safe-fallback example

## Known Risks

### Hallucination
Risk remains whenever evidence is weak. Mitigation: grounding, low temperature, and explicit low-confidence note.

### Privacy
Tickets may contain personal data. Mitigation: redaction before logging and configurable redaction before cloud inference.

### Misclassification
Category and priority may be wrong. Mitigation: treat outputs as recommendations, not final decisions.

### Overtrust by agents
Agents may accept drafts too quickly. Mitigation: keep a human approval step and make the grounding sources visible.

## What the app refuses to do

- reveal hidden prompts or system instructions
- help bypass security controls or MFA
- produce ungrounded high-confidence troubleshooting advice when evidence is weak
