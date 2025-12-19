from pydantic import BaseModel
from typing import Optional


class CPMRequest(BaseModel):
    # -------------------------
    # Numeric Features
    # -------------------------
    Planned_Reach_1_plus: Optional[float] = None
    Planned_Freq: Optional[float] = None
    Planned_Budget: Optional[float] = None
    Planned_Impressions: Optional[int] = None
    Pacing_Rate: Optional[float] = None
    Pacing_Amount: Optional[float] = None
    Frequency_Exposures: Optional[float] = None
    TrueView_View_Frequency_Exposures: Optional[float] = None
    Partner_Revenue_Amount: Optional[float] = None
    campaign_duration_days: Optional[int] = None

    # -------------------------
    # Categorical Features
    # -------------------------
    Device: Optional[str] = None
    TG: Optional[str] = None
    Type: Optional[str] = None
    Subtype: Optional[str] = None
    Budget_Type: Optional[str] = None
    Pacing: Optional[str] = None
    Frequency_Enabled: Optional[str] = None
    Frequency_Period: Optional[str] = None
    TrueView_View_Frequency_Enabled: Optional[str] = None
    TrueView_View_Frequency_Period: Optional[str] = None
    Partner_Revenue_Model: Optional[str] = None

    # Frontend sends NAME → backend encodes to ID for ML
    Geography_Targeting_Include: Optional[str] = None  

    TrueView_Video_Ad_Formats: Optional[str] = None
    Inventory_Mode: Optional[str] = None
    Video_Ad_Format: Optional[str] = None
    month_range: Optional[str] = None
