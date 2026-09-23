"""
Chat routes: blocking answer + server-sent-events streaming.
"""

import json
from typing import Iterator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api import chat_service
from app.api.db import SessionLocal, get_db
from app.api.deps import get_current_user
from app.api.models import User
from app.api.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    session = chat_service.get_or_create_session(
        db, user, payload.session_id, payload.message
    )
    chat_service.maybe_retitle_session(db, session, payload.message)
    history = chat_service.load_history_for_model(db, session)

    result = chat_service.answer(payload.message, history)

    entry = chat_service.record_history(
        db=db,
        user=user,
        session=session,
        query=payload.message,
        response=result["response"],
        intent=result["intent"],
        tool=result["tool"],
        status=result["status"],
        latency_ms=result["latency_ms"],
        cached=result["cached"],
    )

    return ChatResponse(
        session_id=session.id,
        history_id=entry.id,
        response=result["response"],
        intent=result["intent"],
        tool=result["tool"],
        status=result["status"],
        latency_ms=result["latency_ms"],
        cached=result["cached"],
    )


@router.post("/stream")
def chat_stream(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Streams the answer as SSE. Each event is a JSON line:
        data: {"type":"meta"|"token"|"done", ...}
    """
    session = chat_service.get_or_create_session(
        db, user, payload.session_id, payload.message
    )
    chat_service.maybe_retitle_session(db, session, payload.message)
    history = chat_service.load_history_for_model(db, session)

    session_id = session.id
    session_title = session.title
    user_id = user.id
    message = payload.message

    def event_source() -> Iterator[str]:
        intent = "general"
        tool = "llm"

        yield f"data: {json.dumps({'type': 'session', 'session_id': session_id, 'title': session_title})}\n\n"

        final = {"response": "", "status": "SUCCESS", "latency_ms": 0, "cached": False}

        for event in chat_service.stream(message, history):
            if event["type"] == "meta":
                intent = event["intent"]
                tool = event["tool"]
            elif event["type"] == "done":
                final = event

            yield f"data: {json.dumps(event)}\n\n"

        # The request-scoped session is already closing by the time the
        # generator runs, so persist on a fresh one.
        write_db = SessionLocal()
        try:
            db_user = write_db.get(User, user_id)
            db_session = chat_service.get_or_create_session(
                write_db, db_user, session_id, message
            )
            chat_service.record_history(
                db=write_db,
                user=db_user,
                session=db_session,
                query=message,
                response=final.get("response", ""),
                intent=intent,
                tool=tool,
                status=final.get("status", "SUCCESS"),
                latency_ms=final.get("latency_ms", 0),
                cached=final.get("cached", False),
            )
        finally:
            write_db.close()

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
