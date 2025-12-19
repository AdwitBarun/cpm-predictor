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

USD_TO_INR = 83.0  

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

    # -----------------------
    # ML prediction (USD)
    # -----------------------
    X = preprocess(input_data, FEATURE_COLUMNS)

    p10_usd = float(MODELS[0.1].predict(X)[0])
    p50_usd = float(MODELS[0.5].predict(X)[0])
    p90_usd = float(MODELS[0.9].predict(X)[0])

    shap_summary = explain_prediction(MODELS[0.5], X)

    llm_range = gemini_range(
        features=input_data,
        historical_range=(p10_usd, p50_usd, p90_usd),
        shap_summary=shap_summary,
    )

    final_low_usd = 0.85 * p10_usd + 0.15 * llm_range["low"]
    final_high_usd = 0.85 * p90_usd + 0.15 * llm_range["high"]

    # -----------------------
    # Convert to INR (ONLY HERE)
    # -----------------------
    return {
        "currency": "INR",
        "exchange_rate": USD_TO_INR,

        "historical": {
            "p10": round(p10_usd * USD_TO_INR, 2),
            "p50": round(p50_usd * USD_TO_INR, 2),
            "p90": round(p90_usd * USD_TO_INR, 2),
        },

        "llm": {
            "low": round(llm_range["low"] * USD_TO_INR, 2),
            "high": round(llm_range["high"] * USD_TO_INR, 2),
            "explanation": llm_range["explanation"],
            "key_factors": llm_range.get("key_factors", []),
        },

        "final": {
            "low": round(final_low_usd * USD_TO_INR, 2),
            "high": round(final_high_usd * USD_TO_INR, 2),
        },

        "shap_top_features": shap_summary,
    }
