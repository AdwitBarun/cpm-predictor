from fastapi import APIRouter, HTTPException
from cpm_predictor.backend.models.loader import load_models
from cpm_predictor.backend.features.preprocess import preprocess
from cpm_predictor.backend.llm.gemini_client import gemini_range

router = APIRouter()


@router.post("/api/predict")
def predict(payload: dict):
    try:
        MODELS, FEATURE_COLUMNS = load_models()

        X = preprocess(payload, FEATURE_COLUMNS)

        p10 = float(MODELS[0.1].predict(X)[0])
        p50 = float(MODELS[0.5].predict(X)[0])
        p90 = float(MODELS[0.9].predict(X)[0])

        llm = gemini_range(
            features=payload,
            historical_range=(p10, p50, p90),
            shap_summary=[]
        )

        return {
            "historical_range": {"low": p10, "mid": p50, "high": p90},
            "llm_range": llm,
            "final_range": {
                "low": round(0.65 * p10 + 0.35 * llm["low"], 2),
                "high": round(0.65 * p90 + 0.35 * llm["high"], 2),
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
