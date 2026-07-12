"""
Event Analyzer Service
=======================

Extracts the top themes from a free-text event description.

Primary strategy: zero-shot classification with a Hugging Face
transformer (``facebook/bart-large-mnli``) against a curated label set
of professional/networking themes.

The transformer model is large (~1.6 GB) and requires network access
and a fair amount of RAM/CPU the first time it is downloaded. To keep
the service usable in constrained environments (CI, offline demos,
low-memory machines) the analyzer degrades gracefully to a
lightweight keyword-matching heuristic if ``transformers``/``torch``
are not installed or the model fails to load. Either path returns the
same shape of data, so the rest of the app never needs to know which
strategy served the request.
"""

from __future__ import annotations

import logging
import re
from functools import lru_cache
from typing import List

logger = logging.getLogger(__name__)

MODEL_NAME = "facebook/bart-large-mnli"

# Curated candidate labels the zero-shot classifier scores the
# description against. Kept broad enough to cover most professional
# networking events while staying specific enough to be useful.
CANDIDATE_THEMES = [
    "Artificial Intelligence",
    "Technology",
    "Innovation",
    "Climate Change",
    "Sustainability",
    "Urban Planning",
    "Healthcare",
    "Finance",
    "Entrepreneurship",
    "Marketing",
    "Education",
    "Design",
    "Data Science",
    "Cybersecurity",
    "Biotechnology",
    "Robotics",
    "Policy & Government",
    "Community Building",
    "Career Development",
    "Diversity & Inclusion",
]

# Simple keyword fallback map: theme -> trigger words. Used only when
# the transformer pipeline cannot be loaded.
_KEYWORD_MAP = {
    "Artificial Intelligence": ["ai", "artificial intelligence", "machine learning", "ml", "llm", "neural"],
    "Technology": ["tech", "technology", "software", "digital", "startup", "hardware"],
    "Innovation": ["innovation", "innovate", "future", "disrupt"],
    "Climate Change": ["climate", "carbon", "emissions", "warming"],
    "Sustainability": ["sustainab", "renewable", "green energy", "eco"],
    "Urban Planning": ["urban", "city", "cities", "infrastructure", "transit"],
    "Healthcare": ["health", "medical", "medicine", "clinical", "hospital"],
    "Finance": ["finance", "financial", "banking", "investment", "fintech"],
    "Entrepreneurship": ["entrepreneur", "founder", "startup", "venture"],
    "Marketing": ["marketing", "brand", "advertis"],
    "Education": ["education", "learning", "school", "university", "teach"],
    "Design": ["design", "ux", "ui", "creative"],
    "Data Science": ["data science", "analytics", "big data", "statistics"],
    "Cybersecurity": ["security", "cyber", "privacy", "encryption"],
    "Biotechnology": ["biotech", "genom", "pharma", "biology"],
    "Robotics": ["robot", "automation", "drone"],
    "Policy & Government": ["policy", "government", "regulation", "public sector"],
    "Community Building": ["community", "network", "meetup", "social"],
    "Career Development": ["career", "job", "professional development", "mentorship"],
    "Diversity & Inclusion": ["diversity", "inclusion", "equity", "dei"],
}

DEFAULT_THEMES = ["Networking", "Professional Development", "Community Building"]


@lru_cache(maxsize=1)
def _load_classifier():
    """
    Lazily load and cache the zero-shot classification pipeline.

    Returns ``None`` if the required packages are missing or the
    model cannot be loaded, signaling the caller to use the keyword
    fallback instead. Cached with lru_cache so the (expensive) model
    load happens at most once per process.
    """
    try:
        from transformers import pipeline  # type: ignore

        logger.info("Loading zero-shot classification model: %s", MODEL_NAME)
        classifier = pipeline("zero-shot-classification", model=MODEL_NAME)
        return classifier
    except Exception as exc:  # noqa: BLE001 - any load failure should fall back, not crash
        logger.warning("Falling back to keyword-based theme extraction: %s", exc)
        return None


def _keyword_fallback(description: str, top_n: int = 3) -> List[str]:
    """Score candidate themes by simple keyword occurrence."""
    text = description.lower()
    scores = []
    for theme, keywords in _KEYWORD_MAP.items():
        hits = sum(1 for kw in keywords if re.search(re.escape(kw), text))
        if hits:
            scores.append((hits, theme))

    scores.sort(key=lambda pair: pair[0], reverse=True)
    themes = [theme for _, theme in scores[:top_n]]

    if not themes:
        return DEFAULT_THEMES[:top_n]
    while len(themes) < top_n:
        for fallback_theme in DEFAULT_THEMES:
            if fallback_theme not in themes:
                themes.append(fallback_theme)
                break
        else:
            break
    return themes[:top_n]


def extract_themes(description: str, top_n: int = 3) -> List[str]:
    """
    Extract the top ``top_n`` themes from an event description.

    Tries the Hugging Face zero-shot classifier first; falls back to
    keyword matching if the model is unavailable or errors at
    inference time.
    """
    if not description or not description.strip():
        raise ValueError("description must not be empty")

    classifier = _load_classifier()
    if classifier is not None:
        try:
            result = classifier(description, candidate_labels=CANDIDATE_THEMES, multi_label=True)
            labels = result.get("labels", [])
            themes = labels[:top_n] if labels else []
            if themes:
                return themes
        except Exception as exc:  # noqa: BLE001
            logger.warning("Zero-shot inference failed, using keyword fallback: %s", exc)

    return _keyword_fallback(description, top_n=top_n)
