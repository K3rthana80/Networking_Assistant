"""
Unit tests for app.services.fact_checker.

The real ``wikipedia`` package makes live HTTP calls, so every test
here installs a fake ``wikipedia`` module into ``sys.modules`` before
calling the service. This keeps tests hermetic, fast, and able to run
without network access.
"""

from __future__ import annotations

import sys
import types

import pytest

from app.services import fact_checker


class _FakePage:
    def __init__(self, title: str, content: str, url: str):
        self.title = title
        self.content = content
        self.url = url


class _FakeDisambiguationError(Exception):
    def __init__(self, options):
        super().__init__("disambiguation")
        self.options = options


class _FakePageError(Exception):
    pass


def _install_fake_wikipedia(monkeypatch, *, page=None, raise_disambiguation=None, raise_page_error=False, raise_other=False):
    fake_module = types.ModuleType("wikipedia")
    fake_exceptions = types.SimpleNamespace(
        DisambiguationError=_FakeDisambiguationError,
        PageError=_FakePageError,
    )
    fake_module.exceptions = fake_exceptions
    fake_module.set_lang = lambda lang: None

    def fake_page(query, auto_suggest=True, redirect=True):
        if raise_disambiguation is not None:
            raise _FakeDisambiguationError(raise_disambiguation)
        if raise_page_error:
            raise _FakePageError()
        if raise_other:
            raise ConnectionError("timeout")
        return page

    fake_module.page = fake_page
    monkeypatch.setitem(sys.modules, "wikipedia", fake_module)
    return fake_module


def test_fact_check_returns_first_paragraph(monkeypatch):
    page = _FakePage(
        title="Blockchain",
        content="Blockchain is a distributed ledger.\n\n== History ==\nMore text here.",
        url="https://en.wikipedia.org/wiki/Blockchain",
    )
    _install_fake_wikipedia(monkeypatch, page=page)

    result = fact_checker.fact_check("Blockchain")

    assert result.found is True
    assert result.title == "Blockchain"
    assert result.summary == "Blockchain is a distributed ledger."
    assert result.url == "https://en.wikipedia.org/wiki/Blockchain"


def test_fact_check_handles_page_not_found(monkeypatch):
    _install_fake_wikipedia(monkeypatch, raise_page_error=True)

    result = fact_checker.fact_check("asdkjhaskjdhaksjhd")

    assert result.found is False
    assert "No Wikipedia page was found" in result.summary


def test_fact_check_handles_disambiguation_by_retrying_first_option(monkeypatch):
    page = _FakePage(
        title="Mercury (element)",
        content="Mercury is a chemical element.",
        url="https://en.wikipedia.org/wiki/Mercury_(element)",
    )

    fake_module = _install_fake_wikipedia(monkeypatch, raise_disambiguation=["Mercury (element)", "Mercury (planet)"])

    call_count = {"n": 0}
    original_page = fake_module.page

    def page_side_effect(query, auto_suggest=True, redirect=True):
        call_count["n"] += 1
        if call_count["n"] == 1:
            return original_page(query, auto_suggest, redirect)
        return page

    fake_module.page = page_side_effect

    result = fact_checker.fact_check("Mercury")

    assert result.found is True
    assert result.title == "Mercury (element)"


def test_fact_check_handles_network_errors_gracefully(monkeypatch):
    _install_fake_wikipedia(monkeypatch, raise_other=True)

    result = fact_checker.fact_check("Anything")

    assert result.found is False
    assert "temporarily unavailable" in result.summary


def test_fact_check_raises_on_empty_query():
    with pytest.raises(ValueError):
        fact_checker.fact_check("")
