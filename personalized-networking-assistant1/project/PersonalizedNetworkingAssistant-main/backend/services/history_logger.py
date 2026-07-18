from datetime import datetime

from backend.config import HISTORY_FILE
from backend.utils.json_storage import (
    read_json,
    write_json
)


def save_history(event,
                 interest,
                 themes,
                 conversation):

    history = read_json(HISTORY_FILE)

    history.append({

        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        "event": event,

        "interest": interest,

        "themes": themes,

        "conversation": conversation

    })

    write_json(HISTORY_FILE, history)


def get_history():

    return read_json(HISTORY_FILE)