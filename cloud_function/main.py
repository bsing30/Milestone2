from pathlib import Path

import joblib
import numpy as np

MODEL_PATH = Path(__file__).parent / "model.pkl"
MODEL_VERSION = "v1"

model = joblib.load(MODEL_PATH)


def predict(request):
    if request.method != "POST":
        return ("Only POST is supported", 405)

    request_json = request.get_json(silent=True) or {}
    features = request_json.get("features")
    if not isinstance(features, list) or not features:
        return ("'features' must be a non-empty list of numbers", 400)

    try:
        features_array = np.array(features, dtype=float).reshape(1, -1)
        prediction = model.predict(features_array)[0]
    except Exception as exc:
        return (f"Invalid input: {exc}", 400)

    return {"prediction": float(prediction), "model_version": MODEL_VERSION}
