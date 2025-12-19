from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

import joblib
import os

from cpm_predictor.backend.features.preprocess import preprocess
from cpm_predictor.backend.models.shap_explainer import explain_prediction
from cpm_predictor.backend.llm.gemini_client import gemini_range

# -------------------------------------------------
# App
# -------------------------------------------------
app = FastAPI(title="CPM Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# Load artifacts once
# -------------------------------------------------
BASE_DIR = os.path.dirname(__file__)
ARTIFACT_DIR = os.path.join(BASE_DIR, "..", "artifacts")

MODELS = joblib.load(os.path.join(ARTIFACT_DIR, "cpm_quantile_models_v1.pkl"))
FEATURE_COLUMNS = joblib.load(os.path.join(ARTIFACT_DIR, "feature_columns_v1.pkl"))

# -------------------------------------------------
# Health check
# -------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

# -------------------------------------------------
# CPM Prediction Endpoint
# -------------------------------------------------
@app.post("/predict")
def predict_cpm(input_data: Dict[str, Any]):

    X = preprocess(input_data, FEATURE_COLUMNS)

    p10 = float(MODELS[0.1].predict(X)[0])
    p50 = float(MODELS[0.5].predict(X)[0])
    p90 = float(MODELS[0.9].predict(X)[0])

    shap_summary = explain_prediction(MODELS[0.5], X)

    llm_range = gemini_range(
        features=input_data,
        historical_range=(p10, p50, p90),
        shap_summary=shap_summary,
    )

    final_low = 0.85 * p10 + 0.15 * llm_range["low"]
    final_high = 0.85 * p90 + 0.15 * llm_range["high"]

    return {
        "historical": {"p10": p10, "p50": p50, "p90": p90},
        "llm": llm_range,
        "final": {
            "low": round(final_low, 2),
            "high": round(final_high, 2),
        },
        "shap_top_features": shap_summary,
    }
