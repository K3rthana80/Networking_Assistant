from backend.services.event_analyzer import analyze_event


def test_analyze_event():

    result = analyze_event(
        "AI Conference about Healthcare and Machine Learning"
    )

    assert isinstance(result, list)

    assert len(result) > 0

    assert "theme" in result[0]

    assert "confidence" in result[0]