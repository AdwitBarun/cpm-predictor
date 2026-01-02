# backend/models/predictor.py

from typing import Dict, Any
from cpm_predictor.backend.models.loader import load_models
from cpm_predictor.backend.features.preprocess import preprocess_input
from cpm_predictor.backend.models.shap_explainer import explain_prediction


def predict_cpm_range(
    raw_input: Dict[str, Any],
    return_shap: bool = True,
) -> Dict[str, Any]:

    models, feature_columns = load_models()
    city_tier_lookup = models.get("city_tier_lookup")

   

    required_keys = {"p10", "p50", "p90", "q_hat"}
    missing = required_keys - set(models.keys())
    if missing:
        raise KeyError(f"Model bundle missing keys: {missing}")

    model_p10 = models.get("p10")
    model_p50 = models.get("p50")
    model_p90 = models.get("p90")
    q_hat = models.get("q_hat")


    # -----------------------------
    # Preprocess
    # -----------------------------
    X_model, X_similarity, _, llm_payload = preprocess_input(
            raw_input=raw_input,
            feature_columns=feature_columns,
            city_tier_lookup=city_tier_lookup   
        )
    print("🔥 X_MODEL DTYPES")
    print(X_model.dtypes)

    print("🔥 X_MODEL SAMPLE")
    print(X_model.iloc[0].to_dict())

    # -----------------------------
    # Quantile predictions
    # -----------------------------
    p10 = float(model_p10.predict(X_model)[0])
    p50 = float(model_p50.predict(X_model)[0])
    p90 = float(model_p90.predict(X_model)[0])

    # -----------------------------
    # Conformal adjustment
    # -----------------------------
    cpm_low = max(0.0, p10 - q_hat)
    cpm_high = p90 + q_hat

    # -----------------------------
    # SHAP
    # -----------------------------
    shap_summary = []
    if return_shap:
        shap_summary = explain_prediction(model_p50, X_model, top_k=5)

    return {
        "model_range": {
            "p10": round(p10, 2),
            "p50": round(p50, 2),
            "p90": round(p90, 2),
        },
        "conformal_range": {
            "low": round(cpm_low, 2),
            "high": round(cpm_high, 2),
            "coverage_target": 0.90,
        },
        "shap_top_features": shap_summary,
        "X_similarity": X_similarity,
        "llm_payload": llm_payload,
    }
