from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import numpy as np
import joblib
import os

from cpm_predictor.backend.features.preprocess import preprocess_features
from cpm_predictor.backend.models.shap_explainer import explain_prediction
from cpm_predictor.backend.llm.gemini_client import gemini_range

# -------------------------------------------------
# App
# -------------------------------------------------
app = FastAPI(title="CPM Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# Load artifacts
# -------------------------------------------------
BASE_DIR = os.path.dirname(__file__)
ARTIFACT_DIR = os.path.join(BASE_DIR, "..", "artifacts")

MODELS = joblib.load(os.path.join(ARTIFACT_DIR, "cpm_quantile_models.pkl"))
FEATURE_COLUMNS = joblib.load(os.path.join(ARTIFACT_DIR, "feature_columns.pkl"))

# -------------------------------------------------
# Helpers
# -------------------------------------------------
def inverse_log(x: float) -> float:
    """Convert log-CPM → CPM"""
    return float(np.exp(x))

# -------------------------------------------------
# Endpoint
# -------------------------------------------------
@app.post("/predict")
def predict_cpm(input_data: Dict[str, Any]):

    X = preprocess_features(input_data, FEATURE_COLUMNS)

    # ---- LOG CPM (model output)
    p10_log = float(MODELS[0.1].predict(X)[0])
    p50_log = float(MODELS[0.5].predict(X)[0])
    p90_log = float(MODELS[0.9].predict(X)[0])

    shap_summary = explain_prediction(MODELS[0.5], X)

    llm_range_log = gemini_range(
        features=input_data,
        historical_range=(p10_log, p50_log, p90_log),
        shap_summary=shap_summary,
    )

    # ---- Blend in LOG space (important!)
    final_low_log = 0.85 * p10_log + 0.15 * llm_range_log["low"]
    final_high_log = 0.85 * p90_log + 0.15 * llm_range_log["high"]

    # ---- Convert to REAL CPM
    return {
        "scale": "linear_cpm",
        "transform": "exp",

        "historical": {
            "p10": round(inverse_log(p10_log), 2),
            "p50": round(inverse_log(p50_log), 2),
            "p90": round(inverse_log(p90_log), 2),
        },

        "llm": {
            "low": round(inverse_log(llm_range_log["low"]), 2),
            "high": round(inverse_log(llm_range_log["high"]), 2),
            "explanation": llm_range_log["explanation"],
            "key_factors": llm_range_log.get("key_factors", []),
        },

        "final": {
            "low": round(inverse_log(final_low_log), 2),
            "high": round(inverse_log(final_high_log), 2),
        },

        "shap_top_features": shap_summary,
    }
