"""
Service Container

Lazily-created process-wide singletons.

Before this, `ToolRegistry.__init__` eagerly built all six tools. That
chain constructed the Chroma vector store, the Ollama embedding client,
the DuckDuckGo search service and four separate ChatOllama clients — on
every process start, even for a user who only ever asks a plain question.

Everything here is built on first use and reused afterwards.
"""

from functools import lru_cache
from typing import Any

from app.config.logging_config import logger


@lru_cache(maxsize=1)
def get_llm_service():
    from app.services.llm_service import LLMService

    return LLMService()


@lru_cache(maxsize=1)
def get_response_planner():
    from app.services.response_planner import ResponsePlanner

    return ResponsePlanner()


@lru_cache(maxsize=1)
def get_prompt_builder():
    from app.synthesis.prompt_builder import PromptBuilder

    return PromptBuilder()


@lru_cache(maxsize=1)
def get_context_builder():
    from app.synthesis.context_builder import ContextBuilder

    return ContextBuilder()


@lru_cache(maxsize=1)
def get_retriever() -> Any:
    """
    Built lazily: opening Chroma and the embedding client costs ~1-2s and
    is pure waste for non-RAG questions.
    """
    logger.info("Initializing retriever (first RAG request)...")
    from app.rag.retriever import Retriever

    return Retriever()


@lru_cache(maxsize=1)
def get_answer_agent():
    from app.agents.answer_agent import AnswerAgent

    return AnswerAgent()


@lru_cache(maxsize=1)
def get_planner_agent():
    from app.agents.planner_agent import PlannerAgent

    return PlannerAgent()


@lru_cache(maxsize=1)
def get_graph():
    """
    Compiling the LangGraph is not free. The CLI rebuilt it per process
    and the API would have rebuilt it per request.
    """
    from app.graph.builder import build_graph

    return build_graph()
