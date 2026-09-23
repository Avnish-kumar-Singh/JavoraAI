"""
History routes: browse, search, restore and delete persisted queries.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.api.db import get_db
from app.api.deps import get_current_user
from app.api.models import ChatSession, QueryHistory, User
from app.api.schemas import (
    HistoryItem,
    HistoryPage,
    SessionDetail,
    SessionOut,
)

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=HistoryPage)
def list_history(
    q: str | None = Query(None, description="Free-text search over questions"),
    tool: str | None = Query(None),
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Every question this user has ever asked, newest first."""
    query = db.query(QueryHistory).filter(QueryHistory.user_id == user.id)

    if q:
        pattern = f"%{q.strip()}%"
        query = query.filter(
            or_(
                QueryHistory.query.ilike(pattern),
                QueryHistory.response.ilike(pattern),
            )
        )

    if tool:
        query = query.filter(QueryHistory.tool == tool)

    total = query.with_entities(func.count(QueryHistory.id)).scalar() or 0

    rows = (
        query.order_by(QueryHistory.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return HistoryPage(
        total=total,
        limit=limit,
        offset=offset,
        items=[HistoryItem.model_validate(r) for r in rows],
    )


@router.get("/sessions", response_model=list[SessionOut])
def list_sessions(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rows = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user.id)
        .order_by(ChatSession.updated_at.desc())
        .all()
    )
    return [SessionOut.model_validate(r) for r in rows]


@router.get("/sessions/{session_id}", response_model=SessionDetail)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == user.id)
        .one_or_none()
    )
    if session is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")

    return SessionDetail(
        id=session.id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
        entries=[HistoryItem.model_validate(e) for e in session.entries],
    )


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == user.id)
        .one_or_none()
    )
    if session is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")

    db.delete(session)
    db.commit()


@router.delete("/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_history_item(
    history_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    entry = (
        db.query(QueryHistory)
        .filter(QueryHistory.id == history_id, QueryHistory.user_id == user.id)
        .one_or_none()
    )
    if entry is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "History entry not found")

    db.delete(entry)
    db.commit()
