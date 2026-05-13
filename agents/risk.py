import json
from anthropic import Anthropic
from .base import BaseAgent, AgentOutput
from tools.signal_api import search_signals

client = Anthropic()


class RiskSensingAgent(BaseAgent):
    def __init__(self):
        super().__init__("risk_agent")

    def run(self, state: dict) -> AgentOutput:
        supplier = state["supplier"]
        docs, metas = search_signals(f"disruption risk {supplier}", n=6)
        context = "\n".join([
            f"- [{m['signal_type']} | severity={m['severity']}] {d}"
            for d, m in zip(docs, metas)
        ])
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            system="You are a supply chain risk analyst. Output ONLY valid JSON — no preamble, no markdown fences.",
            messages=[{
                "role": "user",
                "content": f"""Supplier: {supplier}
Recent signals:
{context}
Return JSON with this exact schema:
{{
  "confidence":      float between 0 and 1,
  "recommendation":  "one clear action sentence",
  "evidence":        ["signal detail 1", "signal detail 2"],
  "risk_score":      float between 0 and 1,
  "urgency_hours":   integer
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
                "risk_score":    data["risk_score"],
                "urgency_hours": data["urgency_hours"],
            }
        )
