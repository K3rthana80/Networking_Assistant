"""Unit tests for app.services.event_analyzer."""

from __future__ import annotations

import pytest

from app.services import event_analyzer


@pytest.fixture(autouse=True)
def force_keyword_fallback(monkeypatch):
    """
    Force every test in this module to use the lightweight keyword
    fallback instead of downloading/running the real transformer
    model, keeping unit tests fast and network-independent.
    """
    monkeypatch.setattr(event_analyzer, "_load_classifier", lambda: None)
    yield


def test_extract_themes_returns_three_themes():
    themes = event_analyzer.extract_themes("AI for Sustainable Cities Conference", top_n=3)
    assert len(themes) == 3
    assert all(isinstance(t, str) for t in themes)


def test_extract_themes_detects_relevant_keywords():
    themes = event_analyzer.extract_themes("A conference about artificial intelligence and machine learning")
    assert "Artificial Intelligence" in themes


def test_extract_themes_detects_climate_and_urban_topics():
    themes = event_analyzer.extract_themes("Discussing climate change and urban planning for smart cities")
    assert "Climate Change" in themes
    assert "Urban Planning" in themes


def test_extract_themes_falls_back_to_defaults_when_no_keywords_match():
    themes = event_analyzer.extract_themes("xyzzy plugh quux")
    assert len(themes) == 3
    assert all(isinstance(t, str) for t in themes)


def test_extract_themes_raises_on_empty_description():
    with pytest.raises(ValueError):
        event_analyzer.extract_themes("")

    with pytest.raises(ValueError):
        event_analyzer.extract_themes("   ")


def test_extract_themes_respects_top_n():
    themes = event_analyzer.extract_themes("AI, healthcare, finance, marketing, and design summit", top_n=2)
    assert len(themes) == 2
