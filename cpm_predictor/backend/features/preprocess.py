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
# Public API
# =========================================================

def preprocess_input(
    raw_input: Dict[str, Any] | pd.DataFrame,
    feature_columns: List[str],
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Main preprocessing entrypoint.

    Returns
    -------
    X_model : pd.DataFrame
        Single-row dataframe aligned to feature_columns
    X_similarity : pd.DataFrame
        Feature dataframe used for similarity search
    llm_payload : Dict[str, Any]
        Raw + derived human-readable fields for LLM
    """

    df = _normalize_input(raw_input)

    # -----------------------------
    # Derive features
    # -----------------------------
    df = _derive_numeric_features(df)
    df = _derive_time_features(df)
    df = _derive_tg_features(df)
    df = _derive_geo_features(df)
    df = _derive_device_features(df)
    df = _derive_campaign_intensity(df)

    # -----------------------------
    # MODEL FEATURES (STRICT)
    # -----------------------------
    X_model = df.reindex(columns=feature_columns, fill_value=0)

    # -----------------------------
    # SIMILARITY FEATURES
    # (same space as model, but keep summaries)
    # -----------------------------
    similarity_cols = list(set(feature_columns) & set(df.columns))
    similarity_cols += [c for c in df.columns if c.endswith("_summary")]

    X_similarity = df[similarity_cols].copy()

    # -----------------------------
    # LLM PAYLOAD (RAW + DERIVED)
    # -----------------------------
    llm_payload = _build_llm_payload(df)

    return X_model, X_similarity, llm_payload


# =========================================================
# Input normalization
# =========================================================

def _normalize_input(raw_input):
    if isinstance(raw_input, dict):
        df = pd.DataFrame([raw_input])
    elif isinstance(raw_input, pd.DataFrame):
        df = raw_input.copy()
    else:
        raise ValueError("Input must be dict or DataFrame")

    df.columns = [c.strip() for c in df.columns]
    return df


# =========================================================
# Numeric features
# =========================================================

def _derive_numeric_features(df):
    numeric_cols = [
        "Planned Reach 1+",
        "Planned Freq",
        "Planned Budget",
        "Planned Impressions",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df.get(col), errors="coerce")

    return df


# =========================================================
# Time features
# =========================================================

def _derive_time_features(df):
    df["start_date"] = _parse_date(df.get("Start Date"))
    df["end_date"] = _parse_date(df.get("End Date"))

    df["campaign_duration_days"] = (
        df["end_date"] - df["start_date"]
    ).dt.days.clip(lower=1)

    df["start_month"] = df["start_date"].dt.month

    # One-hot months (used in training)
    for m in range(1, 13):
        df[f"is_{_month_name(m)}"] = (df["start_month"] == m).astype(int)

    # Cyclical encoding
    df["start_month_sin"] = np.sin(2 * np.pi * df["start_month"] / 12)
    df["start_month_cos"] = np.cos(2 * np.pi * df["start_month"] / 12)

    return df


def _parse_date(series: pd.Series) -> pd.Series:
    parsed = pd.to_datetime(series, errors="coerce", dayfirst=True)

    mask = parsed.isna()
    if mask.any():
        parsed.loc[mask] = series[mask].apply(_parse_text_date)

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
    tg = df.get("TG").fillna("").astype(str)

    df["age_min"], df["age_max"] = zip(*tg.map(_extract_age))
    df["age_span"] = df["age_max"] - df["age_min"]

    df["is_female"] = tg.str.startswith("F").astype(int)
    df["is_male"] = tg.str.startswith("M").astype(int)
    df["is_both_genders"] = (
        (df["is_female"] == 0) & (df["is_male"] == 0)
    ).astype(int)

    # Purchasing power
    pp = tg.str.upper()

    df["pp_high"] = pp.str.contains(
        r"NCCS\s*AB|ABCDE|HHI\s*TOP", regex=True
    ).astype(int)

    df["pp_medium"] = pp.str.contains(
        r"NCCS\s*ABC|HHI\s*(21|50)", regex=True
    ).astype(int)

    df["pp_low"] = pp.str.contains(
        r"NCCS\s*CDE|RURAL", regex=True
    ).astype(int)

    df["pp_unknown"] = (
        (df["pp_high"] == 0)
        & (df["pp_medium"] == 0)
        & (df["pp_low"] == 0)
    ).astype(int)

    # Human-readable
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

def _derive_geo_features(df):
    geo_decoded = df["Markets"].apply(decode_markets)

    df["geo_city_ids"] = geo_decoded.apply(lambda x: x["geo_city_ids"])
    df["geo_state_ids"] = geo_decoded.apply(lambda x: x["geo_state_ids"])
    df["geo_unknown"] = geo_decoded.apply(lambda x: x["geo_unknown"])

    df["geo_city_count"] = df["geo_city_ids"].apply(len)
    df["geo_state_count"] = df["geo_state_ids"].apply(len)

    df["geo_avg_market_tier"] = geo_decoded.apply(
        lambda x: float(np.mean(x["city_tiers"]))
        if x.get("city_tiers") else 0.0
    )

    df["geo_summary"] = geo_decoded.apply(
        lambda x: ", ".join(x.get("state_names", []))
    )

    return df


# =========================================================
# Device / format features
# =========================================================

def _derive_device_features(df):
    device_txt = (
        df.get("Device", "").fillna("").astype(str)
        + " "
        + df.get("Mobile / CTV", "").fillna("").astype(str)
    ).str.lower()

    df["has_nsk"] = device_txt.str.contains("nsk|non[- ]?skip").astype(int)
    df["has_sk"] = device_txt.str.contains("skip").astype(int)
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
    df["campaign_intensity"] = (
        df["Planned Budget"] / df["campaign_duration_days"]
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
        "campaign_duration_days": int(row.get("campaign_duration_days")),
        "campaign_intensity": float(row.get("campaign_intensity")),
    }
