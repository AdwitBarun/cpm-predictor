"""
Feature preprocessing for CPM prediction.

Responsibilities:
- Accept raw campaign input (dict or DataFrame)
- Derive all ML features used during training
- Produce:
  1) X_model       → aligned to feature_columns.pkl
  2) X_similarity  → for similarity search
  3) llm_payload   → human-readable raw + derived context
"""

from typing import Dict, Any, Tuple, List
import pandas as pd
import numpy as np
import re

from cpm_predictor.backend.features.geo_decoder import decode_markets
from cpm_predictor.backend.llm.utils import decode_tg


# =========================================================
# Helpers
# =========================================================

def safe_col(df: pd.DataFrame, col: str, default="") -> pd.Series:
    """
    Always return a Series.
    Prevents .fillna(), .isna(), .astype crashes.
    """
    if col not in df.columns:
        return pd.Series([default] * len(df), index=df.index)
    return df[col]


# =========================================================
# Public API
# =========================================================

def preprocess_input(
    raw_input: Dict[str, Any] | pd.DataFrame,
    feature_columns: List[str],
    city_tier_lookup: dict | None = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, Any]]:

    df = _normalize_input(raw_input)

    # -----------------------------
    # Derive features
    # -----------------------------
    df = _derive_numeric_features(df)
    df = _derive_time_features(df)
    df = _derive_tg_features(df)
    df = _derive_geo_features(df, city_tier_lookup)
    df = _derive_device_features(df)
    df = _derive_campaign_intensity(df)

    # =====================================================
    # 1️⃣ MODEL FEATURES (STRICT - DO NOT TOUCH)
    # =====================================================
    X_model = df.reindex(columns=feature_columns, fill_value=0)

    # Hard numeric firewall
    X_model = X_model.select_dtypes(include=["number"]).astype(float)

    # Preserve order
    X_model = X_model.reindex(columns=feature_columns, fill_value=0.0)

    # =====================================================
    # SIMILARITY FEATURES (STRICT NUMERIC + ENCODED ONLY)
    # =====================================================

   
    numeric_similarity_cols = [
        "planned_budget",
        "planned_freq",
        "planned_impressions",
        "planned_reach_1_plus",
        "campaign_intensity",
    ]

    numeric_similarity_cols = [
        c for c in numeric_similarity_cols
        if c in df.columns
    ]

    categorical_similarity_cols = [
        c for c in df.columns
        if (
            c.startswith("tg_")
            or c.startswith("geo_")
            or c.startswith("device_")
        )
    ]

    similarity_cols = numeric_similarity_cols + categorical_similarity_cols


    X_similarity = df[similarity_cols].copy()


    X_similarity = X_similarity.select_dtypes(include=["number"]).astype(float)

    # -----------------------------

    # -----------------------------
    from sklearn.preprocessing import StandardScaler

    if numeric_similarity_cols:
        scaler = StandardScaler()
        X_similarity[numeric_similarity_cols] = scaler.fit_transform(
            X_similarity[numeric_similarity_cols]
        )

    # =====================================================

    # =====================================================
    llm_payload = _build_llm_payload(df)

    return X_model, X_similarity, df, llm_payload


# =========================================================
# Input normalization
# =========================================================

COLUMN_ALIASES = {
    "Planned_Reach_1_plus": "Planned Reach 1+",
    "Planned_Freq": "Planned Freq",
    "Planned_Budget": "Planned Budget",
    "Planned_Impressions": "Planned Impressions",
    "Mobile_CTV": "Mobile / CTV",
    "Start_Date": "Start Date",
    "End_Date": "End Date",
    "Campaign_Name": "Campaign Name",
}

def _normalize_input(raw_input):
    if isinstance(raw_input, dict):
        raw_input = {
            COLUMN_ALIASES.get(k, k): v
            for k, v in raw_input.items()
        }
        df = pd.DataFrame([raw_input])

    elif isinstance(raw_input, pd.DataFrame):
        df = raw_input.rename(columns=COLUMN_ALIASES).copy()

    else:
        raise ValueError("Input must be dict or DataFrame")

    df.columns = [c.strip() for c in df.columns]
    return df



# =========================================================
# Numeric features
# =========================================================

def _derive_numeric_features(df):

    # Original raw columns
    raw_cols = {
        "planned_reach_1_plus": "Planned Reach 1+",
        "planned_freq": "Planned Freq",
        "planned_budget": "Planned Budget",
        "planned_impressions": "Planned Impressions",
    }

    for new_col, raw_col in raw_cols.items():
        series = safe_col(df, raw_col)
        if series is None:
            df[new_col] = 0.0
        else:
            df[new_col] = (
                pd.to_numeric(series, errors="coerce")
                .fillna(0.0)
            )

    return df


# =========================================================
# Time features
# =========================================================

def _derive_time_features(df):
    df["start_date"] = pd.to_datetime(
        df.get("Start Date", pd.NaT),
        errors="coerce",
        dayfirst=False
    )

    df["end_date"] = pd.to_datetime(
        df.get("End Date", pd.NaT),
        errors="coerce",
        dayfirst=False
    )

    duration = (df["end_date"] - df["start_date"]).dt.days
    duration = duration.fillna(1)

    df["campaign_duration_days"] = duration.clip(lower=1).astype(int)


    df["start_month"] = df["start_date"].dt.month

    for m in range(1, 13):
        df[f"is_{_month_name(m)}"] = (df["start_month"] == m).astype(int)

    df["start_month_sin"] = np.sin(2 * np.pi * df["start_month"] / 12)
    df["start_month_cos"] = np.cos(2 * np.pi * df["start_month"] / 12)

    return df


def _parse_date(series: pd.Series) -> pd.Series:
    
    series = series.astype(str)

    parsed = pd.to_datetime(series, errors="coerce", dayfirst=True)

    mask = parsed.isna()
    if mask.any():
        parsed.loc[mask] = series.loc[mask].apply(_parse_text_date)

    return parsed



def _parse_text_date(val):
    try:
        val = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", str(val))
        return pd.to_datetime(val, errors="coerce")
    except Exception:
        return pd.NaT


def _month_name(m: int) -> str:
    return [
        "jan", "feb", "mar", "apr", "may", "jun",
        "jul", "aug", "sep", "oct", "nov", "dec"
    ][m - 1]


# =========================================================
# TG features
# =========================================================
def _derive_tg_features(df):
    # -----------------------------
    # ALWAYS read TG fresh & raw
    # -----------------------------
    if "TG" in df.columns:
        tg = df["TG"].astype(str).copy()
    else:
        tg = pd.Series([""] * len(df), index=df.index)

    # 🚨 Guard against double preprocessing
    # If TG already looks decoded → skip numeric parsing
    decoded_mask = tg.str.contains("female|male", case=False, regex=True)

    # -----------------------------
    # AGE
    # -----------------------------
    ages = tg.map(_extract_age)
    df["age_min"] = ages.map(lambda x: x[0])
    df["age_max"] = ages.map(lambda x: x[1])
    df["age_span"] = df["age_max"] - df["age_min"]

    # -----------------------------
    # GENDER (ONLY from raw TG)
    # -----------------------------
    df["is_female"] = (
        tg.str.match(r"^\s*F\b", case=False) & ~decoded_mask
    ).astype(int)

    df["is_male"] = (
        tg.str.match(r"^\s*M\b", case=False) & ~decoded_mask
    ).astype(int)

    df["is_both_genders"] = (
        (df["is_female"] == 0) & (df["is_male"] == 0)
    ).astype(int)

    # -----------------------------
    # PURCHASING POWER
    # -----------------------------
    pp = tg.str.upper()

    df["pp_high"] = (
        pp.str.contains(r"NCCS\s*AB|ABCDE|HHI\s*TOP", regex=True)
        & ~decoded_mask
    ).astype(int)

    df["pp_medium"] = (
        pp.str.contains(r"NCCS\s*ABC|HHI\s*(?:21|50)", regex=True)
        & ~decoded_mask
    ).astype(int)

    df["pp_low"] = (
        pp.str.contains(r"NCCS\s*CDE|RURAL", regex=True)
        & ~decoded_mask
    ).astype(int)

    df["pp_unknown"] = (
        (df["pp_high"] == 0)
        & (df["pp_medium"] == 0)
        & (df["pp_low"] == 0)
    ).astype(int)

    # -----------------------------
    # LLM-ONLY SUMMARY (SAFE)
    # -----------------------------
    df["tg_summary"] = tg.apply(decode_tg)

    return df


def _extract_age(tg: str):
    match = re.search(r"(\d{2})\s*-\s*(\d{2})", tg)
    if match:
        return float(match.group(1)), float(match.group(2))
    return np.nan, np.nan


# =========================================================
# GEO features
# =========================================================
def mean_tier_from_ids(id_list, tier_lookup):
    if not isinstance(id_list, list) or len(id_list) == 0:
        return np.nan

    tiers = [tier_lookup.get(i) for i in id_list if i in tier_lookup]
    tiers = [t for t in tiers if t is not None]

    if not tiers:
        return np.nan

    return float(np.mean(tiers))

def _derive_geo_features(df, city_tier_lookup=None):
    markets = safe_col(df, "Markets").fillna("").astype(str)
    geo_decoded = markets.apply(decode_markets)

    df["geo_city_ids"] = geo_decoded.map(lambda x: x.get("geo_city_ids", []))
    df["geo_state_ids"] = geo_decoded.map(lambda x: x.get("geo_state_ids", []))

    df["geo_city_count"] = df["geo_city_ids"].map(len)
    df["geo_state_count"] = df["geo_state_ids"].map(len)

    # ✅ FIX: compute avg market tier using lookup
    if city_tier_lookup:
        df["geo_avg_market_tier"] = df["geo_city_ids"].apply(
            lambda ids: mean_tier_from_ids(ids, city_tier_lookup)
        )
    else:
        df["geo_avg_market_tier"] = np.nan

    # final safety
    df["geo_avg_market_tier"] = (
        pd.to_numeric(df["geo_avg_market_tier"], errors="coerce")
        .fillna(2.0)          # default = Tier-2
        .clip(1.0, 3.0)
    )

    return df




# =========================================================
# Device / format features
# =========================================================

def _derive_device_features(df):
    device_col = safe_col(df, "Device", "")
    mobile_ctv_col = (
        safe_col(df, "Mobile / CTV", "")
        .where(safe_col(df, "Mobile / CTV", "") != "", safe_col(df, "Mobile_CTV", ""))
    )

    device_txt = (
        device_col.astype(str)
        + " "
        + mobile_ctv_col.astype(str)
    ).str.lower()

    df["has_nsk"] = device_txt.str.contains("nsk|non[- ]?skip", regex=True).astype(int)
    df["has_sk"] = device_txt.str.contains("skip", regex=True).astype(int)
    df["has_bumper"] = device_txt.str.contains("bumper").astype(int)
    df["has_shorts"] = device_txt.str.contains("short").astype(int)

    df["format_unknown"] = (
        (df["has_nsk"] == 0)
        & (df["has_sk"] == 0)
        & (df["has_bumper"] == 0)
        & (df["has_shorts"] == 0)
    ).astype(int)

    is_ctv = device_txt.str.contains("ctv").astype(int)
    is_mobile = device_txt.str.contains("mobile").astype(int)

    df["is_ctv_only"] = ((is_ctv == 1) & (is_mobile == 0)).astype(int)
    df["is_mobile_only"] = ((is_mobile == 1) & (is_ctv == 0)).astype(int)
    df["is_mixed_device"] = ((is_ctv == 1) & (is_mobile == 1)).astype(int)

    return df



# =========================================================
# Campaign intensity
# =========================================================

def _derive_campaign_intensity(df):

    # Ensure column always exists
    if "campaign_duration_days" not in df.columns:
        df["campaign_duration_days"] = 1

    df["campaign_duration_days"] = (
        pd.to_numeric(df["campaign_duration_days"], errors="coerce")
        .fillna(1)
        .clip(lower=1)
    )

    df["campaign_intensity"] = (
        pd.to_numeric(df.get("Planned Budget"), errors="coerce")
        .fillna(0)
        / df["campaign_duration_days"]
    )

    return df



# =========================================================
# LLM payload
# =========================================================

def _build_llm_payload(df):
    row = df.iloc[0]

    return {
        "TG": row.get("TG"),
        "tg_summary": row.get("tg_summary"),
        "Device": row.get("Device"),
        "Mobile / CTV": row.get("Mobile / CTV"),
        "Markets": row.get("Markets"),
        "geo_summary": row.get("geo_summary"),
        "Start Date": str(row.get("start_date")),
        "End Date": str(row.get("end_date")),
        "campaign_duration_days": int(
            row["campaign_duration_days"]
            if "campaign_duration_days" in row and pd.notna(row["campaign_duration_days"])
            else 1
        ),
        "campaign_intensity": float(row.get("campaign_intensity") or 0.0),
    }
