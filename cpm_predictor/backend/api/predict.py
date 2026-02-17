# backend/api/predict.py

from fastapi import APIRouter, HTTPException
from cpm_predictor.backend.models.predictor import predict_cpm_range
from cpm_predictor.backend.models.similiarity import find_similar_campaigns
from cpm_predictor.backend.models.historical_store import get_historical_data
from cpm_predictor.backend.llm.orchestrator import run_llm_reasoning
from cpm_predictor.backend.app.schemas import CampaignInput
from cpm_predictor.backend.models.blending import compute_final_cpm
router = APIRouter()

import math

def json_safe(obj):
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    elif isinstance(obj, dict):
        return {k: json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [json_safe(v) for v in obj]
    else:
        return obj

@router.post("/predict")
def predict_cpm(payload: CampaignInput):
    try:
        raw_input = payload.dict()

        # 🔁 Normalize API keys → training column names
        KEY_REMAP = {
            "Start_Date": "Start Date",
            "End_Date": "End Date",
            "Mobile_CTV": "Mobile / CTV",
            "Planned_Reach_1_plus": "Planned Reach 1+",
            "Planned_Freq": "Planned Freq",
            "Planned_Budget": "Planned Budget",
            "Planned_Impressions": "Planned Impressions",
        }

        normalized_input = {}
        for k, v in raw_input.items():
            normalized_input[KEY_REMAP.get(k, k)] = v

        raw_input = normalized_input    

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
            similarity_output=similar,
        )
        final_cpm = compute_final_cpm(
            pred=pred,
            similar_campaigns=similar,
            llm_result=llm_result
        )



            
        # -----------------------------
        # 5. Final response
        # -----------------------------
        response = {
            "model_range": pred["model_range"],
            "conformal_range": pred["conformal_range"],
            "shap_top_features": pred["shap_top_features"],
            "similar_campaigns": similar,
            "llm_adjusted_range": llm_result,
            "final_blended_cpm": final_cpm,
        }
        return json_safe(response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
