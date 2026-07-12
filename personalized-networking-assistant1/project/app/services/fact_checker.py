"""
Fact Checker Service
======================

Looks up a topic on Wikipedia and returns its first paragraph as a
quick, neutral summary a user can skim before bringing it up in
conversation.

Handles the three failure modes the ``wikipedia`` package is prone to:
    * ``DisambiguationError`` - the query is ambiguous; we retry with
      the first suggested option.
    * ``PageError`` - no matching page exists.
    * Network timeouts / connection errors.

All failures are converted into a well-formed ``FactCheckResult``
instead of bubbling up as raw exceptions, so the API layer can always
return a clean, predictable JSON body.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT_SECONDS = 8


@dataclass
class FactCheckResult:
    summary: str
    title: Optional[str] = None
    url: Optional[str] = None
    found: bool = True


def fact_check(query: str) -> FactCheckResult:
    """
    Return the first paragraph of the Wikipedia page matching
    ``query``. Falls back to a friendly message if no page is found,
    the query is ambiguous with no usable option, or the request
    times out.
    """
    if not query or not query.strip():
        raise ValueError("query must not be empty")

    query = query.strip()

    try:
        import wikipedia  # type: ignore
    except ImportError:
        logger.error("The 'wikipedia' package is not installed.")
        return FactCheckResult(
            summary="Fact checking is temporarily unavailable: the Wikipedia client is not installed.",
            found=False,
        )

    wikipedia.set_lang("en")

    try:
        page = wikipedia.page(query, auto_suggest=True, redirect=True)
    except wikipedia.exceptions.DisambiguationError as exc:
        # Retry with the first disambiguation option, if any.
        options = getattr(exc, "options", [])
        if not options:
            return FactCheckResult(
                summary=f"\"{query}\" is ambiguous on Wikipedia and no alternatives were found.",
                found=False,
            )
        try:
            page = wikipedia.page(options[0], auto_suggest=False, redirect=True)
        except Exception as inner_exc:  # noqa: BLE001
            logger.warning("Disambiguation retry failed for '%s': %s", query, inner_exc)
            return FactCheckResult(
                summary=(
                    f"\"{query}\" is ambiguous on Wikipedia. Possible options include: "
                    f"{', '.join(options[:5])}."
                ),
                found=False,
            )
    except wikipedia.exceptions.PageError:
        return FactCheckResult(
            summary=f"No Wikipedia page was found for \"{query}\". Try a more specific search term.",
            found=False,
        )
    except Exception as exc:  # noqa: BLE001 - covers timeouts/connection errors from the requests lib
        logger.warning("Wikipedia lookup failed for '%s': %s", query, exc)
        return FactCheckResult(
            summary="Fact checking is temporarily unavailable. Please try again in a moment.",
            found=False,
        )

    first_paragraph = _first_paragraph(page.content)
    return FactCheckResult(
        summary=first_paragraph,
        title=page.title,
        url=page.url,
        found=True,
    )


def _first_paragraph(content: str) -> str:
    """Extract just the first non-empty paragraph from page content."""
    for block in content.split("\n"):
        cleaned = block.strip()
        if cleaned and not cleaned.startswith("=="):
            return cleaned
    return content.strip()[:500]
