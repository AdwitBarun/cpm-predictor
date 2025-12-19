import os
import joblib
import numpy as np
from typing import Dict, Any

from cpm_predictor.backend.features.preprocess import preprocess_features
from cpm_predictor.backend.features.geo_decoder import (
    encode_geography,
    decode_geography,
)
from cpm_predictor.backend.models.shap_explainer import explain_prediction
from cpm_predictor.backend.llm.gemini_client import gemini_range

ARTIFACT_DIR = os.path.join(os.path.dirname(__file__), "..", "artifacts")

MODELS = joblib.load(os.path.join(ARTIFACT_DIR, "cpm_quantile_models.pkl"))
FEATURE_COLUMNS = joblib.load(os.path.join(ARTIFACT_DIR, "feature_columns.pkl"))


def predict_cpm_range(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    End-to-end CPM prediction (₹ CPM, not log).
    """

    # -----------------------------
    # 1. Geography handling
    # -----------------------------
    geo_names = payload.get("Geography_Targeting_Include")
    geo_codes = encode_geography(geo_names)

    ml_features = payload.copy()
    ml_features["Geography Targeting - Include"] = geo_codes

    llm_features = payload.copy()
    llm_features["decoded_geo"] = decode_geography(geo_codes)

    # -----------------------------
    # 2. ML preprocessing
    # -----------------------------
    X = preprocess_features(ml_features, FEATURE_COLUMNS)

    # -----------------------------
    # 3. Quantile predictions (LOG)
    # -----------------------------
    p10_log = MODELS[0.1].predict(X)[0]
    p50_log = MODELS[0.5].predict(X)[0]
    p90_log = MODELS[0.9].predict(X)[0]

    # -----------------------------
    # 4. Back-transform → ₹ CPM
    # -----------------------------
    p10 = float(np.expm1(p10_log))
    p50 = float(np.expm1(p50_log))
    p90 = float(np.expm1(p90_log))

    # -----------------------------
    # 5. SHAP
    # -----------------------------
    shap_summary = explain_prediction(MODELS[0.5], X)

    # -----------------------------
    # 6. LLM adjustment
    # -----------------------------
    llm_range = gemini_range(
        features=llm_features,
        historical_range=(p10, p50, p90),
        shap_summary=shap_summary,
    )

    # -----------------------------
    # 7. Final blend
    # -----------------------------
    final_low = 0.85 * p10 + 0.15 * llm_range["low"]
    final_high = 0.85 * p90 + 0.15 * llm_range["high"]

    return {
        "historical": {
            "p10": round(p10, 2),
            "p50": round(p50, 2),
            "p90": round(p90, 2),
        },
        "llm": llm_range,
        "final": {
            "low": round(final_low, 2),
            "high": round(final_high, 2),
        },
        "shap_top_features": shap_summary,
    }
