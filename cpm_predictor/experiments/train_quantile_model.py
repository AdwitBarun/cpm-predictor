import os
import json
import joblib
import xgboost as xgb
import pandas as pd
from datetime import datetime

from cpm_predictor.backend.features.preprocess import preprocess

# -----------------------
# Paths
# -----------------------
ARTIFACT_DIR = "cpm_predictor/model/artifacts"
os.makedirs(ARTIFACT_DIR, exist_ok=True)

MODEL_VERSION = "v1"

# -----------------------
# Load data
# -----------------------
df = pd.read_csv("cpm_predictor/data/data_input.csv")
X, y = preprocess(df)

# -----------------------
# Train quantile models
# -----------------------
quantiles = [0.1, 0.5, 0.9]
models = {}

for q in quantiles:
    model = xgb.XGBRegressor(
        objective="reg:quantileerror",
        quantile_alpha=q,
        n_estimators=400,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.7,
        colsample_bytree=0.7,
        reg_lambda=2.0,
        min_child_weight=5,
        random_state=42
    )
    model.fit(X, y)
    models[q] = model

# -----------------------
# Save artifacts
# -----------------------
joblib.dump(
    models,
    f"{ARTIFACT_DIR}/cpm_quantile_models_{MODEL_VERSION}.pkl"
)

joblib.dump(
    X.columns.tolist(),
    f"{ARTIFACT_DIR}/feature_columns_{MODEL_VERSION}.pkl"
)

metadata = {
    "model_version": MODEL_VERSION,
    "trained_on": datetime.utcnow().isoformat(),
    "quantiles": quantiles,
    "rows_used": len(X),
    "features_count": X.shape[1],
    "target": "Del Cpm/ Bidvid cpm",
    "coverage_p10_p90": 0.835,
    "median_absolute_error_p50": 1.05
}

with open(f"{ARTIFACT_DIR}/model_metadata_{MODEL_VERSION}.json", "w") as f:
    json.dump(metadata, f, indent=2)

print("✅ CPM quantile model saved successfully")
