from fastapi.testclient import TestClient
from sentiment_api import app

client = TestClient(app)

def test_predict_sentiment():
    response = client.post("/predict", json={"text": "I love this!"})
    assert response.status_code == 200

    data = response.json()
    assert "model" in data
    assert data["model"] == "vader"
    assert "compound" in data
    assert isinstance(data["compound"], float)
    assert -1.0 <= data["compound"] <= 1.0

def test_negative_sentiment():
    response = client.post("/predict", json={"text": "This is awful!"})
    data = response.json()
    assert data["compound"] < 0

def test_neutral_sentiment():
    response = client.post("/predict", json={"text": "This is ok."})
    data = response.json()
    assert -0.1 <= data["compound"] <= 0.1

def test_missing_text_field():
    response = client.post("/predict", json={})
    assert response.status_code == 422  # Unprocessable Entity



