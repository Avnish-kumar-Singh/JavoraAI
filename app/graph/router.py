# """
# Graph Router

# Determines the next node.
# """

# from app.graph.state import AgentState


# def route(state: AgentState) -> str:
#     """
#     Return the next node name.
#     """

#     tool = state["selected_tool"]

#     if tool == "llm":
#         return "answer"

#     if tool == "rag":
#         return "rag"

#     if tool == "web":
#         return "web"

#     return "answer"


# from app.graph.state import AgentState
# from app.core.enums import ToolName
# 
# 
# def route(state: AgentState) -> str:
    # """
    # Decide which node to execute next.
    # Currently only the LLM path exists.
    # """
# 
    # tool = state["selected_tool"]
# 
    # if tool == ToolName.LLM.value:
        # return "answer"
# 
    # Temporary fallback until RAG and Web nodes are implemented
    # return "answer"
    
    
    
    
    
from app.graph.state import AgentState


def route(state: AgentState) -> str:
    return "end"