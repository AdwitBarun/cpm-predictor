import os
import json
import re
from typing import Dict, Any, Tuple, List

from dotenv import load_dotenv
from google import genai

# -------------------------------------------------
# Load environment variables
# -------------------------------------------------
load_dotenv(override=True)

# -------------------------------------------------
# Initialize Gemini client (NEW SDK – CORRECT)
# -------------------------------------------------
try:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")

    CLIENT = genai.Client(api_key=api_key)

except Exception as e:
    print(f"⚠️ Gemini client init failed: {e}")
    CLIENT = None


# -------------------------------------------------
# Main Gemini range function
# -------------------------------------------------
def gemini_range(
    features: Dict[str, Any],
    historical_range: Tuple[float, float, float],
    shap_summary: List[Tuple[str, float]],
) -> Dict[str, Any]:
    """
    Get LLM-enhanced CPM range prediction.
    """
    p10, p50, p90 = historical_range

    # Hard fallback if Gemini unavailable
    if CLIENT is None:
        return {
            "low": p10,
            "high": p90,
            "explanation": "Gemini unavailable — using historical CPM range.",
        }

    try:
        prompt = build_prompt(features, historical_range, shap_summary)

        response = CLIENT.models.generate_content(
            model="gemini-2.0-flash",
            contents=[{
                "role": "user",
                "parts": [{"text": prompt}]
            }],
        )

        raw_text = response.text
        result = safe_json(raw_text)

        # Validate structure
        if not all(k in result for k in ("low", "high", "explanation")):
            raise ValueError(f"Invalid Gemini response keys: {result}")

        return {
            "low": float(result["low"]),
            "high": float(result["high"]),
            "explanation": str(result["explanation"]),
        }

    except Exception as e:
        print(f"❌ Error in gemini_range: {e}")
        return {
            "low": p10,
            "high": p90,
            "explanation": "Gemini error — falling back to historical CPM range.",
        }


# -------------------------------------------------
# Prompt builder
# -------------------------------------------------
def build_prompt(
    features: Dict[str, Any],
    historical_range: Tuple[float, float, float],
    shap_summary: List[Tuple[str, float]],
) -> str:
    p10, p50, p90 = historical_range

    top_features = "\n".join(
        f"- {feat}: {imp:.4f}" for feat, imp in shap_summary[:5]
    )

    return f"""
You are a senior media buying expert.

Historical CPM Range:
- P10: {p10:.2f}
- P50: {p50:.2f}
- P90: {p90:.2f}

Campaign Details:
- Device: {features.get('Device', 'N/A')}
- Target Group: {features.get('TG', 'N/A')}
- Geography: {features.get('Geography_Targeting_Include', 'N/A')}
- Budget: {features.get('Planned_Budget', 'N/A')}
- Impressions: {features.get('Planned_Impressions', 'N/A')}
- Frequency: {features.get('Planned_Freq', 'N/A')}
- Inventory Mode: {features.get('Inventory_Mode', 'N/A')}
- Ad Format: {features.get('Video_Ad_Format', 'N/A')}
- Month Range: {features.get('month_range', 'N/A')}
- Campaign Duration: {features.get('campaign_duration_days', 'N/A')} days

Top Influential Features:
{top_features}

STRICT INSTRUCTIONS:
- Respond with ONLY valid JSON
- No markdown
- No explanations outside JSON
- No backticks

Return EXACTLY this format:
{{
  "low": number,
  "high": number,
  "explanation": string
}}
""".strip()


# -------------------------------------------------
# Safe JSON parsing (ROBUST)
# -------------------------------------------------
def safe_json(text: str) -> Dict[str, Any]:
    """
    Safely extract JSON object from LLM output.
    """
    if not text:
        raise ValueError("Empty Gemini response")

    text = text.strip()

    # Remove markdown fences
    text = re.sub(r"```json|```", "", text).strip()

    # Extract first JSON object
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON found in Gemini output: {text[:200]}")

    return json.loads(match.group())
