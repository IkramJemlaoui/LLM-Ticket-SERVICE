# SECURITY.md

## Security Posture for the PoC

This repository is designed for classroom/demo use and demonstrates secure defaults for an investor-ready pilot conversation.

## Secrets Policy

- Never commit API keys, tokens, or passwords.
- Use environment variables loaded from a local `.env` file.
- `.env.example` contains placeholders only.
- Rotate any demo credentials after public presentation.

## Authentication / Authorization

### v1.0.0 demo
- No external identity provider is included.
- The Streamlit app is intended for local demo use.

### Pilot recommendation
- Front the app with enterprise SSO
- Enforce RBAC:
  - submitter can create tickets
  - agent can view AI suggestions
  - manager can review metrics
  - admin can configure knowledge sources

## PII Handling

Support tickets can contain personal data such as names, email addresses, phone numbers, device identifiers, and internal context. The app applies the following controls:

- email-like and phone-like values are redacted before telemetry logging
- when cloud redaction is enabled, subject, description, and requester are each sanitized before provider calls
- only approved support articles are used for grounding
- no long-term storage of raw prompts beyond the local running session in demo mode

## Data Residency

This PoC supports two operating modes:

- **Local/mock mode:** no external model call
- **Cloud mode:** inference location depends on the configured provider

Before a real pilot:
- select a provider region aligned with company policy
- document retention and residency rules
- confirm whether ticket content may leave the tenant or region

## External Services

Potentially used, depending on configuration:

- Azure OpenAI or another OpenAI-compatible LLM endpoint

No arbitrary third-party tools are invoked by the model.

## Prompt & Output Safety

- suspicious prompt-injection patterns stop the workflow before downstream agents run
- generated replies are restricted to retrieved internal knowledge
- retrieval matches below the configured confidence threshold are rejected and escalated
- the Risk & Quality Agent checks taxonomy, prohibited security-bypass language, citation provenance, and evidence presence
- max tokens and low temperature reduce uncontrolled outputs
- agent execution is capped and no agent can send messages, mutate tickets, browse the web, or invoke arbitrary tools
- customer-facing drafts require an explicit human approval event

## Logging & Monitoring

Telemetry is written to `logs/app_events.jsonl` and includes only privacy-minimized metadata such as:

- timestamp
- prompt version
- model/provider
- latency
- per-agent status/latency
- retrieval hits and scores
- quality score and workflow state
- token usage when supplied by the provider
- refusal/fallback flags

Do not ship raw user ticket bodies to shared logs in production.

## Supply Chain / Dependencies

- versions are pinned in `requirements.txt`
- run smoke tests before demo or release
- prefer a lockfile in future iterations

## Public Repo Guidance

This repo is intended to be public for the assignment. Before publishing:

- verify there are no secrets in commit history
- replace demo links/placeholders
- remove any private company data
- confirm all datasets and documentation are legally shareable
