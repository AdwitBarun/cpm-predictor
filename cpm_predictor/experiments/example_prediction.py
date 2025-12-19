import joblib
import numpy as np

from cpm_predictor.backend.features.preprocess import preprocess_features
from cpm_predictor.backend.models.shap_explainer import explain_prediction

ARTIFACT_DIR = "cpm_predictor/backend/artifacts"

models = joblib.load(f"{ARTIFACT_DIR}/cpm_quantile_models.pkl")
feature_columns = joblib.load(f"{ARTIFACT_DIR}/feature_columns.pkl")

sample_input = {
    "Device": "YT NSK",
    "TG": "MF 25-34 NCCS A",
    "Planned_Impressions": 940903,
    "Planned_Budget": 3763612,
    "campaign_duration_days": 84,
    "Inventory Mode": "Limited",
    "Video Ad Format": "Non Skippable",
    "month_range": "Jul–Sep 2025",
}

X = preprocess_features(sample_input, feature_columns)

p10 = np.expm1(models[0.1].predict(X)[0])
p50 = np.expm1(models[0.5].predict(X)[0])
p90 = np.expm1(models[0.9].predict(X)[0])

print("🔮 Predicted CPM Range (₹)")
print("P10:", round(p10, 2))
print("P50:", round(p50, 2))
print("P90:", round(p90, 2))

print("\n🧠 Top SHAP features:")
for feat, val in explain_prediction(models[0.5], X):
    print(f"{feat}: {round(val, 3)}")
