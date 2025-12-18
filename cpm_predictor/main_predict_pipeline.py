import joblib
import pandas as pd
import numpy as np
from cpm_predictor.backend.features.preprocess import preprocess

models = joblib.load("model/segmented_models.pkl")
features = joblib.load("model/feature_columns.pkl")

sample = {
    "Device": "Mobile",
    "TG": "Adults",
    "Markets": "India",
    "Planned Reach 1+": 100000,
    "Planned Freq": 3,
    "Planned Budget": 500000,
    "Planned Impressions": 300000,
    "Type": "Video",
    "Subtype": "InStream",
    "Budget Type": "Daily",
    "Pacing": "Even",
    "Pacing Rate": 1,
    "Pacing Amount": 10000,
    "Frequency Enabled": True,
    "Video Ad Format": "Skippable",
    "Inventory Mode": "Standard",
    "Start Date": "2025-01-01",
    "End Date": "2025-01-31",
    "Del Cpm/\nBidvid  cpm": 50
}

df = pd.DataFrame([sample])
X, _ = preprocess(df)
X = X.reindex(columns=features, fill_value=0)

model = models["Skippable"][0.5]
print("Predicted CPM:", np.expm1(model.predict(X)[0]))
