from typing import Dict, Any, List
import logging
from datetime import datetime
import json

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

    historical_low = historical_range.get("p10", 0.0)
    historical_mid = historical_range.get("p50", 0.0)
    historical_high = historical_range.get("p90", 0.0)

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

Historical CPM Range (Based on similar campaigns):
- 10th Percentile (Low): ${historical_low:.2f}
- 50th Percentile (Median): ${historical_mid:.2f}
- 90th Percentile (High): ${historical_high:.2f}

Market Context:
- Seasonal Factors: {get_seasonal_factors(month_range, current_month)}
- Inventory Pressure: {"High" if inventory_mode.lower() == "limited" else "Moderate"}
- TG Premium Factor: {get_tg_premium_factor(tg)}

Task:
Return ONLY valid JSON (no markdown, no explanations outside JSON):

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
        if "```" in text:
            text = text.split("```")[1]

        result = json.loads(text)

        if not all(k in result["adjusted_range"] for k in ("low", "mid", "high")):
            raise ValueError("Missing adjusted_range keys")

        return result

    except Exception as e:
        logger.error(f"Gemini response parse failed: {e}")
        raise
