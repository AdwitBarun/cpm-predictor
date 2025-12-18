import joblib
import numpy as np
import pandas as pd

from cpm_predictor.backend.features.preprocess import preprocess

ARTIFACT_DIR = "../backend/artifacts"
MODEL_VERSION = "v1"

# Load artifacts
models = joblib.load(f"{ARTIFACT_DIR}/cpm_quantile_models_{MODEL_VERSION}.pkl")
feature_cols = joblib.load(f"{ARTIFACT_DIR}/feature_columns_{MODEL_VERSION}.pkl")

# New data (example)
df_new = pd.read_csv("../data/new_campaign_input.csv")

# Preprocess
X_new, _ = preprocess(df_new)

# Align columns (CRITICAL)
X_new = X_new.reindex(columns=feature_cols, fill_value=0)

# Predict
p10 = np.expm1(models[0.1].predict(X_new))
p50 = np.expm1(models[0.5].predict(X_new))
p90 = np.expm1(models[0.9].predict(X_new))

result = pd.DataFrame({
    "cpm_p10": p10,
    "cpm_p50": p50,
    "cpm_p90": p90
})

print(result)
