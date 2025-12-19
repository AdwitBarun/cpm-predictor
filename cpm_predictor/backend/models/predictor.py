import numpy as np
from typing import Dict, Any

from cpm_predictor.backend.features.preprocess import preprocess_features
from cpm_predictor.backend.models.shap_explainer import explain_prediction
from cpm_predictor.backend.llm.gemini_client import gemini_range


def predict_cpm_range(
    models,
    feature_columns,
    ml_features: Dict[str, Any],
    llm_features: Dict[str, Any],
) -> Dict[str, Any]:
    """
    End-to-end CPM prediction (₹ CPM).
    """

    # -----------------------------
    # 1. ML preprocessing
    # -----------------------------
    X = preprocess_features(ml_features, feature_columns)

    # -----------------------------
    # 2. Quantile predictions (LOG)
    # -----------------------------
    p10_log = models[0.1].predict(X)[0]
    p50_log = models[0.5].predict(X)[0]
    p90_log = models[0.9].predict(X)[0]

    # -----------------------------
    # 3. Back-transform → ₹ CPM
    # -----------------------------
    p10 = float(np.expm1(p10_log))
    p50 = float(np.expm1(p50_log))
    p90 = float(np.expm1(p90_log))

    # -----------------------------
    # 4. SHAP explanation
    # -----------------------------
    shap_summary = explain_prediction(models[0.5], X)

    # -----------------------------
    # 5. LLM adjustment
    # -----------------------------
    llm_range = gemini_range(
        features=llm_features,
        historical_range=(p10, p50, p90),
        shap_summary=shap_summary,
    )

    # -----------------------------
    # 6. Final blend
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
