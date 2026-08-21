"""Conditional-edge logic: where the loop goes after the executor and the verifier."""

from typing import Literal

from langgraph.graph import END

from graph.state import GraphState

# Loop guards so a step that never verifies can't spin forever.
MAX_RETRIES_PER_STEP = 2
MAX_REPLANS = 2


def route_after_executor(state: GraphState) -> Literal["tools", "verifier"]:
    """Only hand off to ToolNode when the executor actually asked for a tool."""
    last = state["messages"][-1]
    return "tools" if getattr(last, "tool_calls", None) else "verifier"


def route_after_verifier(state: GraphState) -> Literal["executor", "planning", END]:
    if state.get("replans", 0) > MAX_REPLANS:
        return END
    if state.get("retries", 0) > MAX_RETRIES_PER_STEP:
        return END
    if state.get("feedback"):
        # Non-empty feedback means the step didn't pass: replan or retry.
        return "planning" if state.get("retries", 0) == 0 else "executor"
    # Step passed â€” move on, or finish if the plan is exhausted.
    return "executor" if state["step_index"] < len(state["plan"]) else END
