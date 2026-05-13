import json
from anthropic import Anthropic
from .base import BaseAgent, AgentOutput
from tools.signal_api import search_signals

client = Anthropic()

SKU_BASELINE = {
    "TaiwanSemi":       {"sku": "SEMI-001", "weekly_units": 5000, "safety_stock_weeks": 3},
    "MalaysiaPCB":      {"sku": "PCB-204",  "weekly_units": 8200, "safety_stock_weeks": 2},
    "ShanghaiAssembly": {"sku": "ASSY-089", "weekly_units": 3100, "safety_stock_weeks": 4},
    "MexicoLogistics":  {"sku": "LOG-310",  "weekly_units": 6500, "safety_stock_weeks": 2},
}


class DemandForecastAgent(BaseAgent):
    def __init__(self):
        super().__init__("demand_agent")

    def run(self, state: dict) -> AgentOutput:
        supplier   = state["supplier"]
        risk_score = state.get("risk_score", 0.5)
        baseline   = SKU_BASELINE.get(supplier, {"sku": "UNKNOWN", "weekly_units": 1000, "safety_stock_weeks": 2})
        docs, _ = search_signals(f"demand supply shortage {supplier}", n=4)
        context = "\n".join(f"- {d}" for d in docs)
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            system="You are a demand planning analyst. Output ONLY valid JSON.",
            messages=[{
                "role": "user",
                "content": f"""Supplier: {supplier}
SKU: {baseline['sku']}
Current weekly demand: {baseline['weekly_units']} units
Safety stock: {baseline['safety_stock_weeks']} weeks
Risk score: {risk_score:.2f}
Relevant signals:
{context}
Should we adjust safety stock or expedite orders? Return JSON:
{{
  "confidence":        float,
  "recommendation":    "action sentence",
  "evidence":          ["reason 1", "reason 2"],
  "adjusted_safety_stock_weeks": integer,
  "expedite_order":    boolean
}}"""
            }]
        )
        data = json.loads(resp.content[0].text.strip())
        return AgentOutput(
            agent_name=self.name,
            confidence=data["confidence"],
            recommendation=data["recommendation"],
            evidence=data["evidence"],
            metadata={
                "adjusted_safety_stock_weeks": data["adjusted_safety_stock_weeks"],
                "expedite_order": data["expedite_order"],
            }
        )
