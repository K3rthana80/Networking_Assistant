"""
Topic Generator Service
=========================

Generates exactly three short, professional networking conversation
starters from a set of detected event themes and the user's stated
interests.

Primary strategy: prompt GPT-2 Small to complete short question
templates. GPT-2 is a base language model (not instruction-tuned) so
outputs are seeded from hand-written prompt stems and aggressively
post-processed (truncated to one sentence, deduplicated, filtered for
minimum quality) to keep results usable.

If ``transformers``/``torch`` are unavailable, falls back to a
template engine that combines themes and interests into natural
questions. This keeps the feature fully functional offline and keeps
test runs fast and deterministic.
"""

from __future__ import annotations

import logging
import random
import re
from functools import lru_cache
from typing import List

logger = logging.getLogger(__name__)

MODEL_NAME = "gpt2"

_PROMPT_STEMS = [
    "A great conversation starter about {topic} at a networking event is: \"",
    "One thoughtful question to ask someone about {topic} is: \"",
    "At a professional networking event, a good icebreaker about {topic} is: \"",
]

# Template bank used both to seed GPT-2 prompts and as a full fallback
# when the model is unavailable. Keeps phrasing natural and varied.
_TEMPLATES = [
    "What inspired you to get involved in {topic}?",
    "What's the most exciting thing happening in {topic} right now?",
    "How did you first become interested in {topic}?",
    "What trends in {topic} are you keeping an eye on this year?",
    "What brought you to this event today?",
    "How do you see {topic} evolving over the next few years?",
    "What's a project related to {topic} you're proud of?",
    "What challenges are you tackling in {topic} at the moment?",
    "Who or what inspired your work in {topic}?",
    "What's one thing you wish more people understood about {topic}?",
    "What drew you to {event}?",
    "What are you hoping to learn or take away from {event}?",
]


@lru_cache(maxsize=1)
def _load_generator():
    """Lazily load and cache the GPT-2 text-generation pipeline."""
    try:
        from transformers import pipeline  # type: ignore

        logger.info("Loading text generation model: %s", MODEL_NAME)
        generator = pipeline("text-generation", model=MODEL_NAME)
        return generator
    except Exception as exc:  # noqa: BLE001
        logger.warning("Falling back to template-based conversation generation: %s", exc)
        return None


def _clean_line(text: str) -> str:
    """Trim a generated blob down to a single, well-formed sentence."""
    text = text.strip().strip('"')
    # Cut at the first sentence-ending punctuation.
    match = re.search(r"[.?!]", text)
    if match:
        text = text[: match.end()]
    text = re.sub(r"\s+", " ", text).strip()
    if text and text[-1] not in ".?!":
        text += "?"
    if text:
        text = text[0].upper() + text[1:]
    return text


def _is_valid_line(text: str) -> bool:
    words = text.split()
    return 4 <= len(words) <= 25


def _template_fallback(themes: List[str], interests: List[str], count: int) -> List[str]:
    topics = list(dict.fromkeys(themes + interests)) or ["this field"]
    rng = random.Random(42)  # deterministic for reproducible tests
    rng.shuffle(topics)

    pool = list(_TEMPLATES)
    rng.shuffle(pool)

    suggestions: List[str] = []
    topic_cycle_index = 0
    for template in pool:
        if len(suggestions) >= count:
            break
        topic = topics[topic_cycle_index % len(topics)]
        topic_cycle_index += 1
        line = template.format(topic=topic, event="this event")
        line = _clean_line(line)
        if line and line not in suggestions:
            suggestions.append(line)

    return suggestions[:count]


def generate_conversation_starters(
    themes: List[str],
    interests: List[str],
    count: int = 3,
) -> List[str]:
    """
    Generate exactly ``count`` unique, professional networking
    conversation starters based on event themes and user interests.
    """
    if not themes and not interests:
        raise ValueError("at least one theme or interest is required")

    topics = list(dict.fromkeys(themes + interests))
    generator = _load_generator()

    suggestions: List[str] = []

    if generator is not None:
        try:
            rng = random.Random(7)
            attempts = 0
            max_attempts = count * 4
            while len(suggestions) < count and attempts < max_attempts:
                topic = topics[attempts % len(topics)]
                stem = rng.choice(_PROMPT_STEMS).format(topic=topic)
                attempts += 1
                output = generator(
                    stem,
                    max_new_tokens=25,
                    num_return_sequences=1,
                    do_sample=True,
                    top_p=0.9,
                    temperature=0.8,
                    pad_token_id=50256,
                )
                generated_text = output[0]["generated_text"][len(stem):]
                line = _clean_line(generated_text)
                if _is_valid_line(line) and line not in suggestions:
                    suggestions.append(line)
        except Exception as exc:  # noqa: BLE001
            logger.warning("GPT-2 generation failed, using template fallback: %s", exc)
            suggestions = []

    if len(suggestions) < count:
        remaining = count - len(suggestions)
        fallback_lines = _template_fallback(themes, interests, count=count + remaining)
        for line in fallback_lines:
            if len(suggestions) >= count:
                break
            if line not in suggestions:
                suggestions.append(line)

    # Final dedupe + hard cap, in case both sources contributed.
    deduped = list(dict.fromkeys(suggestions))
    return deduped[:count]
