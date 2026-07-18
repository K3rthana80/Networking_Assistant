import json
from pathlib import Path
from threading import Lock

lock = Lock()


def read_json(file_path: Path):

    if not file_path.exists():
        return []

    with lock:

        with open(file_path, "r", encoding="utf-8") as file:

            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []


def write_json(file_path: Path, data):

    with lock:

        with open(file_path, "w", encoding="utf-8") as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )