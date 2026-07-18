import requests

BASE_URL = "http://127.0.0.1:8000"


def generate_conversation(event, interest):

    response = requests.post(

        f"{BASE_URL}/generate-conversation",

        json={

            "event": event,

            "interest": interest

        }

    )

    response.raise_for_status()

    return response.json()


def get_history():

    response = requests.get(

        f"{BASE_URL}/history"

    )

    response.raise_for_status()

    return response.json()


def send_feedback(text):

    response = requests.post(

        f"{BASE_URL}/feedback",

        json={

            "feedback": text

        }

    )

    response.raise_for_status()

    return response.json()