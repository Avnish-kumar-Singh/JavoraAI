"""
Request/response schemas.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ---------------- Auth ----------------

class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    # Accepts either the username or the email address.
    identifier: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    created_at: datetime
    last_login_at: Optional[datetime] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user: UserOut


# ---------------- Chat ----------------

class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    session_id: Optional[int] = None


class ChatResponse(BaseModel):
    session_id: int
    history_id: int
    response: str
    intent: str
    tool: str
    status: str
    latency_ms: int
    cached: bool


# ---------------- History ----------------

class HistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: Optional[int]
    query: str
    response: str
    intent: str
    tool: str
    status: str
    latency_ms: int
    created_at: datetime


class HistoryPage(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[HistoryItem]


class SessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    created_at: datetime
    updated_at: datetime


class SessionDetail(SessionOut):
    entries: list[HistoryItem]
