import requests


url = "http://localhost:9003/predict"
wine = {
    "volatile acidity": 0.7,
    "citric acid": 0.0,
    "sulphates": 0.56,
    "alcohol": 9.4,
}


if __name__ == "__main__":
    response = requests.post(url, json=wine)
    print(response.json())
