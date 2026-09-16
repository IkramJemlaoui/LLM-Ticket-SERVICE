# AegisDesk User Views

## Page 1 — Employee Help Portal

The first page is designed for employees. Analysis happens before any ticket is created.

1. An employee or team describes any internal request and supplies impact, urgency, affected-user count, and the channel for status updates.
2. The Safety & Privacy Agent screens the input.
3. The Triage Agent classifies the request and deterministic policy recommends an accountable team.
4. The Knowledge Agent searches approved articles and human-verified resolved cases.
5. The portal immediately displays the request type, team, intake priority, closest solved case, safe proposed solution, approved explanation/tips, and missing information.
6. The employee chooses either **The suggested solution worked** or **Submit ticket to recommended team**.

If self-service works, no unnecessary ticket is created and a privacy-minimized outcome event is recorded. If the ticket is submitted, it is persisted in SQLite, routed to the recommended team, selected in the Support Workspace, and placed according to its priority score. Unsafe input receives no troubleshooting instructions and can only follow the security-review path.

## Page 2 — Support Workspace

The second page is designed for whichever department owns the request: IT, Data, Operations, Finance, HR, Security, Ecommerce, or another approved specialist team. These teams may also create requests for each other through the Employee Request Portal.

It provides:

- urgency-ranked ticket queue and SLA information;
- current owner and recommended accountable team;
- full request, impact, channel, and queue score;
- prominent similar solved case and extracted verified resolution;
- approved documentation and diagnostic explanation;
- editable final response to the employee;
- RAG relevance, accepted source references, quality score, and full agent trace;
- safety warnings and human-control reasons;
- useful/not-relevant retrieval feedback;
- approve, reject, reassign, escalate, resolve, and publish-to-case-memory controls.

Approval assigns the recommended classification/team but does not send anything externally. Resolving and publishing is a separate human action. Real outbound delivery, user identity, RBAC, and Jira/ITSM synchronization remain production-roadmap integrations.
