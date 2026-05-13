import json
from anthropic import Anthropic
from .base import BaseAgent, AgentOutput

client = Anthropic()

VENDOR_DB = [
    {"name": "MalaysiaPCB",     "region": "SEA",   "capacity": "high",   "lead_time_days": 18, "quality_score": 0.91},
    {"name": "VietnamAssembly", "region": "SEA",   "capacity": "medium", "lead_time_days": 22, "quality_score": 0.87},
    {"name": "MexicoLogistics", "region": "LATAM", "capacity": "high",   "lead_time_days": 12, "quality_score": 0.93},
    {"name": "IndiaComponents", "region": "SAS",   "capacity": "medium", "lead_time_days": 25, "quality_score": 0.85},
    {"name": "PolandPrecision", "region": "EU",    "capacity": "low",    "lead_time_days": 20, "quality_score": 0.96},
]


class SupplierIntelAgent(BaseAgent):
    def __init__(self):
        super().__init__("supplier_agent")

    def run(self, state: dict) -> AgentOutput:
        at_risk    = state["supplier"]
        risk_score = state.get("risk_score", 0.5)

        if risk_score < 0.45:
            return AgentOutput(
                agent_name=self.name,
                confidence=0.92,
                recommendation=f"No supplier switch needed — {at_risk} risk score {risk_score:.2f} is below threshold",
                evidence=[f"Risk score {risk_score:.2f} < 0.45 threshold"]
            )

        alternatives = [v for v in VENDOR_DB if v["name"] != at_risk]
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            system="You are a procurement analyst. Output ONLY valid JSON.",
            messages=[{
                "role": "user",
                "content": f"""At-risk supplier: {at_risk} (risk score: {risk_score:.2f})
Available alternatives:
{json.dumps(alternatives, indent=2)}
Rank the top 2 alternatives considering capacity, lead time, quality, and geographic diversification.
Return JSON:
{{
  "confidence":        float,
  "recommendation":    "clear action sentence",
  "evidence":          ["reason for top choice", "reason for second choice"],
  "top_alternatives":  ["vendor_name_1", "vendor_name_2"]
}}"""
            }]
        )
        data = json.loads(resp.content[0].text.strip())
        return AgentOutput(
            agent_name=self.name,
            confidence=data["confidence"],
            recommendation=data["recommendation"],
            evidence=data["evidence"],
            metadata={"top_alternatives": data["top_alternatives"]}
        )
