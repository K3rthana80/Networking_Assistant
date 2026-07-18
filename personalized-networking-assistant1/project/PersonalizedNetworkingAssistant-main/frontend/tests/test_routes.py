from tests.conftest import client

def test_health():

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json()["status"] == "Running"
    
def test_analyze_event():

    response = client.post(

        "/analyze-event",

        json={

            "event":"AI Conference"

        }

    )

    assert response.status_code == 200

    data = response.json()

    assert "themes" in data
    
def test_fact_check():

    response = client.post(

        "/fact-check",

        json={

            "topic":"Artificial Intelligence"

        }

    )

    assert response.status_code == 200

    assert response.json()["verified"] is True
    
def test_generate():

    response = client.post(

        "/generate-conversation",

        json={

            "event":"AI Conference",

            "interest":"Machine Learning"

        }

    )

    assert response.status_code == 200

    assert "conversation" in response.json()
    
def test_history():

    response = client.get("/history")

    assert response.status_code == 200

    assert isinstance(response.json(), list)
    
def test_feedback():

    response = client.post(

        "/feedback",

        json={

            "feedback":"Excellent"

        }

    )

    assert response.status_code == 200

    assert response.json()["message"] == "Feedback saved successfully."