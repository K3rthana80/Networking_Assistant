"""
Integration tests for every API route, using FastAPI's TestClient.

Heavy AI services (theme extraction, text generation, Wikipedia
lookups) are monkeypatched at the module level so the test suite is
fast, deterministic, and runs fully offline. Storage is redirected to
a temporary directory so tests never touch the real history.json /
feedback.json files.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import event_analyzer, fact_checker, feedback_logger, history_logger, topic_generator
from app.services.fact_checker import FactCheckResult


@pytest.fixture(autouse=True)
def isolate_storage(tmp_path, monkeypatch):
    """Redirect history/feedback JSON storage to a temp directory per test."""
    monkeypatch.setattr(history_logger, "HISTORY_FILE", tmp_path / "history.json")
    monkeypatch.setattr(feedback_logger, "FEEDBACK_FILE", tmp_path / "feedback.json")
    yield


@pytest.fixture(autouse=True)
def stub_ai_services(monkeypatch):
    """Replace AI model calls with fast, deterministic stubs."""
    monkeypatch.setattr(
        event_analyzer, "extract_themes", lambda description, top_n=3: ["Artificial Intelligence", "Technology", "Innovation"][:top_n]
    )
    monkeypatch.setattr(
        topic_generator,
        "generate_conversation_starters",
        lambda themes, interests, count=3: [
            "What inspired you to attend this event?",
            "Which AI innovations excite you most?",
            "How do you see sustainability evolving?",
        ][:count],
    )
    monkeypatch.setattr(
        fact_checker,
        "fact_check",
        lambda query: FactCheckResult(
            summary=f"{query} is a topic with a Wikipedia summary.",
            title=query,
            url=f"https://en.wikipedia.org/wiki/{query}",
            found=True,
        ),
    )
    yield


@pytest.fixture()
def client():
    return TestClient(app)


# --------------------------------------------------------------------------
# Health
# --------------------------------------------------------------------------

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# --------------------------------------------------------------------------
# /analyze-event
# --------------------------------------------------------------------------

def test_analyze_event_success(client):
    response = client.post("/analyze-event", json={"description": "AI for Sustainable Cities Conference"})
    assert response.status_code == 200
    body = response.json()
    assert body["themes"] == ["Artificial Intelligence", "Technology", "Innovation"]


def test_analyze_event_rejects_short_description(client):
    response = client.post("/analyze-event", json={"description": "AI"})
    assert response.status_code == 422


def test_analyze_event_rejects_missing_field(client):
    response = client.post("/analyze-event", json={})
    assert response.status_code == 422


# --------------------------------------------------------------------------
# /generate-conversation
# --------------------------------------------------------------------------

def test_generate_conversation_success(client):
    response = client.post(
        "/generate-conversation",
        json={
            "description": "AI for Sustainable Cities Conference",
            "interests": ["Artificial Intelligence", "Climate Change", "Urban Planning"],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["themes"]) == 3
    assert len(body["suggestions"]) == 3


def test_generate_conversation_saves_to_history(client):
    client.post(
        "/generate-conversation",
        json={"description": "AI Conference", "interests": ["Machine Learning", "Healthcare"]},
    )
    history_response = client.get("/history")
    assert history_response.status_code == 200
    entries = history_response.json()["history"]
    assert len(entries) == 1
    assert entries[0]["event"] == "AI Conference"


def test_generate_conversation_rejects_empty_interests(client):
    response = client.post(
        "/generate-conversation",
        json={"description": "AI Conference", "interests": []},
    )
    assert response.status_code == 422


# --------------------------------------------------------------------------
# /fact-check
# --------------------------------------------------------------------------

def test_fact_check_success(client):
    response = client.post("/fact-check", json={"query": "Blockchain"})
    assert response.status_code == 200
    body = response.json()
    assert body["found"] is True
    assert "Blockchain" in body["summary"]


def test_fact_check_rejects_blank_query(client):
    response = client.post("/fact-check", json={"query": ""})
    assert response.status_code == 422


# --------------------------------------------------------------------------
# /history
# --------------------------------------------------------------------------

def test_history_empty_by_default(client):
    response = client.get("/history")
    assert response.status_code == 200
    assert response.json() == {"history": []}


def test_history_newest_first(client):
    client.post("/generate-conversation", json={"description": "Event One", "interests": ["A"]})
    client.post("/generate-conversation", json={"description": "Event Two", "interests": ["B"]})

    entries = client.get("/history").json()["history"]
    assert entries[0]["event"] == "Event Two"
    assert entries[1]["event"] == "Event One"


# --------------------------------------------------------------------------
# /feedback
# --------------------------------------------------------------------------

def test_post_and_get_feedback(client):
    post_response = client.post(
        "/feedback", json={"suggestion": "What inspired you to attend this event?", "action": "like"}
    )
    assert post_response.status_code == 200

    get_response = client.get("/feedback")
    assert get_response.status_code == 200
    entries = get_response.json()["feedback"]
    assert len(entries) == 1
    assert entries[0]["action"] == "like"


def test_feedback_rejects_invalid_action(client):
    response = client.post("/feedback", json={"suggestion": "Some suggestion", "action": "love"})
    assert response.status_code == 422
