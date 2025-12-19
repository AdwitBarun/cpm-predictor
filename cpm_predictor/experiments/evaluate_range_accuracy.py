import joblib
import numpy as np
import pandas as pd

from cpm_predictor.backend.features.preprocess import (
    preprocess_training,
    preprocess_features,
)

ARTIFACT_DIR = "cpm_predictor/backend/artifacts"

# -----------------------
# Load data
# -----------------------
df = pd.read_csv("cpm_predictor/data/data_input.csv")

# Split raw features and log target
X_raw, y_log = preprocess_training(df)

# -----------------------
# Load artifacts
# -----------------------
models = joblib.load(f"{ARTIFACT_DIR}/cpm_quantile_models.pkl")
feature_columns = joblib.load(f"{ARTIFACT_DIR}/feature_columns.pkl")

# -----------------------
# Build model-ready features
# -----------------------
X = preprocess_features(X_raw, feature_columns=feature_columns)

# -----------------------
# Predict (LOG space → CPM)
# -----------------------
p10 = np.expm1(models[0.1].predict(X))
p50 = np.expm1(models[0.5].predict(X))
p90 = np.expm1(models[0.9].predict(X))

y_true = np.expm1(y_log)

# -----------------------
# Metrics
# -----------------------
coverage = ((y_true >= p10) & (y_true <= p90)).mean()
median_abs_error = np.median(np.abs(y_true - p50))

print(f"📊 Range Coverage (P10–P90): {coverage:.3f}")
print(f"📊 Median Absolute Error (₹ CPM): {median_abs_error:.2f}")
