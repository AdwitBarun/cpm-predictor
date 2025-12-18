import shap
import xgboost as xgb
import pandas as pd
from cpm_predictor.backend.features.preprocess import preprocess

import numpy as np
df = pd.read_csv("../data/data_input.csv")

X, y = preprocess(df)

model = xgb.XGBRegressor(
    n_estimators=300,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)

model.fit(X, y)

explainer = shap.Explainer(model)
shap_values = explainer(X)

shap.plots.bar(shap_values, max_display=20)
print("X shape:", X.shape)
print("y NaNs:", y.isna().sum())
print("y inf:", np.isinf(y).sum())
