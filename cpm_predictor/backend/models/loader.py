import os
import joblib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIFACT_DIR = os.path.join(BASE_DIR, "artifacts")

_MODELS = None
_FEATURE_COLUMNS = None


def load_models():
    """
    Load ML artifacts once and cache them.
    """
    global _MODELS, _FEATURE_COLUMNS

    if _MODELS is None or _FEATURE_COLUMNS is None:
        model_path = os.path.join(ARTIFACT_DIR, "cpm_quantile_models.pkl")
        feature_path = os.path.join(ARTIFACT_DIR, "feature_columns.pkl")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")

        if not os.path.exists(feature_path):
            raise FileNotFoundError(f"Feature file not found: {feature_path}")

        _MODELS = joblib.load(model_path)
        _FEATURE_COLUMNS = joblib.load(feature_path)

    return _MODELS, _FEATURE_COLUMNS
