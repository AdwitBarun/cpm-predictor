from pydantic import BaseModel
from typing import Optional

class PredictionRequest(BaseModel):
    Device: str
    TG: str
    Geography_Targeting_Include: str
    Planned_Budget: float
    Planned_Impressions: float
    Planned_Freq: float
    Inventory_Mode: str
    Video_Ad_Format: str
    TrueView_Video_Ad_Formats: str
    month_range: str
    campaign_duration_days: float
