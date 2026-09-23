"""
Tool Executor Node

Executes the tool selected by the planner/router.
"""

import time

from app.graph.state import AgentState
from app.config.logging_config import logger
from app.tools.registry import ToolRegistry

registry = ToolRegistry()


def tool_executor_node(state: AgentState) -> AgentState:
    tool_name = state["selected_tool"]
    logger.info(f"Executing Tool: {tool_name}")

    started = time.perf_counter()
    tool = registry.get_tool(tool_name)
    result = tool.execute(state)
    elapsed_ms = int((time.perf_counter() - started) * 1000)

    logger.info(f"Tool Execution Completed in {elapsed_ms} ms")
    return result
