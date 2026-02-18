"""Minimal ML inference service - Iris classifier API."""
import json
import os
from pathlib import Path

import pickle
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load model at startup
MODEL_PATH = Path(__file__).parent / "model.pkl"
model = None


def load_model():
    global model
    if MODEL_PATH.exists():
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
    return model is not None


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200


@app.route("/predict", methods=["POST"])
def predict():
    """
    Prediction endpoint. Expects JSON: {"features": [[5.1, 3.5, 1.4, 0.2], ...]}
    Returns: {"predictions": [0, 1, ...], "class_names": ["setosa", ...]}
    """
    global model
    if model is None and not load_model():
        return jsonify({"error": "Model not loaded"}), 503

    try:
        data = request.get_json()
        if not data or "features" not in data:
            return jsonify({"error": "Missing 'features' key in JSON body"}), 400

        features = data["features"]
        if not isinstance(features, list):
            return jsonify({"error": "features must be a list of arrays"}), 400

        # Handle single prediction
        if isinstance(features[0], (int, float)):
            features = [features]

        predictions = model.predict(features).tolist()
        class_names = ["setosa", "versicolor", "virginica"]
        labels = [class_names[p] for p in predictions]

        return jsonify({"predictions": predictions, "labels": labels}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    load_model()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
