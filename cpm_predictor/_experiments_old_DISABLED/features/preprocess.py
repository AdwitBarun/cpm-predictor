import pandas as pd
import numpy as np

TARGET = "Del Cpm/\nBidvid  cpm"

NUMERIC_COLS = [
    "Planned Reach 1+",
    "Planned Freq",
    "Planned Budget",
    "Planned Impressions",
    "Pacing Rate",
    "Pacing Amount",
    "Frequency Exposures",
    "TrueView View Frequency Exposures",
    "Partner Revenue Amount",
    "campaign_duration_days"
]

CATEGORICAL_COLS = [
    "Device", "TG", "Type", "Subtype", "Budget Type", "Pacing",
    "Frequency Enabled", "Frequency Period",
    "TrueView View Frequency Enabled",
    "TrueView View Frequency Period",
    "Partner Revenue Model",
    "Geography Targeting - Include",
    "TrueView Video Ad Formats",
    "Inventory Mode",
    "Video Ad Format",
    "month_range"
]

def preprocess(df):
    df = df.copy()

    # Target log transform (critical)
    # Drop rows with invalid target BEFORE log
    df = df[df[TARGET].notna()]
    df = df[df[TARGET] > 0]

    # Log-transform target
    y = np.log1p(df[TARGET])


    # Numeric NaNs → median (robust)
    for col in NUMERIC_COLS:
        df[col] = df[col].fillna(df[col].median())

    X_num = df[NUMERIC_COLS]

    # Categorical encoding with NaN preserved
    X_cat = pd.get_dummies(
        df[CATEGORICAL_COLS],
        dummy_na=True,
        drop_first=False
    )

    X = pd.concat([X_num, X_cat], axis=1)

    return X, y
