"""
LangGraph Builder

The compiled graph is cached — building it per request was pure overhead.
Use `app.core.container.get_graph()` to obtain the shared instance.
"""

from functools import lru_cache

from langgraph.graph import StateGraph, START, END

from app.graph.state import AgentState
from app.nodes.planner_node import planner_node
from app.nodes.router_node import router_node
from app.nodes.tool_executor_node import tool_executor_node


@lru_cache(maxsize=1)
def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node("planner", planner_node)
    builder.add_node("router", router_node)
    builder.add_node("tool_executor", tool_executor_node)

    builder.add_edge(START, "planner")
    builder.add_edge("planner", "router")
    builder.add_edge("router", "tool_executor")
    builder.add_edge("tool_executor", END)

    return builder.compile()
