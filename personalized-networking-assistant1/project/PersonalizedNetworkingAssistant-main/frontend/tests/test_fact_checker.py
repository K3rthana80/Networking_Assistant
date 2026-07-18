from backend.services.fact_checker import verify_topic


def test_verify_topic():

    result = verify_topic("Artificial Intelligence")

    assert result["verified"] is True

    assert "summary" in result
    
def test_invalid_topic():

    result = verify_topic("asdasdxyz123")

    assert result["verified"] is False