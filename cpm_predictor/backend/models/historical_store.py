# backend/models/historical_store.py

import os
import time
import pandas as pd
from typing import Tuple

from cpm_predictor.backend.features.preprocess import preprocess_input

from google.oauth2.service_account import Credentials
import json
# -----------------------------
# Config
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")

LOCAL_CSV_PATH = os.path.join(DATA_DIR, "data_input.csv")

REFRESH_INTERVAL_SECONDS = 3600  # 1 hour

# -----------------------------
# In-memory cache
# -----------------------------
_CACHE = {
    "last_loaded": None,
    "X_hist": None,
    "meta_df": None,
}


# -----------------------------
# Public API
# -----------------------------

def get_historical_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Returns cached historical features + metadata.
    Refreshes cache if expired.
    """
    global _CACHE

    now = time.time()

    if (
        _CACHE["last_loaded"] is None
        or now - _CACHE["last_loaded"] > REFRESH_INTERVAL_SECONDS
    ):
        _load_historical_data()

    return _CACHE["X_hist"], _CACHE["meta_df"]


# -----------------------------
# Load logic
# -----------------------------

def _load_historical_data():
    global _CACHE

    try:
        # 🔹 Step 1: Load data (fallback CSV for now)
        df = _load_from_csv()

        # 🔹 Step 2: Preprocess
        X_model, X_similarity, _ = preprocess_input(
            raw_input=df,
            feature_columns=_load_feature_columns(),
        )

        # 🔹 Step 3: Metadata for UI / similarity
        meta_df = _build_meta_df(df)

        _CACHE.update(
            {
                "X_hist": X_similarity,
                "meta_df": meta_df,
                "last_loaded": time.time(),
            }
        )

        print("✅ Historical data loaded successfully")

    except Exception as e:
        print(f"❌ Failed to load historical data: {e}")
        raise

# backend/models/historical_store.py

def force_refresh():
    """
    Force reload of historical data (admin-triggered).
    """
    global _CACHE
    _CACHE["last_loaded"] = None
    _load_historical_data()

# -----------------------------
# Helpers
# -----------------------------

def _load_from_csv() -> pd.DataFrame:
    if not os.path.exists(LOCAL_CSV_PATH):
        raise FileNotFoundError(f"Missing historical CSV: {LOCAL_CSV_PATH}")

    return pd.read_csv(LOCAL_CSV_PATH)


def _load_feature_columns():
    from cpm_predictor.backend.models.loader import load_models
    _, feature_columns = load_models()
    return feature_columns


def _build_meta_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep ONLY UI-relevant fields here.
    """
    cols = [
        "Campaign Name",
        "Markets",
        "Device",
        "TG",
        "start_month",
        "campaign_intensity",
        "Del Cpm/\nBidvid  cpm",
    ]

    meta = df.copy()
    meta = meta[[c for c in cols if c in meta.columns]]

    meta = meta.rename(
        columns={
            "Del Cpm/\nBidvid  cpm": "delivered_cpm",
            "Markets": "markets",
            "Device": "device_summary",
            "TG": "tg_summary",
        }
    )

    return meta.reset_index(drop=True)

def _load_from_gsheet() -> pd.DataFrame:
    
    import gspread
    creds_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not creds_json:
        raise RuntimeError("Missing GOOGLE_SERVICE_ACCOUNT_JSON")

    sheet_id = os.getenv("HISTORICAL_GSHEET_ID")
    sheet_tab = os.getenv("HISTORICAL_GSHEET_TAB", "Sheet1")

    if not sheet_id:
        raise RuntimeError("Missing HISTORICAL_GSHEET_ID")

    creds_dict = json.loads(creds_json)

    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)

    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id).worksheet(sheet_tab)

    records = sheet.get_all_records()
    return pd.DataFrame(records)

# backend/models/historical_store.py (ADD BELOW EXISTING CODE)

def refresh_from_gsheet_and_save():
    """
    Fetch live Google Sheet, save to data_input.csv,
    then refresh in-memory cache.
    """
    df = _load_from_gsheet()

    os.makedirs(DATA_DIR, exist_ok=True)
    df.to_csv(LOCAL_CSV_PATH, index=False)

    print("✅ Google Sheet downloaded and saved to CSV")

    force_refresh()
