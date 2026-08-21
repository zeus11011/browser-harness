"""Wiring for the plan -> execute -> verify loop.

Node implementations live in `graph/nodes/`, routing logic in `graph/routing.py`,
and the shared state/schemas in `graph/state.py`.
"""

from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode

from graph.mcp_tools import get_browser_ops_tools
from graph.nodes import make_executor_node, make_planning_node, make_verifier_node
from graph.routing import route_after_executor, route_after_verifier
from graph.state import GraphState
from utils.config import get_llm


async def build_graph():
    tools = await get_browser_ops_tools()
    llm = get_llm()

    graph = StateGraph(GraphState)
    graph.add_node("planning", make_planning_node(llm))
    graph.add_node("executor", make_executor_node(llm, tools))
    graph.add_node("verifier", make_verifier_node(llm))
    graph.add_node("tools", ToolNode(tools))

    graph.add_edge(START, "planning")
    graph.add_edge("planning", "executor")
    graph.add_conditional_edges("executor", route_after_executor)
    graph.add_edge("tools", "verifier")
    graph.add_conditional_edges("verifier", route_after_verifier)

    return graph.compile()
