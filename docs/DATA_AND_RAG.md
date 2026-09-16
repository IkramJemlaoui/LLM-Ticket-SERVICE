# AegisDesk Data, RAG, and Case Memory

## What is stored and where

The running application uses a local SQLite database at `data/aegisdesk.db`. It is created automatically on first launch and is excluded from Git because it is runtime state.

| Data | Runtime storage | Reproducible source |
|---|---|---|
| Tickets and status | SQLite `tickets` table | `data/synthetic_tickets.json` for seed records |
| Ticket activity | SQLite `activities` table | activity entries in the synthetic fixture plus runtime events |
| Approved article content and metadata | SQLite `knowledge_articles` table | Markdown files in `data/knowledge_base/` |
| Reusable past solutions | resolved tickets with `resolution_verified=1` | verified resolution fields in the synthetic fixture, plus future human-approved resolutions |
| Retrieval usefulness feedback | SQLite `retrieval_feedback` table | explicit Useful / Not relevant review actions in the UI |
| Agent telemetry | `logs/app_events.jsonl` | generated at runtime; raw ticket and draft content are excluded |

The seed currently creates 27 synthetic tickets, 20 approved articles, and 16 human-labelled verified resolutions. Fifteen governed use cases provide routing and safety regression coverage. The corpus represents an ecommerce company with workplace IT, checkout/order operations, data engineering, analytics, Finance, HR, and cross-department support. This is a demonstration corpus, not production model-weight training data or a statistically representative evaluation set.

## Is this RAG?

Yes. The Knowledge Agent performs retrieval-augmented generation:

1. It combines the sanitized ticket, triage category, and summary into a search query.
2. It builds a TF-IDF representation of approved article paragraphs and human-verified resolved cases.
3. It ranks candidates using cosine similarity.
4. It rejects results below `RETRIEVAL_MIN_SCORE`, removes duplicate sources, and keeps at most `RETRIEVAL_TOP_K` results.
5. The Resolution Agent receives only those results as evidence and creates a cited draft.
6. The Risk & Quality Agent checks that every citation came from the accepted retrieval results.

This is lexical RAG. There is no vector database and no embedding model in the current PoC. The articles and cases do not train, fine-tune, or permanently modify the LLM. They are retrieved as temporary context for the current ticket.

## Approved company article catalog

The synthetic approved catalog contains:

1. Business Application SSO Login Loops
2. Device Support Intake
3. Ecommerce Checkout and Payment Incident Triage
4. Ecommerce Metric Definitions and Ownership
5. Ecommerce Data Pipeline Freshness and Missing Records
6. Internal DNS Troubleshooting
7. Outlook Calendar Sync Troubleshooting
8. Power BI KPI Definition and Clarification
9. Power BI Semantic Model Refresh Failures
10. Suspected Phishing or Security Report
11. Shared Drive Access Requests
12. Managed Endpoint Storage Recovery
13. Microsoft Teams Audio Troubleshooting
14. VPN Access After Password Reset
15. Wi-Fi and Network Connectivity Checks

The complete catalog is visible in the app under **Evidence & controls → Browse the complete approved article catalog**. Article files remain readable and reviewable in `data/knowledge_base/`.

## How past solutions become reusable

An AI draft is never added to case memory automatically. The controlled lifecycle is:

`Create ticket → agents propose → human edits/reviews → Approve draft → Resolve ticket + reuse verified solution`

Only the final action sets `resolution_verified=1`. On the next search, that solution becomes an eligible `verified_case` result. The evidence panel labels it **Human-verified resolved case** so users can distinguish experience reuse from a policy article.

This design prevents unreviewed hallucinations, abandoned drafts, and failed troubleshooting attempts from contaminating future recommendations.

The **Useful match / Not relevant** control records labelled retrieval feedback. It does not retrain the live model automatically. After privacy review and sufficient labelled volume, the company can use this data to evaluate ranking changes or prepare a separately governed fine-tuning dataset.

## Smart queue ranking

At creation, a deterministic priority engine scores each ticket from 0 to 100 using:

- declared urgency;
- business-impact scope;
- number of affected users;
- explicit security and outage indicators.

The score maps to Low, Medium, High, or Critical and to an initial SLA target. The queue orders unresolved work by score, severity, and age; resolved tickets are placed after active work. The Triage Agent can recommend a category and higher priority, but it cannot silently lower the intake priority.

The routing taxonomy maps cases to Identity & Access, Workplace Collaboration, Infrastructure & Network, Endpoint Support, Security Operations, Business Applications, Ecommerce Platform, Data Engineering, BI & Analytics, or the general IT Service Desk. The UI shows the recommended accountable team immediately; the human approval step confirms the local assignment.

## Privacy and production boundary

SQLite is appropriate for a local, single-user classroom demonstration. A production pilot should use authenticated enterprise storage with encryption, RBAC, audit controls, retention/deletion rules, data residency decisions, backup/recovery, knowledge ownership, and concurrent transaction support. Production data should be de-identified for evaluation and should not be used for model training without a separate legal, privacy, security, and governance decision.

## Rebuild the demo database

Run:

```powershell
.\.venv\Scripts\python.exe .\scripts\seed_demo_data.py
```

The initializer is idempotent: it adds missing seed records and synchronizes article content without overwriting user-created tickets. To perform a full reset, stop the app, remove the generated `data/aegisdesk.db` file, and run the command again.
