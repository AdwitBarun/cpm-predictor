# backend/app/schemas.py

from pydantic import BaseModel
from typing import Dict, Any, List


class CampaignInput(BaseModel):
    Device: str | None = None
    TG: str | None = None
    Mobile_CTV: str | None = None
    Markets: str | None = None
    Start_Date: str | None = None
    End_Date: str | None = None

    Planned_Reach_1_plus: float | None = None
    Planned_Freq: float | None = None
    Planned_Budget: float | None = None
    Planned_Impressions: float | None = None

    class Config:
        extra = "allow"  


class CPMResponse(BaseModel):
    model_range: Dict[str, float]
    conformal_range: Dict[str, float]

    shap_top_features: List[Dict[str, Any]]
    similar_campaigns: List[Dict[str, Any]]

    llm_adjusted_range: Dict[str, Any]
