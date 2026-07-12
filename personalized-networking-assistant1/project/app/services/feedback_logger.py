"""
Feedback Logger Service
==========================

Persists user feedback (like/dislike) on generated conversation
starters to a local JSON file, following the same atomic-write
pattern as ``history_logger``.
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FEEDBACK_FILE = Path(os.environ.get("FEEDBACK_FILE_PATH", PROJECT_ROOT / "feedback.json"))

_lock = threading.Lock()


def _ensure_file() -> None:
    if not FEEDBACK_FILE.exists():
        FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
        FEEDBACK_FILE.write_text("[]", encoding="utf-8")


def _read_all() -> List[Dict[str, Any]]:
    _ensure_file()
    try:
        raw = FEEDBACK_FILE.read_text(encoding="utf-8").strip()
        if not raw:
            return []
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError) as exc:
        logger.error("Failed to read feedback file, returning empty feedback: %s", exc)
        return []


def _write_all(entries: List[Dict[str, Any]]) -> None:
    _ensure_file()
    directory = FEEDBACK_FILE.parent
    fd, tmp_path = tempfile.mkstemp(dir=directory, prefix=".feedback_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tmp_file:
            json.dump(entries, tmp_file, indent=2, default=str)
        os.replace(tmp_path, FEEDBACK_FILE)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def log_feedback(suggestion: str, action: str) -> Dict[str, Any]:
    """Append a new feedback record and return it."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "suggestion": suggestion,
        "action": action,
    }
    with _lock:
        entries = _read_all()
        entries.append(entry)
        _write_all(entries)
    return entry


def get_feedback() -> List[Dict[str, Any]]:
    """Return all feedback entries, newest first."""
    with _lock:
        entries = _read_all()
    return list(reversed(entries))
