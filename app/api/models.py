"""
ORM models: users, chat sessions and persisted query history.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.api.db import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    sessions: Mapped[list["ChatSession"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    history: Mapped[list["QueryHistory"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class ChatSession(Base):
    """A conversation thread. Groups history entries so the UI can show
    a sidebar of past chats and restore one."""

    __tablename__ = "chat_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(200), default="New chat")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_utcnow, onupdate=_utcnow
    )

    user: Mapped["User"] = relationship(back_populates="sessions")
    entries: Mapped[list["QueryHistory"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="QueryHistory.created_at",
    )


class QueryHistory(Base):
    """One question + answer, with the routing and timing metadata."""

    __tablename__ = "query_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    session_id: Mapped[int | None] = mapped_column(
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )

    query: Mapped[str] = mapped_column(Text)
    response: Mapped[str] = mapped_column(Text, default="")

    intent: Mapped[str] = mapped_column(String(32), default="general")
    tool: Mapped[str] = mapped_column(String(32), default="llm")
    status: Mapped[str] = mapped_column(String(32), default="SUCCESS")

    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    cached: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=_utcnow, index=True
    )

    user: Mapped["User"] = relationship(back_populates="history")
    session: Mapped["ChatSession | None"] = relationship(back_populates="entries")


Index("ix_history_user_created", QueryHistory.user_id, QueryHistory.created_at)
