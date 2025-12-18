import pandas as pd
import joblib
import xgboost as xgb
from cpm_predictor.backend.features.preprocess import preprocess

# -----------------------------
# Load data
# -----------------------------
df = pd.read_csv("data/data_input.csv")

# -----------------------------
# Preprocess
# -----------------------------
X, y = preprocess(df)

# -----------------------------
# Train global quantile models
# -----------------------------
quantiles = [0.1, 0.5, 0.9]
models = {}

for q in quantiles:
    model = xgb.XGBRegressor(
        objective="reg:quantileerror",
        quantile_alpha=q,
        n_estimators=400,
        max_depth=4,          # conservative depth
        learning_rate=0.05,
        subsample=0.7,
        colsample_bytree=0.7,
        min_child_weight=5,
        reg_lambda=2.0,
        random_state=42
    )

    model.fit(X, y)
    models[q] = model
    print(f"✅ Trained quantile model q={q}")

# -----------------------------
# Save artifacts
# -----------------------------
joblib.dump(models, "model/global_quantile_models.pkl")
joblib.dump(X.columns.tolist(), "model/feature_columns.pkl")

print("🎯 Global quantile models saved.")
