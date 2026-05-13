from langgraph.graph import StateGraph, END
from typing import TypedDict
from agents.supervisor import SupervisorAgent

class CanaryState(TypedDict):
    supplier: str
    result:   dict
    error:    str | None

supervisor = SupervisorAgent()


def run_supervisor(state: CanaryState) -> CanaryState:
    try:
        result = supervisor.run(state["supplier"])
        return {**state, "result": result, "error": None}
    except Exception as exc:
        return {**state, "result": {}, "error": str(exc)}


def route_output(state: CanaryState) -> str:
    return state.get("result", {}).get("gate", "ALERT_ONLY")


def auto_execute(state: CanaryState) -> CanaryState:
    action = state["result"]["synthesis"]["primary_action"]
    print(f"[AUTO-EXECUTE] {action}")
    return state


def human_review(state: CanaryState) -> CanaryState:
    action = state["result"]["synthesis"]["primary_action"]
    print(f"[HUMAN REVIEW QUEUED] {action}")
    return state


def alert_only(state: CanaryState) -> CanaryState:
    action = state["result"]["synthesis"]["primary_action"]
    print(f"[ALERT ONLY] {action}")
    return state


builder = StateGraph(CanaryState)
builder.add_node("supervisor",   run_supervisor)
builder.add_node("AUTO_EXECUTE", auto_execute)
builder.add_node("HUMAN_REVIEW", human_review)
builder.add_node("ALERT_ONLY",   alert_only)

builder.set_entry_point("supervisor")
builder.add_conditional_edges("supervisor", route_output, {
    "AUTO_EXECUTE": "AUTO_EXECUTE",
    "HUMAN_REVIEW": "HUMAN_REVIEW",
    "ALERT_ONLY":   "ALERT_ONLY",
})

for node in ["AUTO_EXECUTE", "HUMAN_REVIEW", "ALERT_ONLY"]:
    builder.add_edge(node, END)

canary_graph = builder.compile()
