# Power BI Semantic Model Refresh Failures

Why it can happen: a dashboard can become stale when a scheduled refresh fails, the gateway is offline, source credentials expire, a schema changes, or capacity/time limits interrupt processing.

Safe first checks:
- open the semantic model refresh history and record status, time, duration, and the exact error
- confirm the configured gateway and cloud connections are online
- verify credentials through the approved credential-management process
- compare the dashboard timestamp with the upstream warehouse freshness timestamp
- do not republish, change schema, or disable security as an unapproved workaround

Route Power BI configuration and visual issues to BI & Analytics. Route missing or late warehouse data to Data Engineering. Escalate a revenue, orders, or operations dashboard affecting company-wide decisions as high impact.

External basis reviewed for this synthetic runbook: Microsoft Learn, “Configure scheduled refresh,” https://learn.microsoft.com/en-us/power-bi/connect-data/refresh-scheduled-refresh
