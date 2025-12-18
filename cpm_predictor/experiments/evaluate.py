import joblib
import pandas as pd
import numpy as np
from cpm_predictor.backend.features.preprocess import preprocess
from sklearn.metrics import mean_absolute_error

df = pd.read_csv("data/data_input.csv")
X, y = preprocess(df)

models = joblib.load("model/segmented_models.pkl")

for seg, seg_models in models.items():
    preds = seg_models[0.5].predict(X)
    mae = mean_absolute_error(y, preds)
    print(f"{seg} | MAE(log): {mae:.3f}")
