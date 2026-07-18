from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATABASE_DIR = BASE_DIR / "database"

HISTORY_FILE = DATABASE_DIR / "history.json"

FEEDBACK_FILE = DATABASE_DIR / "feedback.json"

APP_NAME = "Personalized Networking Assistant"

APP_VERSION = "1.0.0"