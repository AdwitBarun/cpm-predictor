from fastapi import APIRouter
from typing import Dict, Any

from cpm_predictor.backend.models.predictor import predict_cpm_range
from cpm_predictor.backend.features.geo_decoder import encode_geo_name
from cpm_predictor.backend.app.schemas import CPMRequest

router = APIRouter()

# -------------------------------------------------
# Schema → Training column mapping
# -------------------------------------------------
SCHEMA_TO_MODEL_COLS = {
    "Planned_Reach_1_plus": "Planned Reach 1+",
    "Budget_Type": "Budget Type",
    "Pacing_Rate": "Pacing Rate",
    "Pacing_Amount": "Pacing Amount",
    "Frequency_Exposures": "Frequency Exposures",
    "TrueView_View_Frequency_Exposures": "TrueView View Frequency Exposures",
    "TrueView_View_Frequency_Enabled": "TrueView View Frequency Enabled",
    "TrueView_View_Frequency_Period": "TrueView View Frequency Period",
    "Partner_Revenue_Amount": "Partner Revenue Amount",
    "Partner_Revenue_Model": "Partner Revenue Model",
    "Geography_Targeting_Include": "Geography Targeting - Include",
    "TrueView_Video_Ad_Formats": "TrueView Video Ad Formats",
    "Inventory_Mode": "Inventory Mode",
    "Video_Ad_Format": "Video Ad Format",
}


# -------------------------------------------------
# Utility: normalize incoming payload
# -------------------------------------------------
def normalize_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    normalized = {}

    for key, value in data.items():
        mapped_key = SCHEMA_TO_MODEL_COLS.get(key, key)
        normalized[mapped_key] = value

    return normalized


# -------------------------------------------------
# Prediction endpoint
# -------------------------------------------------
@router.post("/predict")
def predict_cpm(req: CPMRequest):
    """
    Predict CPM range.
    Frontend sends:
      - Geography name (e.g. "Hyderabad")

    Backend:
      - Converts name → geo code for ML
      - Keeps name for Gemini LLM
    """

    payload = req.model_dump(exclude_none=True)

    # -------------------------
    # Geography handling
    # -------------------------
    geo_name = payload.get("Geography_Targeting_Include")

    if geo_name:
        geo_code = encode_geo_name(geo_name)
        payload["Geography_Targeting_Include"] = geo_code
        payload["decoded_geo"] = [geo_name]   # for LLM context

    # -------------------------
    # Normalize column names
    # -------------------------
    normalized_payload = normalize_payload(payload)

    # -------------------------
    # Run prediction pipeline
    # -------------------------
    result = predict_cpm_range(normalized_payload)

    return result
