from cpm_predictor.backend.llm.tools.tg_tool import run_tg_tool
from cpm_predictor.backend.llm.tools.geo_tool import run_geo_tool
from cpm_predictor.backend.llm.tools.seasonality_tool import run_seasonality_tool
from cpm_predictor.backend.llm.tools.inventory_tool import run_inventory_tool
from cpm_predictor.backend.llm.tools.brand_tool import run_brand_tool
from cpm_predictor.backend.llm.tools.residual_context_tool import run_residual_context_tool
from cpm_predictor.backend.llm.utils import decode_tg


import numpy as np
import json
import re

# -------------------------------------------------
# Helper: extract factor from LLM JSON explanation
# -------------------------------------------------
def extract_adjustment_factor(tool_response):
    try:
        text = tool_response.get("explanation", "")
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return 1.0

        payload = json.loads(match.group())
        return float(payload.get("adjustment_factor", 1.0))
    except Exception:
        return 1.0


# -------------------------------------------------
# Main LLM reasoning
# -------------------------------------------------
def run_llm_reasoning(
    raw_input: dict,
    model_output: dict,
    similarity_output: list,
):
    decoded_tg = decode_tg(raw_input.get("TG"))

    model_range = model_output["model_range"]
    conformal_range = model_output["conformal_range"]

    base_range = {
        "low": conformal_range["low"],
        "mid": model_range["p50"],
        "high": conformal_range["high"],
        "confidence": conformal_range.get("coverage_target", 0.9),
    }

    model_context = {
        "model_prediction": base_range,
        "decoded_tg": decoded_tg,
        "similar_campaigns": similarity_output,
    }

    # -----------------------------
    # Run tools safely
    # -----------------------------
    tool_results = []

    tools = [
        run_tg_tool,
        lambda x: run_geo_tool(x, similarity_output),
        run_seasonality_tool,
        run_inventory_tool,
        run_brand_tool,
    ]

    for tool in tools:
        try:
            res = tool(raw_input)
        except TypeError:
            res = tool(raw_input, model_context)

        if not isinstance(res, dict):
            res = {
                "adjustment_factor": 1.0,
                "explanation": str(res)
            }

        tool_results.append(res)

    # -----------------------------
    # 🔥 CORE: aggregate LLM belief
    # -----------------------------
    raw_factors = [
        extract_adjustment_factor(res)
        for res in tool_results
    ]

    llm_adjustment_factor = float(np.prod(raw_factors))

    # 🔒 INDUSTRY SAFETY CLAMP
    llm_adjustment_factor = max(0.90, min(1.15, llm_adjustment_factor))

    # -----------------------------
    # Apply adjustment
    # -----------------------------
    llm_low = round(base_range["low"] * llm_adjustment_factor, 2)
    llm_mid = round(base_range["mid"] * llm_adjustment_factor, 2)
    llm_high = round(base_range["high"] * llm_adjustment_factor, 2)

    return {
        "llm_predicted_cpm": {
            "low": llm_low,
            "mid": llm_mid,
            "high": llm_high,
        },
        "base_model_range": base_range,
        "adjustment_factor": round(llm_adjustment_factor, 3),
        "tool_impacts": tool_results,
        "explanation": (
            "LLM adjusted CPM using audience quality, geography, "
            "seasonality, inventory pressure, and brand context."
        ),
        "confidence_note": (
            f"Base model conformal coverage: "
            f"{base_range['confidence']:.2f}"
        ),
    }
