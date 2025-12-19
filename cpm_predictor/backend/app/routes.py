"""
API routes for CPM Prediction
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from cpm_predictor.backend.models.load_and_predict import load_and_predict

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/predict")
def predict_cpm(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predict CPM range (₹).

    Frontend sends:
    - Geography_Targeting_Include → NAMES (e.g. "Kolkata, Patna")
    - Other campaign features

    Backend returns:
    - historical (ML P10/P50/P90)
    - llm (Gemini adjusted)
    - final (blended)
    - shap_top_features
    """
    try:
        logger.info("Received /predict request")

        result = load_and_predict(payload)

        return result

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(
            status_code=500,
            detail="Internal error while predicting CPM",
        )


@router.get("/health")
def health():
    return {"status": "ok"}
