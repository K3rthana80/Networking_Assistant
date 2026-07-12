"""
Pydantic schemas used across the Personalized Networking Assistant API.

Every request and response body is modeled explicitly so FastAPI can
validate input, generate accurate OpenAPI docs, and return meaningful
422 errors when a client sends malformed data.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


# --------------------------------------------------------------------------
# /analyze-event
# --------------------------------------------------------------------------

class EventAnalysisRequest(BaseModel):
    description: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="Free-text description of the networking event.",
        examples=["AI for Sustainable Cities Conference"],
    )

    @field_validator("description")
    @classmethod
    def description_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("description cannot be blank")
        return value.strip()


class EventAnalysisResponse(BaseModel):
    themes: List[str] = Field(..., description="Top themes detected in the event description.")


# --------------------------------------------------------------------------
# /generate-conversation
# --------------------------------------------------------------------------

class ConversationRequest(BaseModel):
    description: str = Field(..., min_length=3, max_length=1000)
    interests: List[str] = Field(
        ...,
        min_length=1,
        max_length=20,
        description="List of the user's personal or professional interests.",
        examples=[["Artificial Intelligence", "Climate Change", "Urban Planning"]],
    )

    @field_validator("description")
    @classmethod
    def description_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("description cannot be blank")
        return value.strip()

    @field_validator("interests")
    @classmethod
    def interests_not_blank(cls, value: List[str]) -> List[str]:
        cleaned = [i.strip() for i in value if i and i.strip()]
        if not cleaned:
            raise ValueError("at least one non-empty interest is required")
        return cleaned


class ConversationResponse(BaseModel):
    themes: List[str]
    suggestions: List[str]


# --------------------------------------------------------------------------
# /fact-check
# --------------------------------------------------------------------------

class FactCheckRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=200, examples=["Blockchain"])

    @field_validator("query")
    @classmethod
    def query_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("query cannot be blank")
        return value.strip()


class FactCheckResponse(BaseModel):
    summary: str
    title: Optional[str] = None
    url: Optional[str] = None
    found: bool = True


# --------------------------------------------------------------------------
# /history
# --------------------------------------------------------------------------

class HistoryEntry(BaseModel):
    timestamp: datetime
    event: str
    interests: List[str]
    themes: List[str]
    suggestions: List[str]


class HistoryResponse(BaseModel):
    history: List[HistoryEntry]


# --------------------------------------------------------------------------
# /feedback
# --------------------------------------------------------------------------

class FeedbackAction(str):
    LIKE = "like"
    DISLIKE = "dislike"


class FeedbackRequest(BaseModel):
    suggestion: str = Field(..., min_length=1, max_length=500)
    action: str = Field(..., description="Either 'like' or 'dislike'.")

    @field_validator("action")
    @classmethod
    def action_must_be_valid(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in ("like", "dislike"):
            raise ValueError("action must be 'like' or 'dislike'")
        return normalized


class FeedbackEntry(BaseModel):
    timestamp: datetime
    suggestion: str
    action: str


class FeedbackResponse(BaseModel):
    feedback: List[FeedbackEntry]


class MessageResponse(BaseModel):
    message: str
