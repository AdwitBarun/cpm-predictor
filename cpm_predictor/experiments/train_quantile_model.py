import os
import json
import joblib
import xgboost as xgb
import pandas as pd
import numpy as np

from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.metrics import median_absolute_error

from cpm_predictor.backend.features.preprocess import preprocess_training

# -------------------------------------------------
# Paths
# -------------------------------------------------
ARTIFACT_DIR = "cpm_predictor/backend/artifacts"
os.makedirs(ARTIFACT_DIR, exist_ok=True)

MODEL_VERSION = "v1"

# -------------------------------------------------
# Load data
# -------------------------------------------------
df = pd.read_csv("cpm_predictor/data/data_input.csv")

X_raw, y = preprocess_training(df)

# -------------------------------------------------
# One-hot encode ONCE
# -------------------------------------------------
X = pd.get_dummies(X_raw, drop_first=False)

assert X.shape[1] > 0, "❌ Feature matrix is empty"
assert y.notna().all(), "❌ Target still contains NaN"

FEATURE_COLUMNS = X.columns.tolist()

# -------------------------------------------------
# Train / val split
# -------------------------------------------------
X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -------------------------------------------------
# Train quantile models
# -------------------------------------------------
models = {}
for q in [0.1, 0.5, 0.9]:
    model = xgb.XGBRegressor(
        objective="reg:quantileerror",
        quantile_alpha=q,
        n_estimators=400,
        max_depth=4,
        learning_rate=0.02,
        subsample=0.7,
        colsample_bytree=0.7,
        reg_lambda=2.0,
        min_child_weight=5,
        random_state=42,
    )
    model.fit(X_train, y_train)
    models[q] = model

# -------------------------------------------------
# Validation (₹ CPM)
# -------------------------------------------------
p10 = np.expm1(models[0.1].predict(X_val))
p50 = np.expm1(models[0.5].predict(X_val))
p90 = np.expm1(models[0.9].predict(X_val))
y_true = np.expm1(y_val)

coverage = ((y_true >= p10) & (y_true <= p90)).mean()
mae = median_absolute_error(y_true, p50)

print(f"📊 P10–P90 Coverage: {coverage:.3f}")
print(f"📊 Median Absolute Error (₹ CPM): {mae:.2f}")

# -------------------------------------------------
# Save artifacts
# -------------------------------------------------
joblib.dump(models, f"{ARTIFACT_DIR}/cpm_quantile_models.pkl")
joblib.dump(FEATURE_COLUMNS, f"{ARTIFACT_DIR}/feature_columns.pkl")

metadata = {
    "model_version": MODEL_VERSION,
    "trained_on": datetime.utcnow().isoformat(),
    "rows_used": len(X),
    "features_count": len(FEATURE_COLUMNS),
    "target": "log(Del Cpm / Bidvid CPM)",
    "coverage_p10_p90": round(float(coverage), 3),
    "median_absolute_error_cpm": round(float(mae), 2),
}

with open(f"{ARTIFACT_DIR}/model_metadata_{MODEL_VERSION}.json", "w") as f:
    json.dump(metadata, f, indent=2)

print("✅ Quantile CPM models trained & saved successfully")
