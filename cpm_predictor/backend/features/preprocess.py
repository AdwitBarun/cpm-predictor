import pandas as pd
import numpy as np
from typing import Dict, List, Union

TARGET_COL = "Del Cpm/\nBidvid  cpm"

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
    "campaign_duration_days",
]

CATEGORICAL_COLS = [
    "Device",
    "TG",
    "Type",
    "Subtype",
    "Budget Type",
    "Pacing",
    "Frequency Enabled",
    "Frequency Period",
    "TrueView View Frequency Enabled",
    "TrueView View Frequency Period",
    "Partner Revenue Model",
    "Geography Targeting - Include",
    "TrueView Video Ad Formats",
    "Inventory Mode",
    "Video Ad Format",
    "month_range",
]

# =====================================================
# 🔹 COMMON FEATURE PROCESSING (NO TARGET)
# =====================================================
def preprocess_features(
    input_data: Union[Dict, pd.DataFrame],
    feature_columns: List[str],
) -> pd.DataFrame:

    if isinstance(input_data, dict):
        df = pd.DataFrame([input_data])
    else:
        df = input_data.copy()

    for col in NUMERIC_COLS + CATEGORICAL_COLS:
        if col not in df.columns:
            df[col] = np.nan

    for col in NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].fillna(df[col].median())

    for col in CATEGORICAL_COLS:
        df[col] = (
            df[col]
            .astype(str)
            .replace({"nan": "Unknown", "None": "Unknown"})
            .fillna("Unknown")
        )

    df = pd.get_dummies(df, columns=CATEGORICAL_COLS, drop_first=False)

    for col in feature_columns:
        if col not in df.columns:
            df[col] = 0

    return df[feature_columns].replace([np.inf, -np.inf], 0).fillna(0.001)

# =====================================================
# 🔹 TRAINING PREPROCESS (WITH TARGET)
# =====================================================
def preprocess_training(df: pd.DataFrame):
    TARGET_COL = "Del Cpm/\nBidvid  cpm"

    if TARGET_COL not in df.columns:
        raise ValueError(f"Target column missing: {TARGET_COL}")

    # --- Clean target ---
    y_raw = pd.to_numeric(df[TARGET_COL], errors="coerce")

    # Drop invalid CPM rows
    mask = (
        y_raw.notna() &
        np.isfinite(y_raw) &
        (y_raw > 0) &
        (y_raw < 1_000)   # sanity cap, adjust if needed
    )

    df = df.loc[mask].reset_index(drop=True)
    y_raw = y_raw.loc[mask]

    # Log-transform target
    y = np.log1p(y_raw)

    # Drop target from features
    X_raw = df.drop(columns=[TARGET_COL])

    return X_raw, y
