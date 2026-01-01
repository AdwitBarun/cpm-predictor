# backend/features/geo_decoder.py

import os
import re
import pandas as pd
import numpy as np
from difflib import SequenceMatcher
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

# =========================================================
# Paths
# =========================================================
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

GEO_DATA_PATH = os.path.join(
    BASE_DIR, "data", "geotargets-2025-10-29.csv"
)

# =========================================================
# In-memory caches
# =========================================================
_initialized = False
cities_df = None
states_df = None

city_lookup = {}
state_lookup = {}
canonical_state_lookup = {}

# =========================================================
# Hardcoded planner vocabulary (from your notebook)
# =========================================================
HARDCODE_MARKETS = {
    "up": [20471],
    "uttarpradesh": [20471],
    "wb": [20472],
    "westbengal": [20472],
    "mah": [20473],
    "mpcg": [20464, 21334],          # MP + Chhattisgarh
    "bih+jk": [20455, 21336],        # Bihar + Jharkhand
    "bih + jk": [20455, 21336],
    "aptl": [20453, 20454],          # AP + Telangana
    "ap+tl": [20453, 20454],
    "up+utt": [20471, 2356],         # UP + Uttarakhand
}

COMMENTARY_KEYWORDS = [
    "refer", "saving", "billing", "media plan"
]

# =========================================================
# Initialization (lazy)
# =========================================================
def _initialize():
    global _initialized
    global cities_df, states_df
    global city_lookup, state_lookup, canonical_state_lookup

    if _initialized:
        return

    if not os.path.exists(GEO_DATA_PATH):
        raise FileNotFoundError(f"Geo CSV not found: {GEO_DATA_PATH}")

    geo = pd.read_csv(GEO_DATA_PATH)
    geo.columns = geo.columns.str.lower()

    # India only
    geo = geo[geo["country code"] == "IN"].copy()

    # Exclude country row
    geo = geo[geo["canonical name"].str.lower() != "india"]

    # Split
    cities_df = geo[geo["parent id"].notna()].copy()
    states_df = geo[geo["parent id"].isna()].copy()

    cities_df["name_norm"] = cities_df["name"].str.lower().str.strip()
    states_df["name_norm"] = states_df["name"].str.lower().str.strip()
    states_df["canonical_norm"] = (
        states_df["canonical name"].str.lower().str.strip()
    )

    # Lookups
    city_lookup = {
        r["name_norm"]: (int(r["criteria id"]), int(r["parent id"]))
        for _, r in cities_df.iterrows()
        if isinstance(r["name_norm"], str)
    }

    state_lookup = {
        r["name_norm"]: int(r["criteria id"])
        for _, r in states_df.iterrows()
        if isinstance(r["name_norm"], str)
    }

    canonical_state_lookup = {
        r["canonical_norm"]: int(r["criteria id"])
        for _, r in states_df.iterrows()
        if isinstance(r["canonical_norm"], str)
    }

    _initialized = True
    logger.info("Geo decoder initialized (%d states, %d cities)",
                len(state_lookup), len(city_lookup))


# =========================================================
# Helpers
# =========================================================
def _tokenize(text: str) -> set:
    return set(
        re.sub(r"[^a-z0-9+ ]", " ", text.lower()).split()
    )


def _fuzzy_match_state(text: str, threshold: float = 0.9):
    best_score = 0
    best_id = None

    for canon, sid in canonical_state_lookup.items():
        score = SequenceMatcher(None, text, canon).ratio()
        if score > best_score:
            best_score = score
            best_id = sid

    if best_score >= threshold:
        return best_id

    return None


# =========================================================
# PUBLIC API
# =========================================================
def decode_markets(market_value: str) -> Dict[str, Any]:
    """
    Decode Markets column into structured geo features.

    Output schema MUST stay stable:
    - geo_city_ids
    - geo_state_ids
    - geo_unknown
    - city_tiers
    - state_names
    """

    _initialize()

    result = {
        "geo_city_ids": [],
        "geo_state_ids": [],
        "geo_unknown": 0,
        "city_tiers": [],
        "state_names": [],
    }

    # -----------------------------
    # Missing / NaN
    # -----------------------------
    if not market_value or not isinstance(market_value, str):
        result["geo_unknown"] = 1
        return result

    v = market_value.lower()

    # -----------------------------
    # Commentary rows
    # -----------------------------
    if any(k in v for k in COMMENTARY_KEYWORDS):
        result["geo_unknown"] = 1
        return result

    # -----------------------------
    # Hardcoded overrides
    # -----------------------------
    compact = v.replace(" ", "")
    if compact in HARDCODE_MARKETS:
        state_ids = HARDCODE_MARKETS[compact]
        result["geo_state_ids"] = state_ids
        result["state_names"] = [
            name for name, sid in state_lookup.items()
            if sid in state_ids
        ]
        return result

    tokens = _tokenize(v)
    tokens.add("".join(tokens))

    city_ids = set()
    state_ids = set()

    # -----------------------------
    # City detection
    # -----------------------------
    for name, (cid, sid) in city_lookup.items():
        if name in v:
            city_ids.add(cid)
            state_ids.add(sid)

    # -----------------------------
    # State detection (exact)
    # -----------------------------
    for t in tokens:
        if t in state_lookup:
            state_ids.add(state_lookup[t])

    # -----------------------------
    # Fuzzy fallback (canonical name)
    # -----------------------------
    if not city_ids and not state_ids:
        clean = re.sub(r"[^a-z ]", " ", v)
        clean = re.sub(r"\s+", " ", clean).strip()
        sid = _fuzzy_match_state(clean)
        if sid:
            state_ids.add(sid)

    # -----------------------------
    # Finalize
    # -----------------------------
    result["geo_city_ids"] = sorted(city_ids)
    result["geo_state_ids"] = sorted(state_ids)

    if not city_ids and not state_ids:
        result["geo_unknown"] = 1

    # State names (for LLM)
    result["state_names"] = [
        name for name, sid in state_lookup.items()
        if sid in state_ids
    ]

    # AVERAGE TIER (if you add tier mapping later)
    result["city_tiers"] = []

    return result
