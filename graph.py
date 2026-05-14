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
    if state.get("error") or not state.get("result"):
        return "ERROR"
    return state["result"].get("gate", "ALERT_ONLY")


def _get_action(state: CanaryState) -> str:
    return state.get("result", {}).get("synthesis", {}).get("primary_action", "No action (agent error)")


def auto_execute(state: CanaryState) -> CanaryState:
    print(f"[AUTO-EXECUTE] {_get_action(state)}")
    return state


def human_review(state: CanaryState) -> CanaryState:
    print(f"[HUMAN REVIEW QUEUED] {_get_action(state)}")
    return state


def alert_only(state: CanaryState) -> CanaryState:
    print(f"[ALERT ONLY] {_get_action(state)}")
    return state


def error_node(state: CanaryState) -> CanaryState:
    print(f"[ERROR] {state.get('error', 'Unknown error')}")
    return state


builder = StateGraph(CanaryState)
builder.add_node("supervisor",   run_supervisor)
builder.add_node("AUTO_EXECUTE", auto_execute)
builder.add_node("HUMAN_REVIEW", human_review)
builder.add_node("ALERT_ONLY",   alert_only)
builder.add_node("ERROR",        error_node)

builder.set_entry_point("supervisor")
builder.add_conditional_edges("supervisor", route_output, {
    "AUTO_EXECUTE": "AUTO_EXECUTE",
    "HUMAN_REVIEW": "HUMAN_REVIEW",
    "ALERT_ONLY":   "ALERT_ONLY",
    "ERROR":        "ERROR",
})

for node in ["AUTO_EXECUTE", "HUMAN_REVIEW", "ALERT_ONLY", "ERROR"]:
    builder.add_edge(node, END)

canary_graph = builder.compile()
