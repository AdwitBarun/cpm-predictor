import os
import pandas as pd
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# -------------------------------------------------
# Paths
# -------------------------------------------------
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

GEO_DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "geotargets-2025-10-29.csv"
)

# -------------------------------------------------
# In-memory lookup tables
# -------------------------------------------------
_geo_name_to_id = {}
_geo_id_to_name = {}
_initialized = False


# -------------------------------------------------
# Initialization (lazy, safe)
# -------------------------------------------------
def _initialize():
    global _initialized, _geo_name_to_id, _geo_id_to_name

    if _initialized:
        return

    if not os.path.exists(GEO_DATA_PATH):
        raise FileNotFoundError(f"Geo data file not found: {GEO_DATA_PATH}")

    df = pd.read_csv(GEO_DATA_PATH)

    required_cols = {"Criteria ID", "Name"}
    if not required_cols.issubset(df.columns):
        raise ValueError(
            f"Geo CSV must contain columns {required_cols}, found {df.columns}"
        )

    for _, row in df.iterrows():
        cid = row.get("criteria_id")
        name = row.get("name")

        if not isinstance(name, str):
            continue  # skip NaN / floats / bad rows

        name_clean = name.strip().lower()
        if not name_clean:
            continue

        cid_str = str(cid)

        _geo_name_to_id[name_clean] = cid_str
        _geo_id_to_name[cid_str] = name_clean

    _initialized = True

    logger.info(
        "Loaded %d geo targets from %s",
        len(_geo_name_to_id),
        GEO_DATA_PATH,
    )


# -------------------------------------------------
# Encode: NAMES → GEO IDS (ML)
# -------------------------------------------------
def encode_geography(geo_names) -> str:
    _initialize()

    if not geo_names or not isinstance(geo_names, str):
        return ""

    names = [
        n.strip().lower()
        for n in geo_names.split(";")
        if isinstance(n, str) and n.strip()
    ]

    codes = [
        _geo_name_to_id[n]
        for n in names
        if n in _geo_name_to_id
    ]

    return ";".join(codes)


# -------------------------------------------------
# Decode: GEO IDS → NAMES (LLM)
# -------------------------------------------------
def decode_geography(geo_codes: Optional[str]) -> List[str]:
    _initialize()

    if not geo_codes or not isinstance(geo_codes, str):
        return []

    return [
        _geo_id_to_name.get(code.strip(), f"Unknown({code.strip()})")
        for code in geo_codes.split(";")
        if code.strip()
    ]
