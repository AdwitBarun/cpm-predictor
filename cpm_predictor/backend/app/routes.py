from fastapi import APIRouter, HTTPException
from .schemas import PredictionRequest
from ..models.predictor import predict_cpm_range

router = APIRouter()

@router.post("/predict")
def predict(payload: PredictionRequest):
    try:
        return predict_cpm_range(payload.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
