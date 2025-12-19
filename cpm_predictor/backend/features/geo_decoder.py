import os
import pandas as pd
from typing import List, Dict, Optional, Union
import logging

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

GEO_DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "geotargets-2025-10-29.csv"
)

_geo_id_to_name = {}
_geo_name_to_id = {}
_initialized = False


def _initialize():
    global _geo_id_to_name, _geo_name_to_id, _initialized

    if _initialized:
        return

    df = pd.read_csv(GEO_DATA_PATH)

    _geo_id_to_name = dict(
        zip(df["criteria_id"].astype(str), df["name"].str.lower())
    )

    _geo_name_to_id = {
        name.lower(): str(cid)
        for cid, name in zip(df["criteria_id"], df["name"])
    }

    _initialized = True


def encode_geography(geo_names: Optional[str]) -> str:
    """
    Convert geography NAMES → semicolon-separated GEO CODES (for ML)
    """
    _initialize()

    if not geo_names:
        return ""

    names = [n.strip().lower() for n in geo_names.split(";")]
    codes = [
        _geo_name_to_id[n]
        for n in names
        if n in _geo_name_to_id
    ]

    return ";".join(codes)


def decode_geography(geo_codes: Optional[str]) -> List[str]:
    """
    Convert GEO CODES → NAMES (for LLM)
    """
    _initialize()

    if not geo_codes:
        return []

    return [
        _geo_id_to_name.get(c.strip(), f"Unknown({c.strip()})")
        for c in geo_codes.split(";")
    ]
