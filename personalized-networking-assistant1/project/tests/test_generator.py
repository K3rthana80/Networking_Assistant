"""Unit tests for app.services.topic_generator."""

from __future__ import annotations

import pytest

from app.services import topic_generator


@pytest.fixture(autouse=True)
def force_template_fallback(monkeypatch):
    """Force the template-based path so tests stay fast and deterministic."""
    monkeypatch.setattr(topic_generator, "_load_generator", lambda: None)
    yield


def test_generate_returns_exactly_three_suggestions():
    suggestions = topic_generator.generate_conversation_starters(
        themes=["Artificial Intelligence", "Climate Change", "Urban Planning"],
        interests=["Machine Learning", "Healthcare"],
        count=3,
    )
    assert len(suggestions) == 3


def test_generate_suggestions_are_unique():
    suggestions = topic_generator.generate_conversation_starters(
        themes=["Artificial Intelligence"],
        interests=["Artificial Intelligence"],
        count=3,
    )
    assert len(suggestions) == len(set(suggestions))


def test_generate_suggestions_are_strings_ending_in_punctuation():
    suggestions = topic_generator.generate_conversation_starters(
        themes=["Technology"], interests=["Design"], count=3
    )
    for line in suggestions:
        assert isinstance(line, str)
        assert line.strip() != ""
        assert line.strip()[-1] in ".?!"


def test_generate_respects_requested_count():
    suggestions = topic_generator.generate_conversation_starters(
        themes=["Finance", "Marketing"], interests=["Entrepreneurship"], count=2
    )
    assert len(suggestions) == 2


def test_generate_raises_without_any_topics():
    with pytest.raises(ValueError):
        topic_generator.generate_conversation_starters(themes=[], interests=[], count=3)
