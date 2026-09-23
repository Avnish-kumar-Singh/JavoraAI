"""
Chat Service

Bridges the HTTP layer to the LangGraph pipeline and persists history.

Two execution paths:

* `answer()`   — runs the full compiled graph, returns the finished answer.
* `stream()`   — plans the route itself, then streams tokens for the two
                 text-generation paths (plain LLM and RAG). The tool paths
                 that are not token-generating (compiler, DSA, review, web)
                 are run to completion and emitted as one chunk.

Streaming is the single biggest win for *perceived* response time: the
first token lands in about a second instead of the user staring at a
spinner for the whole generation.
"""

import time
from datetime import datetime, timezone
from typing import Iterator, Optional

from sqlalchemy.orm import Session

from app.api.models import ChatSession, QueryHistory, User
from app.config.logging_config import logger
from app.core.cache import make_key, response_cache
from app.core.text import is_smalltalk
from app.core.container import (
    get_answer_agent,
    get_context_builder,
    get_graph,
    get_llm_service,
    get_planner_agent,
    get_retriever,
)
from app.core.enums import ToolName

STREAMABLE_TOOLS = {ToolName.LLM.value, ToolName.RAG.value}
MAX_TITLE_LENGTH = 60
# Keep more of the same chat thread available so follow-up questions and
# iterative debugging still feel like one continuous conversation.
HISTORY_TURNS_SENT_TO_MODEL = 12
DEFAULT_TITLE = "New chat"


def _title_from(message: str) -> str:
    title = message.strip().replace("\n", " ")
    if len(title) > MAX_TITLE_LENGTH:
        title = title[:MAX_TITLE_LENGTH].rstrip() + "..."
    return title or DEFAULT_TITLE


# --------------------------------------------------------------------
# Session + history persistence
# --------------------------------------------------------------------

def get_or_create_session(
    db: Session,
    user: User,
    session_id: Optional[int],
    first_message: str,
) -> ChatSession:
    if session_id is not None:
        session = (
            db.query(ChatSession)
            .filter(ChatSession.id == session_id, ChatSession.user_id == user.id)
            .one_or_none()
        )
        if session is not None:
            return session

    # A brand-new chat opened with "hi" gets a neutral title rather than
    # the greeting itself — otherwise every casual chat in the sidebar
    # ends up named "Hii chat!!" and they become indistinguishable.
    title = DEFAULT_TITLE if is_smalltalk(first_message) else _title_from(first_message)

    session = ChatSession(user_id=user.id, title=title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def maybe_retitle_session(db: Session, session: ChatSession, message: str) -> None:
    """
    A session opened with small talk keeps the placeholder title until the
    user actually asks something — then it's renamed from that message, so
    the sidebar shows what the chat is about instead of "New chat" or a
    stale greeting.
    """
    if session.title == DEFAULT_TITLE and not is_smalltalk(message):
        session.title = _title_from(message)
        db.commit()


def load_history_for_model(db: Session, session: ChatSession) -> list[dict]:
    """
    Rebuild the current chat thread in chronological order so follow-up
    questions still work after a page refresh without dropping earlier turns.
    """
    rows = (
        db.query(QueryHistory)
        .filter(QueryHistory.session_id == session.id)
        .order_by(QueryHistory.created_at.asc())
        .limit(HISTORY_TURNS_SENT_TO_MODEL)
        .all()
    )

    messages: list[dict] = []
    for row in rows:
        messages.append({"role": "user", "content": row.query})
        messages.append({"role": "assistant", "content": row.response})
    return messages


def record_history(
    db: Session,
    user: User,
    session: ChatSession,
    query: str,
    response: str,
    intent: str,
    tool: str,
    status: str,
    latency_ms: int,
    cached: bool,
) -> QueryHistory:
    entry = QueryHistory(
        user_id=user.id,
        session_id=session.id,
        query=query,
        response=response,
        intent=intent,
        tool=tool,
        status=status,
        latency_ms=latency_ms,
        cached=1 if cached else 0,
    )
    db.add(entry)

    # entry.created_at is only populated at flush, so take the clock
    # directly rather than reading a column that is still None here.
    session.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(entry)
    return entry


# --------------------------------------------------------------------
# Execution
# --------------------------------------------------------------------

def _base_state(query: str, history: list[dict]) -> dict:
    return {
        "messages": history,
        "user_query": query,
        "intent": "",
        "selected_tool": "",
        "context": "",
        "response": "",
        "status": "",
        "error": "",
    }


def _normalize(response) -> str:
    if isinstance(response, str):
        return response
    if isinstance(response, dict):
        return response.get("message", str(response))
    return str(response)


def answer(query: str, history: list[dict]) -> dict:
    """Blocking path — runs the whole graph."""
    started = time.perf_counter()

    state = _base_state(query, history)
    result = get_graph().invoke(state)

    return {
        "response": _normalize(result.get("response", "")),
        "intent": result.get("intent", "general"),
        "tool": result.get("selected_tool", "llm"),
        "status": result.get("status") or "SUCCESS",
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "cached": False,
    }


def stream(query: str, history: list[dict]) -> Iterator[dict]:
    """
    Yields dict events:
        {"type": "meta",  "intent":..., "tool":...}
        {"type": "token", "text": "..."}
        {"type": "done",  "response":..., "latency_ms":..., "cached":...}
    """
    started = time.perf_counter()

    state = _base_state(query, history)
    get_planner_agent().plan(state)

    tool = state["selected_tool"]
    intent = state["intent"]

    yield {"type": "meta", "intent": intent, "tool": tool}

    if tool not in STREAMABLE_TOOLS:
        # Non-generative tools: run to completion, emit in one piece.
        from app.tools.registry import ToolRegistry

        try:
            result = ToolRegistry().get_tool(tool).execute(state)
            text = _normalize(result.get("response", ""))
            status = result.get("status") or "SUCCESS"
        except Exception as exc:
            logger.exception("Tool execution failed")
            text = f"Something went wrong running the {tool} tool: {exc}"
            status = "FAILED"

        yield {"type": "token", "text": text}
        yield {
            "type": "done",
            "response": text,
            "status": status,
            "latency_ms": int((time.perf_counter() - started) * 1000),
            "cached": False,
        }
        return

    # RAG: fetch context before generating.
    if tool == ToolName.RAG.value:
        try:
            documents = get_retriever().retrieve(query)
            state["context"] = get_context_builder().build(documents)
        except Exception:
            logger.exception("Retrieval failed — continuing without context")
            state["context"] = ""

    cache_key = make_key("answer", query, state.get("context", ""))
    cached_response = response_cache.get(cache_key)

    if cached_response is not None:
        yield {"type": "token", "text": cached_response}
        yield {
            "type": "done",
            "response": cached_response,
            "status": "SUCCESS",
            "latency_ms": int((time.perf_counter() - started) * 1000),
            "cached": True,
        }
        return

    agent = get_answer_agent()
    prompt, plan = agent.build_prompt(state)

    collected: list[str] = []
    for piece in get_llm_service().stream(prompt, max_tokens=plan["max_tokens"]):
        collected.append(piece)
        yield {"type": "token", "text": piece}

    full = "".join(collected)
    if full and not full.startswith("Error:"):
        response_cache.set(cache_key, full)

    yield {
        "type": "done",
        "response": full,
        "status": "SUCCESS",
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "cached": False,
    }
