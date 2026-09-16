# Power BI KPI Definition and Clarification

Why it can happen: two users can see different KPI values when filters, date ranges, time zones, sales channels, currencies, returns, or metric definitions differ. A KPI is not only a displayed number; it needs an agreed base measure, target, trend context, and business owner.

Safe first checks:
- record the dashboard, page, KPI name, displayed value, and expected value
- capture the active date range, region, channel, currency, and other filters
- check the semantic model's last refresh time
- compare the KPI definition in the metric catalog before changing DAX
- route definition questions to BI & Analytics and source-data discrepancies to Data Engineering

For ecommerce reporting, do not silently change a published measure. Confirm whether revenue means gross merchandise value, gross revenue, net revenue after discounts, or net revenue after returns and cancellations. Record the approved definition and owner in the ticket.

External basis reviewed for this synthetic runbook: Microsoft Learn, “Create key performance indicator (KPI) visualizations,” https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-kpi
