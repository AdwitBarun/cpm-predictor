from typing import Dict, Any, List
import logging
import json
import re
from datetime import datetime

from cpm_predictor.backend.llm.utils import (
    decode_tg,
    get_seasonal_factors,
    get_tg_premium_factor,
)

logger = logging.getLogger(__name__)


def build_gemini_prompt(
    input_data: Dict[str, Any],
    historical_range: Dict[str, float],
    decoded_geo: List[str],
) -> str:

    tg = input_data.get("TG", "Not specified")
    device = input_data.get("Device", "Not specified")
    inventory_mode = input_data.get("Inventory_Mode", "Standard")
    ad_format = input_data.get("Video_Ad_Format", "Not specified")
    month_range = input_data.get("month_range", "Not specified")

    tg_description = decode_tg(tg)

    current_month = datetime.now().strftime("%B")

    return f"""
You are an experienced ad-tech media strategist with deep knowledge of programmatic advertising.

Campaign Details:
- Target Group (TG): {tg} (Decoded: {tg_description})
- Device: {device}
- Inventory Mode: {inventory_mode}
- Video Ad Format: {ad_format}
- Month Range: {month_range} (Current Month: {current_month})
- Geography: {", ".join(decoded_geo) if decoded_geo else "Global"}

Historical CPM Range:
- Low: ${historical_range["p10"]:.2f}
- Mid: ${historical_range["p50"]:.2f}
- High: ${historical_range["p90"]:.2f}

Market Context:
- Seasonal Factors: {get_seasonal_factors(month_range, current_month)}
- Inventory Pressure: {"High" if inventory_mode.lower() == "limited" else "Moderate"}
- TG Premium Factor: {get_tg_premium_factor(tg)}

Return ONLY valid JSON:

{{
  "adjusted_range": {{
    "low": number,
    "mid": number,
    "high": number
  }},
  "explanation": string,
  "key_factors": [
    {{ "factor": string, "impact": "positive|negative|neutral", "effect": string }}
  ]
}}
""".strip()


def parse_gemini_response(text: str) -> Dict[str, Any]:
    try:
        data = safe_json(text)

        if "adjusted_range" not in data:
            raise ValueError("Missing adjusted_range")

        for k in ("low", "mid", "high"):
            if k not in data["adjusted_range"]:
                raise ValueError(f"Missing adjusted_range.{k}")

        return data

    except Exception as e:
        logger.error(f"Gemini response parse failed: {e}")
        raise


def safe_json(text: str) -> Dict[str, Any]:
    """
    Robust JSON extractor for LLM output.
    """
    if not text or not text.strip():
        raise ValueError("Empty Gemini response")

    text = re.sub(r"```json|```", "", text, flags=re.IGNORECASE).strip()

    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError(f"No JSON found in response: {text[:200]}")

    return json.loads(match.group())
