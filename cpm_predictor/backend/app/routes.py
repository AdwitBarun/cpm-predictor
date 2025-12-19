from fastapi import APIRouter
from cpm_predictor.backend.features.geo_decoder import encode_geography
from cpm_predictor.backend.models.load_and_predict import predict_cpm_range

router = APIRouter()

@router.post("/predict")
def predict(payload: dict):

    # ------------------------------------------------
    # 1. Geography from frontend = NAMES
    # ------------------------------------------------
    geo_names = payload.get("Geography_Targeting_Include", "")

    # ------------------------------------------------
    # 2. Encode for ML
    # ------------------------------------------------
    geo_codes = encode_geography(geo_names)

    ml_features = payload.copy()
    ml_features["Geography_Targeting_Include"] = geo_codes

    # ------------------------------------------------
    # 3. LLM uses names directly
    # ------------------------------------------------
    llm_features = payload.copy()
    llm_features["decoded_geo"] = geo_names.split(";") if geo_names else []

    # ------------------------------------------------
    # 4. Predict
    # ------------------------------------------------
    return predict_cpm_range(
        ml_features=ml_features,
        llm_features=llm_features,
    )
