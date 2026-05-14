from anthropic import Anthropic
from .base import BaseAgent, AgentOutput, parse_json

client = Anthropic()

LANES = {
    "TaiwanSemi":       {"primary": "Taiwan → LA (ocean, 14d)",            "cost_usd_per_kg": 3.20},
    "MalaysiaPCB":      {"primary": "Penang → Rotterdam (ocean, 22d)",     "cost_usd_per_kg": 2.80},
    "ShanghaiAssembly": {"primary": "Shanghai → LA (ocean, 16d)",          "cost_usd_per_kg": 2.60},
    "MexicoLogistics":  {"primary": "Monterrey → Chicago (truck, 3d)",     "cost_usd_per_kg": 1.40},
}

ALTERNATIVES = [
    "Air freight (+$8/kg, -10 days transit)",
    "Alternate ocean carrier via Singapore hub (+4 days, -15% cost)",
    "Rail through Eastern Europe (+6 days, -8% cost)",
    "Split shipment: 30% air for critical SKUs, 70% ocean standard",
]


class RoutingAgent(BaseAgent):
    def __init__(self):
        super().__init__("routing_agent")

    def run(self, state: dict) -> AgentOutput:
        supplier   = state["supplier"]
        risk_score = state.get("risk_score", 0.5)
        lane       = LANES.get(supplier, {"primary": "Unknown", "cost_usd_per_kg": 3.0})
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            system="You are a logistics routing analyst. Output ONLY valid JSON.",
            messages=[{
                "role": "user",
                "content": f"""Supplier: {supplier}
Current primary lane: {lane['primary']}
Cost: ${lane['cost_usd_per_kg']}/kg
Disruption risk score: {risk_score:.2f}
Available alternatives:
{chr(10).join(f"- {a}" for a in ALTERNATIVES)}
Recommend the best routing strategy given the risk level. Return JSON:
{{
  "confidence":          float,
  "recommendation":      "action sentence",
  "evidence":            ["reason 1", "reason 2"],
  "recommended_route":   "route description",
  "cost_delta_pct":      float
}}"""
            }]
        )
        data = parse_json(resp.content[0].text)
        return AgentOutput(
            agent_name=self.name,
            confidence=data["confidence"],
            recommendation=data["recommendation"],
            evidence=data["evidence"],
            metadata={
                "recommended_route": data["recommended_route"],
                "cost_delta_pct":    data["cost_delta_pct"],
            }
        )
