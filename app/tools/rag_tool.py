"""
RAG Tool
"""

from app.tools.base_tool import BaseTool
from app.graph.state import AgentState
from app.config.logging_config import logger
from app.core.container import (
    get_answer_agent,
    get_context_builder,
    get_retriever,
)


class RAGTool(BaseTool):
    def execute(self, state: AgentState) -> AgentState:
        logger.info("RAG Tool Started")

        try:
            documents = get_retriever().retrieve(state["user_query"])
            state["context"] = get_context_builder().build(documents)
        except Exception:
            # A broken/empty vector store should degrade to a plain answer
            # rather than failing the whole request.
            logger.exception("Retrieval failed — answering without context")
            state["context"] = ""

        return get_answer_agent().generate(state)
