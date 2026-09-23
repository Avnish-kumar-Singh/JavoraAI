"""
Planner Node

LangGraph node that delegates reasoning to PlannerAgent.
"""

from app.graph.state import AgentState
from app.core.container import get_planner_agent


def planner_node(state: AgentState) -> AgentState:
    return get_planner_agent().plan(state)
