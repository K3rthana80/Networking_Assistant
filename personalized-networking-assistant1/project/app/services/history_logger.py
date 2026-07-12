"""
History Logger Service
=========================

Persists every generated conversation (event, interests, themes,
suggestions) to a local JSON file, newest entries returned first.

No database is used, per the project spec. Writes are done atomically
(write to a temp file, then replace) to avoid corrupting the JSON file
if the process is interrupted mid-write.
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

# Project root is three levels up from this file: app/services/ -> app/ -> project/
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
HISTORY_FILE = Path(os.environ.get("HISTORY_FILE_PATH", PROJECT_ROOT / "history.json"))

_lock = threading.Lock()


def _ensure_file() -> None:
    if not HISTORY_FILE.exists():
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        HISTORY_FILE.write_text("[]", encoding="utf-8")


def _read_all() -> List[Dict[str, Any]]:
    _ensure_file()
    try:
        raw = HISTORY_FILE.read_text(encoding="utf-8").strip()
        if not raw:
            return []
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError) as exc:
        logger.error("Failed to read history file, returning empty history: %s", exc)
        return []


def _write_all(entries: List[Dict[str, Any]]) -> None:
    _ensure_file()
    directory = HISTORY_FILE.parent
    fd, tmp_path = tempfile.mkstemp(dir=directory, prefix=".history_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tmp_file:
            json.dump(entries, tmp_file, indent=2, default=str)
        os.replace(tmp_path, HISTORY_FILE)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def log_conversation(
    event: str,
    interests: List[str],
    themes: List[str],
    suggestions: List[str],
) -> Dict[str, Any]:
    """Append a new conversation record and return it."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "interests": interests,
        "themes": themes,
        "suggestions": suggestions,
    }
    with _lock:
        entries = _read_all()
        entries.append(entry)
        _write_all(entries)
    return entry


def get_history() -> List[Dict[str, Any]]:
    """Return all history entries, newest first."""
    with _lock:
        entries = _read_all()
    return list(reversed(entries))
