from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any

from cpm_predictor.backend.models.predictor import predict_cpm_range

router = APIRouter()

class CPMRequest(BaseModel):
    payload: Dict[str, Any]

@router.post("/predict")
def predict_cpm(req: CPMRequest):
    result = predict_cpm_range(req.payload)
    return result
