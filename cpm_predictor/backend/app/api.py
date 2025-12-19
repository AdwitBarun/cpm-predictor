"""
FastAPI application for the CPM prediction service.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import logging

from cpm_predictor.backend.models.load_and_predict import load_and_predict

# -------------------------------------------------
# Logging
# -------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------------------------
# FastAPI App
# -------------------------------------------------
app = FastAPI(
    title="CPM Prediction API",
    description="Predict CPM ranges using ML + LLM (Gemini)",
    version="2.0.0",
)

# -------------------------------------------------
# CORS
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# Routes
# -------------------------------------------------
@app.post("/predict")
async def predict(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predict CPM range.

    Input:
      - Geography_Targeting_Include → NAME (e.g. "Hyderabad")
      - Other campaign fields

    Output:
      - historical (ML range, ₹ CPM)
      - llm (contextual adjustment)
      - final (blended range)
      - shap_top_features
    """
    try:
        logger.info("Received prediction request")

        result = load_and_predict(payload)

        logger.info("Prediction successful")
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


@app.get("/health")
async def health():
    return {"status": "ok"}
