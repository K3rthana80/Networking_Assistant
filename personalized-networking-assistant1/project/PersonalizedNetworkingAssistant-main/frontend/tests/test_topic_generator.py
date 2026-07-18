from backend.services.topic_generator import generate_conversation


def test_generate_conversation():

    themes = [

        {

            "theme": "Artificial Intelligence",

            "confidence": 0.95

        }

    ]

    result = generate_conversation(

        "AI Conference",

        "Machine Learning",

        themes,

        "Artificial Intelligence is the simulation of human intelligence."

    )

    assert isinstance(result, str)

    assert len(result) > 10