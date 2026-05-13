# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**Canary** is a multi-agent AI system that monitors supplier signals and autonomously recommends (or executes) supply chain actions. A supervisor agent orchestrates four specialist agents in parallel, synthesizes their outputs with Claude Opus, and routes decisions through a confidence gate.

## Commands

```bash
# Install dependencies
uv add anthropic langgraph langchain-anthropic chromadb \
       sentence-transformers fastapi uvicorn pandas \
       pydantic python-dotenv rich

# Run the system
uv run python run.py
```

Copy `.env.example` to `.env` and fill in `ANTHROPIC_API_KEY` before running.

## Architecture

### Execution flow

1. `run.py` generates synthetic signals → ingests them into ChromaDB → invokes the LangGraph graph per supplier
2. `graph.py` defines a `StateGraph` with a single entry node (`supervisor`) and three terminal nodes (`AUTO_EXECUTE`, `HUMAN_REVIEW`, `ALERT_ONLY`) selected by a confidence gate
3. `agents/supervisor.py` runs in two phases:
   - **Phase 1 (serial):** `RiskSensingAgent` runs first and writes `risk_score` into shared state
   - **Phase 2 (parallel):** `DemandForecastAgent`, `SupplierIntelAgent`, and `RoutingAgent` run concurrently via `ThreadPoolExecutor`, receiving `risk_score` from phase 1
   - **Phase 3:** Claude Opus synthesizes all four agent outputs into a unified action plan and overall confidence score

### Confidence gate thresholds (`agents/supervisor.py`)

| Gate | Confidence | Behaviour |
|---|---|---|
| `AUTO_EXECUTE` | ≥ 0.85 | Action executed autonomously |
| `HUMAN_REVIEW` | 0.60 – 0.84 | Queued for human approval |
| `ALERT_ONLY` | < 0.60 | Monitoring alert only |

### Agent contracts

All agents extend `BaseAgent` ([agents/base.py](agents/base.py)) and return `AgentOutput` (a Pydantic v2 model). Every Claude call uses `system="Output ONLY valid JSON"` — responses are parsed with `json.loads` directly.

| Agent | Model | Key metadata output |
|---|---|---|
| `RiskSensingAgent` | claude-sonnet-4-6 | `risk_score`, `urgency_hours` |
| `DemandForecastAgent` | claude-sonnet-4-6 | `adjusted_safety_stock_weeks`, `expedite_order` |
| `SupplierIntelAgent` | claude-sonnet-4-6 | `top_alternatives` |
| `RoutingAgent` | claude-sonnet-4-6 | `recommended_route`, `cost_delta_pct` |
| `SupervisorAgent` (synthesis) | claude-opus-4-6 | `overall_confidence`, `primary_action` |

`SupplierIntelAgent` short-circuits and returns a no-action response when `risk_score < 0.45`.

### Vector store

`store/vector_store.py` wraps ChromaDB with a `SentenceTransformer("all-MiniLM-L6-v2")` embedder (fully local, no API key). The store is a process-level singleton (`get_store()`). The default client is in-memory and resets each run — swap to `chromadb.PersistentClient(path="./db")` for persistence.

### Data

`data/signals.py` generates synthetic supplier disruption signals (no external API required). Replace with a live feed (e.g. `feedparser`) for production.

## Extension points

- **FastAPI:** expose `POST /analyse/{supplier}` returning full result JSON
- **Persistent store:** `chromadb.PersistentClient(path="./db")` in `store/vector_store.py`
- **LangSmith tracing:** add `LANGCHAIN_TRACING_V2=true` to `.env`
- **Approval webhook:** POST to Slack in `human_review()` node in `graph.py`
- **ERP write-back:** call SAP OData API in `auto_execute()` node in `graph.py`
- **Live signals:** replace `data/signals.py` with `feedparser` RSS/news ingestion
