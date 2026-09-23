# """
# Router Node

# Responsible for selecting the next workflow step.
# """

# from app.graph.state import AgentState
# from app.config.logging_config import logger


# def router_node(state: AgentState) -> AgentState:
#     """
#     Router only logs the selected tool.
#     The actual routing is handled by LangGraph.
#     """

#     logger.info("Router Node Started")
#     logger.info(f"Selected Tool: {state['selected_tool']}")

#     return state



# """
# Router Node
# 
# Executes the selected tool.
# """
# 
# from app.graph.state import AgentState
# from app.config.logging_config import logger
# from app.tools.registry import ToolRegistry
# 
# registry = ToolRegistry()
# 
# 
# def router_node(state: AgentState) -> AgentState:
# 
    # logger.info("Router Node Started")
# 
    # tool_name = state["selected_tool"]
# 
    # logger.info(f"Selected Tool: {tool_name}")
# 
    # tool = registry.get_tool(tool_name)
# 
    # return tool.execute(state)
    
    
    
    
    
"""
Router Node

Only decides the route.
"""

from app.graph.state import AgentState
from app.config.logging_config import logger


def router_node(state: AgentState) -> AgentState:
    logger.info("Router Node Started")

    logger.info(f"Selected Tool: {state['selected_tool']}")

    return state