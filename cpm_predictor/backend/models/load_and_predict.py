from typing import Dict, Any

from cpm_predictor.backend.models.loader import load_artifacts
from cpm_predictor.backend.models.predictor import predict_cpm_range
from cpm_predictor.backend.features.geo_decoder import (
    encode_geography,
    decode_geography,
)


def load_and_predict(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Public entry point for API / services.
    """

    # -------------------------------------------------
    # 1. Load artifacts (cached)
    # -------------------------------------------------
    models, feature_columns = load_artifacts()

    # -------------------------------------------------
    # 2. Split ML vs LLM features
    # -------------------------------------------------
    geo_names = payload.get("Geography_Targeting_Include")

    ml_features = payload.copy()
    ml_features["Geography Targeting - Include"] = encode_geography(geo_names)

    llm_features = payload.copy()
    llm_features["decoded_geo"] = decode_geography(
        ml_features["Geography Targeting - Include"]
    )

    # -------------------------------------------------
    # 3. Delegate to predictor
    # -------------------------------------------------
    return predict_cpm_range(
        ml_features=ml_features,
        llm_features=llm_features,
    )
