# """
# Defines the shared state used by the LangGraph workflow.
# """

# from typing import Annotated

# from typing_extensions import TypedDict
# from langgraph.graph.message import add_messages


# class AgentState(TypedDict):
#     """
#     Shared state for every node in the graph.
#     """

#     # Chat history
#     messages: Annotated[list, add_messages]

#     # Original user question
#     user_query: str

#     # Intent classification
#     intent: str

#     # Which tool the planner selected
#     selected_tool: str

#     # Retrieved context (RAG)
#     context: str

#     # Final response
#     response: str

#     # Current workflow status
#     status: str

#     # Error message (if any)
#     error: str



"""
Defines the shared state used by the LangGraph workflow.
"""

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    Shared state for every node in the graph.
    """

    # Chat history
    messages: Annotated[list, add_messages]

    # Original user question
    user_query: str

    # Intent classification
    intent: str

    # Which tool the planner selected
    selected_tool: str

    # Retrieved context (RAG)
    context: str

    # Final response
    response: str

    # Current workflow status
    status: str

    # Error message (if any)
    error: str