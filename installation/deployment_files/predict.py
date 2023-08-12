import os
import mlflow

from flask import Flask, request, jsonify


MODEL_NAME = "sk-rfc-model"

mlflow.set_tracking_uri(os.getenv("MLFLOW_SITE_URL"))
model = mlflow.pyfunc.load_model(model_uri=F"models:/{MODEL_NAME}/latest")

app = Flask("red-wine-quality-prediction")


def predict(features):
    """Calls model prediction based on the json features."""
    return int(model.predict(features)[0])


@app.route("/predict", methods=["POST"])
def predict_endpoint():
    """Creates a flask endpoint for prediction.
    Returns prediction as a json."""
    wine = request.get_json()
    prediction = predict(wine)
    result = {
        "quality": prediction,
        "model": MODEL_NAME
    }
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9003)
