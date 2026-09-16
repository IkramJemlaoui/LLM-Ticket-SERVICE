# Ecommerce Metric Definitions and Ownership

Why it can happen: dashboard disputes often reflect different business definitions rather than a technical defect. Order date versus payment date, local versus UTC day boundaries, gross versus net revenue, cancellations, returns, taxes, shipping, and test orders can materially change the result.

Company demonstration definitions:
- Orders: distinct production order IDs created in the selected period, excluding test orders
- Gross merchandise value: item value before discounts, cancellations, returns, tax, and shipping
- Net sales: captured item revenue after discounts, cancellations, and approved returns; tax and shipping excluded
- Conversion rate: completed paid orders divided by eligible sessions under the approved analytics definition
- Return rate: approved returned units divided by fulfilled units for the cohort definition shown in the dashboard

The BI & Analytics Team owns presentation and measure logic. Data Engineering owns source pipelines and curated tables. Finance or the designated business owner approves financial KPI definitions. Never change a financial KPI solely to make it match an expected number.
