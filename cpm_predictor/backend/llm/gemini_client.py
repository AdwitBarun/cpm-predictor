import os
from typing import Dict, Any, Tuple, List

from dotenv import load_dotenv
from google import genai

from cpm_predictor.backend.llm.prompts import (
    build_gemini_prompt,
    parse_gemini_response,
)

# -------------------------------------------------
# Load env
# -------------------------------------------------
load_dotenv(override=True)

CLIENT = None
try:
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        CLIENT = genai.Client(api_key=api_key)
except Exception as e:
    print(f"⚠️ Gemini init failed: {e}")


# -------------------------------------------------
# Public API
# -------------------------------------------------
def gemini_range(
    features: Dict[str, Any],
    historical_range: Tuple[float, float, float],
    shap_summary: List[Tuple[str, float]],  # kept for future extension
) -> Dict[str, Any]:

    p10, p50, p90 = historical_range

    if CLIENT is None:
        return fallback(p10, p90, "Gemini unavailable")

    try:
        prompt = build_gemini_prompt(
            input_data=features,
            historical_range={"p10": p10, "p50": p50, "p90": p90},
            decoded_geo=features.get("decoded_geo", []),
        )

        response = CLIENT.models.generate_content(
            model="gemini-1.5-pro",
            contents=prompt,
        )

        parsed = parse_gemini_response(response.text)
        adj = parsed["adjusted_range"]

        return {
            "low": float(adj["low"]),
            "high": float(adj["high"]),
            "explanation": parsed["explanation"],
            "key_factors": parsed.get("key_factors", []),
        }

    except Exception as e:
        return fallback(p10, p90, str(e))


def fallback(low: float, high: float, reason: str) -> Dict[str, Any]:
    return {
        "low": low,
        "high": high,
        "explanation": f"Fallback to ML CPM range. Reason: {reason}",
        "key_factors": [],
    }
