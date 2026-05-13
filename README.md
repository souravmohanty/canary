<div align="center">

```
 ██████╗ █████╗ ███╗   ██╗ █████╗ ██████╗ ██╗   ██╗
██╔════╝██╔══██╗████╗  ██║██╔══██╗██╔══██╗╚██╗ ██╔╝
██║     ███████║██╔██╗ ██║███████║██████╔╝ ╚████╔╝ 
██║     ██╔══██║██║╚██╗██║██╔══██║██╔══██╗  ╚██╔╝  
╚██████╗██║  ██║██║ ╚████║██║  ██║██║  ██║   ██║   
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝  
```

**Agentic Supply Chain Intelligence**

*Early warning. Autonomous action. Zero blind spots.*

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-latest-1C3C3C?style=flat-square)](https://langchain-ai.github.io/langgraph/)
[![Claude](https://img.shields.io/badge/Powered%20by-Claude%20Opus%20%2F%20Sonnet-D97757?style=flat-square)](https://anthropic.com)
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/Status-POC-F59E0B?style=flat-square)]()

</div>

---

## What is Canary?

Canary is a **multi-agent AI system** that monitors supplier signals across your supply chain and autonomously recommends — or executes — procurement actions before disruptions become crises.

Named after the canary in the coal mine, it watches so you don't have to.

Traditional supply chain tools give you dashboards. Canary gives you decisions.

```
Supplier risk detected → agents reason in parallel → confidence-gated action
```

When TaiwanSemi's capacity drops 35%, freight rates spike, and a typhoon warning fires simultaneously, Canary doesn't show you three alerts. It says: *"Pre-qualify MexicoLogistics as backup. Issue contingency PO. Reroute 30% of critical SKUs to air freight. Confidence: 0.91 — queued for your approval."*

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    SIGNAL INGESTION                      │
│  Supplier feeds · Geo/trade · Weather · Freight · Demand │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              SUPERVISOR AGENT  (Claude Opus)             │
│         Orchestrates · Resolves conflicts · Gates        │
└──────┬──────────────┬──────────────┬───────────┬────────┘
       │              │              │           │
       ▼              ▼              ▼           ▼
  ┌─────────┐   ┌──────────┐  ┌──────────┐ ┌─────────┐
  │  Risk   │   │  Demand  │  │ Supplier │ │Routing  │
  │ Agent   │   │  Agent   │  │  Agent   │ │ Agent   │
  │ Sonnet  │   │ Sonnet   │  │ Sonnet   │ │ Sonnet  │
  └────┬────┘   └────┬─────┘  └────┬─────┘ └────┬────┘
       └──────────────┴──────────────┴───────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  CONFIDENCE GATE                         │
│   ≥ 0.85 AUTO_EXECUTE · 0.60–0.84 HUMAN_REVIEW         │
│                    < 0.60 ALERT_ONLY                     │
└─────────────────────────────────────────────────────────┘
```

### The four specialist agents

| Agent | Responsibility | Model |
|---|---|---|
| **Risk Sensing** | Scores disruption probability from signal context | Claude Sonnet |
| **Demand Forecast** | Adjusts safety stock and expedite recommendations | Claude Sonnet |
| **Supplier Intel** | Ranks backup vendors when primary is at risk | Claude Sonnet |
| **Logistics Routing** | Recommends alternative freight paths with cost delta | Claude Sonnet |

The **Supervisor** (Claude Opus) fans out to all four in parallel, synthesizes outputs, resolves conflicts, and routes to the appropriate execution path.

---

## Quickstart

### Prerequisites

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) package manager
- Anthropic API key — get one at [console.anthropic.com](https://console.anthropic.com)

### Install

```bash
git clone https://github.com/your-org/canary.git
cd canary

# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv add anthropic langgraph langchain-anthropic chromadb \
       sentence-transformers fastapi uvicorn pandas \
       pydantic python-dotenv rich
```

### Configure

```bash
cp .env.example .env
# Add your key:
# ANTHROPIC_API_KEY=sk-ant-...
```

### Run

```bash
uv run python run.py
```

Expected output:

```
━━━━━━━━━━ CANARY — Supply Chain Intelligence ━━━━━━━━━━

Generating signals and indexing...
Ingested 80 signals into local vector store

Analysing TaiwanSemi...
Analysing MalaysiaPCB...
Analysing ShanghaiAssembly...
Analysing MexicoLogistics...

╭─────────────────┬──────────────┬────────────┬────────────────────────────────────────╮
│ Supplier        │ Gate         │ Confidence │ Primary Action                         │
├─────────────────┼──────────────┼────────────┼────────────────────────────────────────┤
│ TaiwanSemi      │ HUMAN_REVIEW │ 0.78       │ Pre-qualify MexicoLogistics as backup  │
│ MalaysiaPCB     │ ALERT_ONLY   │ 0.52       │ Monitor freight rate trend — no action │
│ ShanghaiAssembly│ AUTO_EXECUTE │ 0.91       │ Increase safety stock to 6 weeks       │
│ MexicoLogistics │ ALERT_ONLY   │ 0.38       │ Stable — no intervention needed        │
╰─────────────────┴──────────────┴────────────┴────────────────────────────────────────╯
```

---

## Project Structure

```
canary/
├── .env                    # ANTHROPIC_API_KEY
├── .env.example
├── CLAUDE.md               # Claude Code context file
├── README.md
├── run.py                  # Entry point
├── graph.py                # LangGraph graph definition
├── data/
│   └── signals.py          # Synthetic supplier signal generator
├── store/
│   └── vector_store.py     # ChromaDB wrapper (local, no Docker)
├── tools/
│   └── signal_api.py       # Signal retrieval tool
└── agents/
    ├── base.py             # AgentOutput model + BaseAgent ABC
    ├── risk.py             # Risk sensing agent
    ├── demand.py           # Demand forecast agent
    ├── supplier.py         # Supplier intelligence agent
    ├── routing.py          # Logistics routing agent
    └── supervisor.py       # Orchestrator — fan-out, synthesis, gating
```

---

## How It Works

### 1. Signal ingestion

Canary ingests supplier signals — capacity changes, lead time shifts, news alerts, freight spikes, quality flags — and indexes them into a local ChromaDB vector store using `sentence-transformers` embeddings. In production this layer connects to live EDI feeds, news APIs, AIS vessel tracking, and ERP systems.

### 2. Agent reasoning

Each specialist agent retrieves relevant signals via semantic search, constructs a structured prompt, and calls Claude to reason over the context. Every agent returns a typed `AgentOutput`:

```python
class AgentOutput(BaseModel):
    agent_name:     str
    confidence:     float       # 0.0 – 1.0
    recommendation: str
    evidence:       list[str]
    metadata:       dict
```

### 3. Supervisor synthesis

The Supervisor runs the **Risk agent first** to seed a `risk_score` into shared state, then fans out the remaining three agents in parallel via `ThreadPoolExecutor`. It passes all outputs to Claude Opus, which synthesizes a unified action plan and resolves any conflicts between agents.

### 4. Confidence gate

```
confidence ≥ 0.85  →  AUTO_EXECUTE   (system acts autonomously)
confidence 0.60–0.84  →  HUMAN_REVIEW  (queued for approval)
confidence < 0.60   →  ALERT_ONLY    (monitoring only)
```

### 5. LangGraph routing

The graph routes the supervisor output to one of three terminal nodes based on the gate decision, providing a clean extension point for adding ERP write-back, Slack approval webhooks, or audit logging.

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | required | Your Anthropic API key |
| `LANGCHAIN_TRACING_V2` | `false` | Enable LangSmith tracing |
| `LANGCHAIN_API_KEY` | — | Required if tracing enabled |
| `AUTO_EXECUTE_THRESHOLD` | `0.85` | Confidence floor for autonomous execution |
| `HUMAN_REVIEW_THRESHOLD` | `0.60` | Confidence floor for human review queue |

---

## Extending Canary

### Swap synthetic signals for real feeds

Replace `data/signals.py` with a live ingestion pipeline:

```python
# Example: RSS news feed
import feedparser

def ingest_news_feed(url: str, store: SignalStore):
    feed = feedparser.parse(url)
    for entry in feed.entries:
        store.ingest_text(entry.summary, metadata={"source": url})
```

### Add a FastAPI endpoint

```python
# api.py
from fastapi import FastAPI
from graph import canary_graph

app = FastAPI(title="Canary API")

@app.post("/analyse/{supplier}")
async def analyse(supplier: str):
    result = canary_graph.invoke({
        "supplier": supplier,
        "result": {},
        "error": None,
    })
    return result
```

Run with:
```bash
uv run uvicorn api:app --reload
```

### Add Slack approval webhook

In `graph.py`, update `human_review()` to POST to your Slack webhook:

```python
import httpx

def human_review(state: CanaryState) -> CanaryState:
    action = state["result"]["synthesis"]["primary_action"]
    httpx.post(SLACK_WEBHOOK_URL, json={
        "text": f"🟡 *Canary approval needed*\n{action}",
        "attachments": [{
            "actions": [
                {"type": "button", "text": "Approve", "value": "approve"},
                {"type": "button", "text": "Reject",  "value": "reject"},
            ]
        }]
    })
    return state
```

### Enable LangSmith tracing

```bash
# .env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__...
LANGCHAIN_PROJECT=canary
```

Every agent step, tool call, and token count will appear in the LangSmith dashboard.

### Persist the vector store

Swap the in-memory client for a persistent one:

```python
# store/vector_store.py
self.client = chromadb.PersistentClient(path="./canary_db")
```

---

## Roadmap

- [ ] Live signal ingestion (news RSS, AIS vessel tracking, GDELT geopolitical events)
- [ ] FastAPI REST layer with OpenAPI docs
- [ ] Slack / Teams approval webhook with one-tap Approve/Reject
- [ ] SAP OData write-back for autonomous PO issuance
- [ ] Operator dashboard (Next.js) with live risk heat map
- [ ] LangSmith tracing integration
- [ ] Persistent ChromaDB with supplier history
- [ ] Supplier risk score model trained on historical disruption events (XGBoost)
- [ ] Multi-tenant support for multiple supply chain networks
- [ ] SOC 2 Type II compliance hardening

---

## Tech Stack

| Component | Technology |
|---|---|
| Agent framework | [LangGraph](https://langchain-ai.github.io/langgraph/) |
| LLM — Supervisor | Claude Opus (`claude-opus-4-6`) |
| LLM — Specialists | Claude Sonnet (`claude-sonnet-4-6`) |
| Vector store | [ChromaDB](https://www.trychroma.com/) |
| Embeddings | `sentence-transformers` (`all-MiniLM-L6-v2`) |
| Data validation | [Pydantic](https://docs.pydantic.dev/) v2 |
| Concurrency | `concurrent.futures.ThreadPoolExecutor` |
| Package manager | [uv](https://docs.astral.sh/uv/) |
| CLI output | [Rich](https://rich.readthedocs.io/) |

---

## Contributing

Contributions are welcome. Please open an issue before submitting a PR for significant changes.

```bash
# Fork the repo, then:
git checkout -b feature/my-feature
uv run python run.py          # verify it runs
git commit -m "feat: my feature"
git push origin feature/my-feature
# Open a pull request
```

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

<div align="center">

Built with [Claude](https://anthropic.com) · Powered by [LangGraph](https://langchain-ai.github.io/langgraph/)

*The canary warns. The agents act.*

</div>
