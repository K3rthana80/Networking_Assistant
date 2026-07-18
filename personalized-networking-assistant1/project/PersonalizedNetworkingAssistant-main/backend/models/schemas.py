from pydantic import BaseModel


class EventRequest(BaseModel):
    event: str


class ConversationRequest(BaseModel):
    event: str
    interest: str


class FactRequest(BaseModel):
    topic: str


class FeedbackRequest(BaseModel):
    feedback: str


class HealthResponse(BaseModel):
    status: str
    version: str


class FactResponse(BaseModel):
    verified: bool
    topic: str
    summary: str
    
class HistoryResponse(BaseModel):
    timestamp: str
    event: str
    interest: str
    themes: list
    conversation: str


class FeedbackResponse(BaseModel):
    timestamp: str
    feedback: str