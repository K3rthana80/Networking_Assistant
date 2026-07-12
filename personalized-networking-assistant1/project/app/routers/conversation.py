"""
Conversation Router
======================

Defines every HTTP endpoint for the Personalized Networking
Assistant: event analysis, conversation generation, fact checking,
history, and feedback.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    ConversationRequest,
    ConversationResponse,
    EventAnalysisRequest,
    EventAnalysisResponse,
    FactCheckRequest,
    FactCheckResponse,
    FeedbackRequest,
    FeedbackResponse,
    HistoryResponse,
    MessageResponse,
)
from app.services import event_analyzer, fact_checker, feedback_logger, history_logger, topic_generator

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/analyze-event", response_model=EventAnalysisResponse)
def analyze_event(payload: EventAnalysisRequest) -> EventAnalysisResponse:
    """Extract the top themes from an event description."""
    try:
        themes = event_analyzer.extract_themes(payload.description, top_n=3)
        return EventAnalysisResponse(themes=themes)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("analyze_event failed")
        raise HTTPException(status_code=500, detail="Failed to analyze event description.") from exc


@router.post("/generate-conversation", response_model=ConversationResponse)
def generate_conversation(payload: ConversationRequest) -> ConversationResponse:
    """Detect themes and generate three networking conversation starters, then log them."""
    try:
        themes = event_analyzer.extract_themes(payload.description, top_n=3)
        suggestions = topic_generator.generate_conversation_starters(
            themes=themes, interests=payload.interests, count=3
        )
        history_logger.log_conversation(
            event=payload.description,
            interests=payload.interests,
            themes=themes,
            suggestions=suggestions,
        )
        return ConversationResponse(themes=themes, suggestions=suggestions)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("generate_conversation failed")
        raise HTTPException(status_code=500, detail="Failed to generate conversation starters.") from exc


@router.post("/fact-check", response_model=FactCheckResponse)
def fact_check(payload: FactCheckRequest) -> FactCheckResponse:
    """Look up a topic on Wikipedia and return its opening summary."""
    try:
        result = fact_checker.fact_check(payload.query)
        return FactCheckResponse(
            summary=result.summary,
            title=result.title,
            url=result.url,
            found=result.found,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("fact_check failed")
        raise HTTPException(status_code=500, detail="Fact check service failed unexpectedly.") from exc


@router.get("/history", response_model=HistoryResponse)
def get_history() -> HistoryResponse:
    """Return all past conversations, newest first."""
    try:
        entries = history_logger.get_history()
        return HistoryResponse(history=entries)
    except Exception as exc:  # noqa: BLE001
        logger.exception("get_history failed")
        raise HTTPException(status_code=500, detail="Failed to load history.") from exc


@router.get("/feedback", response_model=FeedbackResponse)
def get_feedback() -> FeedbackResponse:
    """Return all recorded feedback, newest first."""
    try:
        entries = feedback_logger.get_feedback()
        return FeedbackResponse(feedback=entries)
    except Exception as exc:  # noqa: BLE001
        logger.exception("get_feedback failed")
        raise HTTPException(status_code=500, detail="Failed to load feedback.") from exc


@router.post("/feedback", response_model=MessageResponse)
def post_feedback(payload: FeedbackRequest) -> MessageResponse:
    """Record a like/dislike for a given conversation starter."""
    try:
        feedback_logger.log_feedback(suggestion=payload.suggestion, action=payload.action)
        return MessageResponse(message="Feedback recorded.")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("post_feedback failed")
        raise HTTPException(status_code=500, detail="Failed to record feedback.") from exc
