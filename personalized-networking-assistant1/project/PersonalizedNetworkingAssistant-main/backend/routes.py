from fastapi import APIRouter
from backend.services.event_analyzer import analyze_event
from backend.services.fact_checker import verify_topic
from backend.services.topic_generator import generate_conversation

from backend.models.schemas import (
    EventRequest,
    ConversationRequest,
    FactRequest,
    FactResponse
)

from backend.services.history_logger import (
    save_history,
    get_history
)

from backend.services.feedback_logger import (
    save_feedback,
    get_feedback
)

from backend.models.schemas import FeedbackRequest

router = APIRouter()


@router.get("/")
async def root():
    return {
        "message": "Personalized Networking Assistant API"
    }


@router.get("/health")
async def health():
    return {
        "status": "Running"
    }


@router.post("/analyze-event")
async def analyze_event_route(request: EventRequest):

    themes = analyze_event(request.event)

    return {
        "event": request.event,
        "themes": themes
    }
    

@router.post("/fact-check", response_model=FactResponse)
async def fact_check(request: FactRequest):

    return verify_topic(request.topic)


@router.post("/generate-conversation")
async def generate(request: ConversationRequest):

    themes = analyze_event(request.event)

    if themes:

        topic = themes[0]["theme"]

        wiki = verify_topic(topic)

        summary = wiki["summary"]
        verified = wiki["verified"]

    else:

        summary = ""

    conversation = generate_conversation(
        request.event,
        request.interest,
        themes,
        summary
    )
    
    save_history(
        request.event,
        request.interest,
        themes,
        conversation
    )

    return {
    "event": request.event,
    "interest": request.interest,
    "themes": themes,
    "verified": verified,
    "verified_summary": summary,
    "conversation": conversation
    }
    
@router.get("/history")
async def history():

    return get_history()


@router.post("/feedback")
async def feedback(request: FeedbackRequest):

    save_feedback(request.feedback)

    return {

        "message": "Feedback saved successfully."

    }


@router.get("/feedback")
async def feedback_history():

    return get_feedback()