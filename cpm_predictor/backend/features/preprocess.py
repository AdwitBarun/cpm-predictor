import pandas as pd
import numpy as np
from typing import Dict, List, Union


# ---------------------------------------------------------
# Columns by type (MUST match training-time logic)
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# Main preprocessing function
# ---------------------------------------------------------

def preprocess(
    input_data: Union[Dict, pd.DataFrame],
    feature_columns: List[str],
) -> pd.DataFrame:
    """
    Preprocess raw input into model-ready dataframe.

    Args:
        input_data: dict (single prediction) or DataFrame
        feature_columns: exact feature list used during training

    Returns:
        pd.DataFrame with columns exactly matching feature_columns
    """

    # ---------------------------
    # 1️⃣ Convert input to DataFrame
    # ---------------------------
    if isinstance(input_data, dict):
        df = pd.DataFrame([input_data])
    else:
        df = input_data.copy()

    # ---------------------------
    # 2️⃣ Ensure all expected base columns exist
    # ---------------------------
    for col in NUMERIC_COLS + CATEGORICAL_COLS:
        if col not in df.columns:
            df[col] = np.nan

    # ---------------------------
    # 3️⃣ Numeric handling
    # ---------------------------
    for col in NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

        # Median imputation (robust for skewed CPM data)
        median_val = df[col].median()
        df[col] = df[col].fillna(median_val)

    # ---------------------------
    # 4️⃣ Categorical handling
    # ---------------------------
    for col in CATEGORICAL_COLS:
        df[col] = (
            df[col]
            .astype(str)
            .replace({"nan": "Unknown", "None": "Unknown"})
            .fillna("Unknown")
        )

    # ---------------------------
    # 5️⃣ One-hot encode categoricals
    # ---------------------------
    df_encoded = pd.get_dummies(
        df,
        columns=CATEGORICAL_COLS,
        drop_first=False,
    )

    # ---------------------------
    # 6️⃣ Align with training features
    # ---------------------------
    for col in feature_columns:
        if col not in df_encoded.columns:
            df_encoded[col] = 0

    # Remove extra columns (from unseen categories)
    df_encoded = df_encoded[feature_columns]

    # ---------------------------
    # 7️⃣ Final safety checks
    # ---------------------------
    df_encoded = df_encoded.replace([np.inf, -np.inf], 0)
    df_encoded = df_encoded.fillna(0)

    return df_encoded
