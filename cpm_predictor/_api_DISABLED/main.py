from fastapi import FastAPI
import joblib
import pandas as pd
import numpy as np
from experiments_old.features.preprocess import preprocess
from backend.models.confidence import confidence_score
from experiments_old.explainability.shap_explain import explain_instance
from backend.models.recommendations import suggest_actions
from experiments_old.llm.gemini_decision import get_decision

app = FastAPI()

models = joblib.load("model/segmented_models.pkl")
features = joblib.load("model/feature_columns.pkl")

@app.post("/predict")
def predict(payload: dict):
    segment = payload["Video Ad Format"]
    client_cpm = payload["client_cpm"]

    df = pd.DataFrame([payload])
    X, _ = preprocess(df)
    X = X.reindex(columns=features, fill_value=0)

    seg_models = models.get(segment)
    if not seg_models:
        return {"error": "No model for this segment"}

    preds = {q: np.expm1(m.predict(X)[0]) for q, m in seg_models.items()}

    conf = confidence_score(preds[0.1], preds[0.5], preds[0.9])

    shap_vals = explain_instance(seg_models[0.5], X)
    top_feats = sorted(
        zip(X.columns, shap_vals[0]),
        key=lambda x: abs(x[1]),
        reverse=True
    )[:5]

    return {
        "predicted_range": preds,
        "confidence": conf,
        "drivers": top_feats,
        "recommendations": suggest_actions(top_feats),
        "decision": get_decision(
            (preds[0.1], preds[0.5], preds[0.9]),
            top_feats,
            client_cpm
        )
    }
