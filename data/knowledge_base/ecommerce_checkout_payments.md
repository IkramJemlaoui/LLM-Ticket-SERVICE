# Ecommerce Checkout and Payment Incident Triage

Why it can happen: failures may come from browser/session problems, payment authentication, a payment-provider status, webhook delay, duplicate delivery, or an internal order-creation/fulfillment failure. A successful browser redirect alone is not proof that payment and fulfillment completed.

Safe first checks:
- collect only redacted order, checkout-session, and payment references; never request full card data
- determine scope by country, payment method, device, browser, and time window
- check the provider status and the payment lifecycle state
- correlate checkout, payment webhook, order, inventory, and fulfillment events by their identifiers
- make fulfillment idempotent and verify it has not already run before retrying

Route customer checkout and order-flow defects to the Ecommerce Platform Team. Route suspicious payment activity or data exposure to Security Operations. Do not manually mark an order paid without verified provider evidence and the approved business process.

External basis reviewed for this synthetic runbook: Stripe Documentation, “Fulfill orders,” https://docs.stripe.com/checkout/fulfillment and “The Payment Intents API,” https://docs.stripe.com/payments/payment-intents
