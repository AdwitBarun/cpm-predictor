from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class PredictionRequest(BaseModel):
    """Schema for prediction request payload."""
    campaign_id: str = Field(..., description="Unique identifier for the campaign")
    advertiser_id: str = Field(..., description="ID of the advertiser")
    placement: str = Field(..., description="Placement type (e.g., 'in_feed', 'story')")
    targeting: Dict[str, Any] = Field(..., description="Targeting parameters")
    budget: float = Field(..., gt=0, description="Campaign budget")
    duration_days: int = Field(..., gt=0, description="Campaign duration in days")
    
    class Config:
        schema_extra = {
            "example": {
                "campaign_id": "camp_123",
                "advertiser_id": "adv_456",
                "placement": "in_feed",
                "targeting": {
                    "age_range": [18, 35],
                    "gender": "all",
                    "locations": ["US", "CA"],
                    "interests": ["technology", "gaming"]
                },
                "budget": 10000.0,
                "duration_days": 30
            }
        }

class PredictionResponse(BaseModel):
    """Schema for prediction response."""
    campaign_id: str
    prediction_id: str
    predictions: Dict[str, float]  # quantile: value
    confidence_interval: Dict[str, float]  # lower, upper
    timestamp: datetime
    model_version: str
    
    class Config:
        schema_extra = {
            "example": {
                "campaign_id": "camp_123",
                "prediction_id": "pred_789",
                "predictions": {
                    "q10": 0.85,
                    "q50": 1.20,
                    "q90": 1.75
                },
                "confidence_interval": {
                    "lower": 0.80,
                    "upper": 1.80
                },
                "timestamp": "2023-10-01T12:00:00Z",
                "model_version": "v1.0"
            }
        }

class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str
    details: Optional[Dict[str, Any]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "error": "Invalid input parameters",
                "details": {"field": "budget", "issue": "must be greater than 0"}
            }
        }
