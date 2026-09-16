# Ecommerce Data Pipeline Freshness and Missing Records

Why it can happen: late source events, failed ingestion, schema drift, duplicate keys, an incomplete date partition, transformation failure, or a semantic-model refresh can make dashboards stale or incomplete.

Safe first checks:
- identify the pipeline, dataset/table, run ID, expected freshness SLA, and affected partition
- compare source event counts with bronze/raw, curated, and reporting-layer counts
- inspect the first failed step and exact error without exposing customer payloads
- distinguish late data from permanently missing data and preserve replay/idempotency controls
- validate row counts and key business totals after recovery before closing the incident

Route orchestration, ingestion, transformation, warehouse, and data-quality failures to Data Engineering. Route a correct curated dataset with an incorrect visual or measure to BI & Analytics. Major revenue or order-data gaps during business reporting windows require high priority.

External basis reviewed for this synthetic runbook: Microsoft Learn, “Understand star schema and the importance for Power BI,” https://learn.microsoft.com/en-us/power-bi/guidance/star-schema
