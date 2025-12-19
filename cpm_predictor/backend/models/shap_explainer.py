"""
SHAP explainer for CPM prediction models.

This module provides local (per-prediction) SHAP explanations
to understand which features are driving the CPM prediction.
"""

from typing import List, Tuple
import numpy as np
import pandas as pd
import shap


def explain_prediction(model, X, top_k=5):
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    if isinstance(shap_values, list):
        shap_values = shap_values[0]

    vals = shap_values[0]
    cols = X.columns.tolist()

    result = sorted(
        zip(cols, vals),
        key=lambda x: abs(x[1]),
        reverse=True
    )[:top_k]

    # 🔥 FORCE python floats
    return [(str(k), float(v)) for k, v in result]

# -------------------------------------------------
# Optional utility: pretty format for LLM / logs
# -------------------------------------------------

def format_shap_for_llm(
    shap_summary: List[Tuple[str, float]]
) -> List[dict]:
    """
    Convert SHAP output into a JSON-friendly format for LLMs.

    Args:
        shap_summary:
            Output from explain_prediction()

    Returns:
        List of dicts with feature, impact, and direction.
    """
    formatted = []

    for feature, impact in shap_summary:
        formatted.append(
            {
                "feature": str(feature),
                "impact": round(float(impact), 3),
                "direction": "increases" if impact > 0 else "decreases",
            }
        )

    return formatted


# -------------------------------------------------
# Example usage (for local testing only)
# -------------------------------------------------

if __name__ == "__main__":
    import joblib

    print("Running SHAP explainer test...")

    # Dummy example (replace with real artifacts if testing manually)
    try:
        model = joblib.load(
            "cpm_predictor/backend/artifacts/cpm_quantile_models.pkl"
        )["p50"]

        X_sample = pd.DataFrame(
            {
                "Planned Budget": [400000],
                "Planned Impressions": [2000000],
                "campaign_duration_days": [60],
            }
        )

        explanation = explain_prediction(model, X_sample)
        formatted = format_shap_for_llm(explanation)

        print("Top SHAP features:")
        for item in formatted:
            print(item)

    except Exception as e:
        print(f"SHAP test failed: {e}")
