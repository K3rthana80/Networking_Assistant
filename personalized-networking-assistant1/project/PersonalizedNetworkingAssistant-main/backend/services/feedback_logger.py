from datetime import datetime

from backend.config import FEEDBACK_FILE
from backend.utils.json_storage import (
    read_json,
    write_json
)


def save_feedback(feedback):

    data = read_json(FEEDBACK_FILE)

    data.append({

        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        "feedback": feedback

    })

    write_json(FEEDBACK_FILE, data)


def get_feedback():

    return read_json(FEEDBACK_FILE)