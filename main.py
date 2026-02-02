from pathlib import Path

import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

MODEL_PATH = Path(__file__).parent / "model.pkl"
MODEL_VERSION = "v1"

app = FastAPI(title="Milestone 1 Model Serving")

try:
    model = joblib.load(MODEL_PATH)
except Exception as exc:  # pragma: no cover - fail fast at startup
    raise RuntimeError(f"Failed to load model at {MODEL_PATH}") from exc


class PredictRequest(BaseModel):
    features: list[float] = Field(..., min_items=1)


class PredictResponse(BaseModel):
    prediction: float
    model_version: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest) -> PredictResponse:
    try:
        features = np.array(payload.features, dtype=float).reshape(1, -1)
        prediction = model.predict(features)[0]
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return PredictResponse(prediction=float(prediction), model_version=MODEL_VERSION)
