# LLM Service Desk Copilot

A Jira-style GenAI service desk workspace that helps support teams triage tickets faster, ask for missing details earlier, and draft grounded first replies from approved internal knowledge.

## Problem

IT support teams waste time because tickets arrive incomplete, agents repeat the same clarification questions, and internal troubleshooting knowledge is scattered. That creates slower first response times, inconsistent triage, and avoidable SLA risk.

## Solution

This PoC embeds an AI copilot inside a ticket-management experience that looks and feels like a modern service desk tool.

The copilot:
- summarizes messy tickets
- identifies missing information
- suggests category and priority
- drafts an agent reply grounded in approved KB articles
- blocks unsafe or policy-violating requests

## Target Users

- L1 IT support agents
- service desk managers
- employees submitting internal support requests

## Product Scope in v1.0.0

This release implements a **single web portal demo** in Streamlit with a **Jira-like UI**:
- left navigation with queue and filter controls
- center ticket queue and ticket detail workspace
- right AI Copilot panel for summary, triage, reply drafting, and grounding

It is a **working PoC**, not a real Jira integration.

## Demo Link

Add your recorded demo link here: `https://...`

## Team Members

- Lead student: `YOUR NAME`
- Team member 2: `NAME OR N/A`
- Team member 3: `NAME OR N/A`
- Team member 4: `NAME OR N/A`

## Quick Start

### Prerequisites
- Python 3.11+
- No GPU required
- Internet only if you switch from mock mode to a cloud LLM

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./scripts/run_demo.sh
```

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
powershell -ExecutionPolicy Bypass -File .\scripts\run_demo.ps1
```

The app opens through Streamlit at `http://localhost:8501`.

## One-Command Demo

- macOS/Linux: `./scripts/run_demo.sh`
- Windows: `powershell -ExecutionPolicy Bypass -File .\scripts\run_demo.ps1`

## Seed Data

```bash
python scripts/seed_demo_data.py
```

## Smoke Tests

```bash
pytest -k smoke
```

## Repository Structure

```text
app/                    UI, pipeline, retrieval, guardrails, mock/cloud provider logic
data/knowledge_base/    Approved KB articles used for grounding
docs/                   Demo script and deck outline
tests/                  Smoke tests
scripts/                Demo launcher scripts for Linux/macOS and Windows
```

## AI & Guardrails

### Where AI is used
- ticket summarization
- missing-information detection
- category suggestion
- priority suggestion
- grounded reply drafting

### Models, prompts, retrieval, inference location

**Default reproducible mode**
- provider: `mock`
- inference location: local deterministic fallback
- purpose: clean-machine demo with no secrets

**Optional investor demo mode**
- provider: Azure OpenAI or another OpenAI-compatible endpoint
- recommended generation model: `gpt-4.1-mini`
- inference location: cloud
- prompt style: single JSON response with strict schema
- retrieval: local TF-IDF search over approved markdown KB articles
- retrieval top-k: `3`

### Why this design
- smallest-sufficient model for short ticket reasoning
- fast, low-cost, reproducible demo path
- lexical retrieval is simpler and cheaper than a vector DB for a tiny controlled KB
- human review remains in the loop for high-impact actions

### Guardrails implemented
- prompt-injection detection
- PII redaction before telemetry
- optional redaction before cloud inference
- grounding to approved KB only
- refusal of unsafe security-bypass requests
- capped temperature and max tokens
- no arbitrary tool execution

### Quality & observability
- JSONL telemetry in `logs/app_events.jsonl`
- latency and retrieval-hit logging
- refusal and fallback flags
- smoke tests for the pipeline

### Known risks & mitigations
- hallucination risk reduced with grounding and low temperature
- wrong routing risk reduced by keeping agent review in the loop
- privacy risk reduced by redaction before logs
- prompt injection reduced by input scanning and refusal logic

## Stack Consistency Notes

This repo currently reflects:
- ticketing experience: **Jira-style mock workspace in Streamlit**
- real integration: **none**
- vector database: **none**
- retrieval method: **TF-IDF over local markdown KB articles**
- default model provider: **mock**

Your slides and demo narration should match those statements exactly unless you change the code and config.

## Environment Variables

See `.env.example`.

## AI Media Disclosure

If you use ElevenLabs, Synthesia, CapCut, or other media tools in the recorded demo, disclose them here and in the deck. Do not represent mocked features as implemented features.

## Data Sources

All sample KB files in `data/knowledge_base/` are synthetic demo content created for this PoC. Replace them only with legally usable internal content.

## Release

Tag the GitHub repository with `v1.0.0` before submission.
