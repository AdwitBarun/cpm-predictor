"""
SHAP explainer for CPM prediction models.

This module provides local (per-prediction) SHAP explanations
to understand which features are driving the CPM prediction.
"""

from typing import List, Tuple
import numpy as np
import pandas as pd
import shap


def explain_prediction(
    model,
    X: pd.DataFrame,
    top_k: int = 5,
) -> List[Tuple[str, float]]:
    """
    Generate SHAP-based feature importance for a single prediction.

    Args:
        model:
            Trained tree-based model (XGBoost / LightGBM / CatBoost).
        X:
            Preprocessed input features as a pandas DataFrame
            with shape (1, n_features).
        top_k:
            Number of top contributing features to return.

    Returns:
        A list of (feature_name, importance) tuples sorted
        by absolute SHAP importance (descending).

    Example:
        >>> shap_summary = explain_prediction(model, X)
        >>> print(shap_summary)
        [
            ('Inventory Mode_Limited', 1.23),
            ('TG_F25-44', 0.87),
            ('Planned Budget', 0.41),
            ...
        ]
    """

    # ----------------------------
    # Input validation
    # ----------------------------
    if not isinstance(X, pd.DataFrame):
        raise ValueError("X must be a pandas DataFrame")

    if X.shape[0] != 1:
        raise ValueError(
            f"SHAP explanation expects a single-row DataFrame, got {X.shape[0]} rows"
        )

    # ----------------------------
    # Initialize SHAP explainer
    # ----------------------------
    # TreeExplainer is fast and stable for tree-based models
    explainer = shap.TreeExplainer(model)

    # ----------------------------
    # Compute SHAP values
    # ----------------------------
    shap_values = explainer.shap_values(X)

    # Some models return a list (e.g., multi-output); handle safely
    if isinstance(shap_values, list):
        shap_values = shap_values[0]

    # Extract values for the single row
    shap_vals = shap_values[0]

    feature_names = X.columns.tolist()

    # ----------------------------
    # Compute absolute importance
    # ----------------------------
    feature_importance = sorted(
        zip(feature_names, np.abs(shap_vals)),
        key=lambda x: x[1],
        reverse=True,
    )

    return feature_importance[:top_k]


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
