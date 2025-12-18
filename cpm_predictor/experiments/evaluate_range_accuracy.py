import joblib
import numpy as np
import pandas as pd
from cpm_predictor.backend.features.preprocess import preprocess

ARTIFACT_DIR = "../backend/artifacts"
MODEL_VERSION = "v1"

df = pd.read_csv("../data/data_input.csv")
X, y = preprocess(df)

models = joblib.load(f"{ARTIFACT_DIR}/cpm_quantile_models_{MODEL_VERSION}.pkl")

p10 = models[0.1].predict(X)
p50 = models[0.5].predict(X)
p90 = models[0.9].predict(X)

# Back-transform
p10 = np.expm1(p10)
p50 = np.expm1(p50)
p90 = np.expm1(p90)

y_true = np.expm1(y)

coverage = ((y_true >= p10) & (y_true <= p90)).mean()

print("Range coverage (P10–P90):", round(coverage, 3))
print("Median absolute error (P50):", round(np.median(abs(y_true - p50)), 2))
