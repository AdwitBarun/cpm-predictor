"""
SHAP explainer for CPM prediction models.

Provides local explanations for why CPM is high / low.
"""

from typing import List, Tuple
import shap
import pandas as pd


def explain_prediction(model, X: pd.DataFrame, top_k: int = 10):
    """
    Compute SHAP values for a single prediction.

    Parameters
    ----------
    model : trained tree-based model (use p50)
    X : pd.DataFrame
        Single-row input
    top_k : int
        Number of top features

    Returns
    -------
    List[Tuple[str, float]]
    """

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

    return [(str(k), float(v)) for k, v in result]


def format_shap_for_llm(
    shap_summary: List[Tuple[str, float]]
):
    """
    Convert SHAP output into LLM-friendly structure.
    """
    formatted = []

    for feature, impact in shap_summary:
        formatted.append({
            "feature": feature,
            "impact": round(impact, 3),
            "direction": "increases" if impact > 0 else "decreases",
        })

    return formatted
