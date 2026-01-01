# backend/api/predict.py

from fastapi import APIRouter, HTTPException
from cpm_predictor.backend.models.predictor import predict_cpm_range
from cpm_predictor.backend.models.similiarity import find_similar_campaigns
from cpm_predictor.backend.models.historical_store import get_historical_data
from cpm_predictor.backend.llm.orchestrator import run_llm_reasoning
from cpm_predictor.backend.app.schemas import CampaignInput

router = APIRouter()


@router.post("/predict")
def predict_cpm(payload: CampaignInput):
    try:
        raw_input = payload.dict()

        # -----------------------------
        # 1. ML prediction
        # -----------------------------
        pred = predict_cpm_range(raw_input)

        # -----------------------------
        # 2. Load historical data
        # -----------------------------
        X_hist, meta_df = get_historical_data()

        # -----------------------------
        # 3. Similarity search
        # -----------------------------
        similar = find_similar_campaigns(
            X_new=pred["X_similarity"],
            X_hist=X_hist,
            meta_df=meta_df,
            k=5,
        )

        # -----------------------------
        # 4. LLM reasoning
        # -----------------------------
        llm_result = run_llm_reasoning(
            raw_input=raw_input,
            model_output=pred,
            similar_campaigns=similar,
        )

        # -----------------------------
        # 5. Final response
        # -----------------------------
        return {
            "model_range": pred["model_range"],
            "conformal_range": pred["conformal_range"],
            "shap_top_features": pred["shap_top_features"],
            "similar_campaigns": similar,
            "llm_adjusted_range": llm_result,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
