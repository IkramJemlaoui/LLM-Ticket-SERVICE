# Pitch Deck Outline (12 slides)

## 1. Title
LLM Service Desk Copilot  
AI assistant for faster, safer IT support triage

## 2. Problem
- tickets miss key details
- agents waste time asking the same clarifying questions
- knowledge is scattered
- slower resolutions and weaker SLA compliance

## 3. Why existing workflow fails
- manual triage
- inconsistent ticket quality
- repeated first-response work
- high-volume low-complexity issues still consume agent time

## 4. Solution
A service-desk copilot that:
- summarizes messy tickets
- asks for missing info
- suggests category and priority
- drafts a grounded first reply from approved internal knowledge

## 5. Demo journey
1. user submits a vague IT issue
2. AI clarifies and triages it
3. agent gets a grounded reply draft with citations

## 6. Visible AI moment
Show:
- summary
- missing info prompts
- category/priority suggestion
- grounded reply draft

## 7. AI & Guardrails
- provider/model actually used in the demo
- inference location
- retrieval method: TF-IDF lexical retrieval over markdown KB
- prompt injection detection
- redacted telemetry
- fallback when evidence is weak

## 8. 10-layer architecture
Use the architecture from `ARCHITECTURE.md`

## 9. Business value / KPI
Example KPI targets:
- reduce first-response drafting time by 60%
- reduce back-and-forth clarifications by 30%
- improve SLA compliance on common tickets

## 10. Responsible / Frugal AI
- smallest-sufficient model
- low temperature / token cap
- human-in-the-loop for high-impact actions
- no arbitrary tools
- only approved knowledge sources

## 11. Proof of implementation
- public repo
- one-command demo
- smoke tests
- release v1.0.0
- recorded demo link

## 12. Pilot ask
Request a 4-week pilot with one support queue and success metrics tied to:
- time-to-first-response
- reopen rate
- agent acceptance of AI suggestions

## Slide consistency notes

Update your existing slide:
- keep the business problem and solution
- change "vector store" to "TF-IDF retrieval over approved KB docs" unless you implement embeddings
- mark email / Teams / Slack as roadmap connectors unless you built them
- keep privacy, human review, and cost controls visible
