from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import logging

from cpm_predictor.backend.models.load_and_predict import load_and_predict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CPM Prediction API",
    description="Predict CPM ranges using ML + LLM (Gemini)",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict")
async def predict(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        logger.info("Received prediction request")
        return load_and_predict(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("Prediction failed")
        raise HTTPException(
            status_code=500,
            detail="Internal error while predicting CPM",
        )

@app.get("/health")
async def health():
    return {"status": "ok"}
