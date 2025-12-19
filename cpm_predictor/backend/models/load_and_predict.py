from typing import Dict, Any

from cpm_predictor.backend.models.loader import load_models
from cpm_predictor.backend.models.predictor import predict_cpm_range
from cpm_predictor.backend.features.geo_decoder import (
    encode_geography,
    decode_geography,
)


def load_and_predict(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Public entry point used by API / services.
    """

    # -------------------------------------------------
    # 1. Load artifacts
    # -------------------------------------------------
    models, feature_columns = load_models()

    # -------------------------------------------------
    # 2. Geography handling
    # -------------------------------------------------
    geo_names = payload.get("Geography_Targeting_Include")

    ml_features = payload.copy()
    ml_features["Geography Targeting - Include"] = encode_geography(geo_names)

    llm_features = payload.copy()
    llm_features["decoded_geo"] = decode_geography(
        ml_features["Geography Targeting - Include"]
    )

    # -------------------------------------------------
    # 3. Predict
    # -------------------------------------------------
    return predict_cpm_range(
        models=models,
        feature_columns=feature_columns,
        ml_features=ml_features,
        llm_features=llm_features,
    )
