import json
from concurrent.futures import ThreadPoolExecutor
from anthropic import Anthropic
from .base import AgentOutput
from .risk     import RiskSensingAgent
from .demand   import DemandForecastAgent
from .supplier import SupplierIntelAgent
from .routing  import RoutingAgent

client = Anthropic()

CONFIDENCE_THRESHOLDS = {
    "auto_execute": 0.85,   # Execute autonomously
    "human_review": 0.60,   # Queue for approval
    # below 0.60 = ALERT_ONLY
}


class SupervisorAgent:
    def __init__(self):
        self.agents = {
            "risk":     RiskSensingAgent(),
            "demand":   DemandForecastAgent(),
            "supplier": SupplierIntelAgent(),
            "routing":  RoutingAgent(),
        }

    def _run_safe(self, name: str, agent, state: dict) -> AgentOutput:
        try:
            return agent.run(state)
        except Exception as exc:
            return AgentOutput(
                agent_name=name,
                confidence=0.0,
                recommendation=f"Agent error: {exc}",
                evidence=[]
            )

    def _synthesize(self, outputs: list[AgentOutput], supplier: str) -> dict:
        summaries = "\n".join([
            f"[{o.agent_name}] confidence={o.confidence:.2f}: {o.recommendation}"
            for o in outputs
        ])
        resp = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=768,
            system="You are a supply chain decision orchestrator. Output ONLY valid JSON.",
            messages=[{
                "role": "user",
                "content": f"""Supplier under review: {supplier}
Agent assessments:
{summaries}
Synthesize into a unified action plan. Resolve any conflicts between agents.
Return JSON:
{{
  "overall_confidence":  float between 0 and 1,
  "primary_action":      "the single most important action to take now",
  "secondary_actions":   ["action 2", "action 3"],
  "conflicts_detected":  boolean,
  "conflict_resolution": "how conflicts were resolved, or null if none"
}}"""
            }]
        )
        return json.loads(resp.content[0].text.strip())

    def _gate(self, confidence: float) -> str:
        if confidence >= CONFIDENCE_THRESHOLDS["auto_execute"]:
            return "AUTO_EXECUTE"
        if confidence >= CONFIDENCE_THRESHOLDS["human_review"]:
            return "HUMAN_REVIEW"
        return "ALERT_ONLY"

    def run(self, supplier: str) -> dict:
        # Phase 1: risk agent first — seeds risk_score into shared state
        state       = {"supplier": supplier}
        risk_output = self._run_safe("risk", self.agents["risk"], state)
        state["risk_score"] = risk_output.metadata.get("risk_score", 0.5)

        # Phase 2: remaining agents in parallel
        with ThreadPoolExecutor(max_workers=3) as pool:
            futures = {
                name: pool.submit(self._run_safe, name, agent, state)
                for name, agent in self.agents.items()
                if name != "risk"
            }
            parallel_outputs = [f.result() for f in futures.values()]

        all_outputs = [risk_output] + parallel_outputs

        # Phase 3: synthesize + gate
        synthesis = self._synthesize(all_outputs, supplier)
        gate      = self._gate(synthesis["overall_confidence"])

        return {
            "supplier":      supplier,
            "gate":          gate,
            "synthesis":     synthesis,
            "agent_outputs": [o.model_dump() for o in all_outputs],
        }
