# ARCHITECTURE

## Overview

This PoC implements a **Jira-style service desk workspace** in Streamlit with a constrained GenAI copilot embedded in ticket triage.

## Layered Architecture

1. **Business Layer**  
   Faster IT ticket triage, fewer clarification loops, improved SLA compliance.

2. **User Layer**  
   L1 support agents and employees submitting requests.

3. **Experience Layer**  
   Streamlit UI with three panes:
   - left: queue filters and search
   - center: ticket list and ticket details
   - right: AI Copilot recommendations

4. **Application Layer**  
   `app/streamlit_app.py` manages state, rendering, ticket selection, and user actions.

5. **AI Orchestration Layer**  
   `app/pipeline.py` coordinates guardrails, retrieval, provider selection, fallback behavior, and telemetry.

6. **Guardrails Layer**  
   `app/guardrails.py` applies:
   - prompt-injection pattern detection
   - PII redaction
   - input truncation
   - refusal for clearly unsafe requests

7. **Knowledge / Retrieval Layer**  
   `app/retrieval.py` performs TF-IDF retrieval over approved markdown KB articles in `data/knowledge_base/`.

8. **Model Layer**  
   `app/llm.py` supports:
   - default reproducible mock provider
   - optional Azure OpenAI / OpenAI-compatible cloud provider

9. **Data Layer**  
   - demo ticket fixtures in `app/demo_data.py`
   - KB articles in `data/knowledge_base/`
   - redacted telemetry logs in `logs/app_events.jsonl`

10. **Ops & Governance Layer**  
   - `.env.example` for secret placeholders
   - smoke tests in `tests/test_smoke.py`
   - responsible AI disclosure in `RAI.md`
   - security controls documented in `SECURITY.md`

## End-to-End Flow

1. Agent selects a ticket in the queue.
2. The app sends the ticket subject + description to the orchestration layer.
3. Guardrails inspect the input for suspicious instructions and PII.
4. Retrieval searches approved KB articles for relevant grounding.
5. The provider generates structured output:
   - summary
   - missing information
   - suggested category
   - suggested priority
   - grounded draft reply
6. The UI renders the result in the AI Copilot panel.
7. Telemetry logs latency, retrieval hits, fallback/refusal status, and prompt version.

## Implementation Choices

### Why Streamlit
- fastest route to a working investor demo
- easy three-pane layout
- low setup friction on clean machines

### Why TF-IDF instead of a vector DB
- smaller operational footprint
- no embedding pipeline required for the assignment demo
- reproducible with zero external infrastructure

### Why mock mode by default
- removes secret-management friction during grading
- makes the demo deterministic and stable
- keeps the repo runnable on a clean machine

## Consistency Statement

The current codebase implements:
- **Jira-style UI look and feel**: yes
- **actual Jira backend integration**: no
- **vector DB**: no
- **RAG over approved local KB**: yes
- **cloud LLM required to run**: no

Slides and README should match those facts.
