import os
import joblib
from typing import Dict, Any

from ..features.preprocess import preprocess
from .shap_explainer import explain_prediction
from ..llm.gemini_client import gemini_range


# -------------------------------------------------
# Load trained artifacts
# -------------------------------------------------
ARTIFACT_DIR = os.path.join(os.path.dirname(__file__), "..", "artifacts")

MODELS = joblib.load(os.path.join(ARTIFACT_DIR, "cpm_quantile_models.pkl"))
FEATURE_COLUMNS = joblib.load(os.path.join(ARTIFACT_DIR, "feature_columns.pkl"))


# -------------------------------------------------
# Main prediction function (USED EVERYWHERE)
# -------------------------------------------------
def predict_cpm_range(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predict CPM range using:
    - Quantile ML models (P10 / P50 / P90)
    - SHAP explanations
    - Gemini LLM enhancement
    - Final blended CPM range
    """

    # -----------------------------
    # 1. Preprocess input
    # -----------------------------
    X = preprocess(input_data, FEATURE_COLUMNS)

    # -----------------------------
    # 2. Quantile predictions
    # -----------------------------
    p10 = float(MODELS["p10"].predict(X)[0])
    p50 = float(MODELS["p50"].predict(X)[0])
    p90 = float(MODELS["p90"].predict(X)[0])

    # -----------------------------
    # 3. SHAP explanation (median model)
    # -----------------------------
    shap_summary = explain_prediction(MODELS["p50"], X)

    # -----------------------------
    # 4. Gemini LLM range adjustment
    # -----------------------------
    llm_range = gemini_range(
        features=input_data,
        historical_range=(p10, p50, p90),
        shap_summary=shap_summary,
    )

    # -----------------------------
    # 5. Blend ML + LLM
    # -----------------------------
    final_low = 0.65 * p10 + 0.35 * llm_range["low"]
    final_high = 0.65 * p90 + 0.35 * llm_range["high"]

    return {
        "historical_range": {
            "low": round(p10, 2),
            "mid": round(p50, 2),
            "high": round(p90, 2),
        },
        "llm_range": llm_range,
        "final_range": {
            "low": round(final_low, 2),
            "high": round(final_high, 2),
        },
        "shap_top_features": shap_summary,
    }
