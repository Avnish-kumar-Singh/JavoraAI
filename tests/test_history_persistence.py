from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api.chat_service import load_history_for_model, record_history
from app.api.db import Base
from app.api.models import ChatSession, QueryHistory, User


def _build_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return Session(bind=engine)


def test_load_history_for_model_keeps_more_than_three_pairs():
    db = _build_db()
    user = User(username="persisted", email="persisted@example.com", password_hash="hash")
    db.add(user)
    db.commit()
    db.refresh(user)

    session = ChatSession(user_id=user.id, title="Follow-up chat")
    db.add(session)
    db.commit()
    db.refresh(session)

    for i in range(1, 9):
        entry = QueryHistory(
            user_id=user.id,
            session_id=session.id,
            query=f"Q{i}",
            response=f"A{i}",
            created_at=datetime.now(timezone.utc),
        )
        db.add(entry)
    db.commit()

    history = load_history_for_model(db, session)

    assert len(history) >= 8, f"Expected more retained history, got {len(history)}"
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Q1"
    assert history[-1]["role"] == "assistant"
    assert history[-1]["content"] == "A8"

    db.close()
