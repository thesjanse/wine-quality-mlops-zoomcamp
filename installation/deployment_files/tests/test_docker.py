import requests


def test_service():
    """Integration test for the prediction endpoint."""
    request = {
        "volatile acidity": 0.7,
        "citric acid": 0.0,
        "sulphates": 0.56,
        "alcohol": 9.4,
    }
    url = "http://localhost:9003/predict"

    expected = {
        "model": "sk-rfc-model",
        "quality": 5
    }

    actual = requests.post(url, json=request, timeout=5).json()
    assert actual == expected
