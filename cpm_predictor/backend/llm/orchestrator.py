from cpm_predictor.backend.llm.tools.tg_tool import run_tg_tool
from cpm_predictor.backend.llm.tools.geo_tool import run_geo_tool
from cpm_predictor.backend.llm.tools.seasonality_tool import run_seasonality_tool
from cpm_predictor.backend.llm.tools.inventory_tool import run_inventory_tool
from cpm_predictor.backend.llm.tools.brand_tool import run_brand_tool
from cpm_predictor.backend.llm.tools.residual_context_tool import run_residual_context_tool


def run_llm_reasoning(
    raw_input: dict,
    model_output: dict,
    similarity_output: list,
    decoded_tg: str
):
    """
    LLM reasoning layer that adjusts ML CPM range using tool-based context.
    """

    # -------------------------------------------------
    # 1️⃣ Normalize model output → base CPM range
    # -------------------------------------------------
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

    # -------------------------------------------------
    # 2️⃣ Run tools
    # -------------------------------------------------
    tool_results = []

    tool_results.append(run_tg_tool(raw_input, model_context))
    tool_results.append(run_geo_tool(raw_input, similarity_output))
    tool_results.append(run_seasonality_tool(raw_input))
    tool_results.append(run_inventory_tool(raw_input))
    tool_results.append(run_brand_tool(raw_input))

    used_keys = [
        "TG", "Markets", "Device", "Mobile / CTV",
        "Start Date", "End Date", "Campaign Name", "Advertiser"
    ]

    tool_results.append(
        run_residual_context_tool(raw_input, used_keys)
    )

    # -------------------------------------------------
    # 3️⃣ Aggregate multiplicative adjustments
    # -------------------------------------------------
    adjustment_factor = 1.0
    impacts = []

    for res in tool_results:
        adjustment_factor *= res.get("adjustment_factor", 1.0)
        impacts.append(res)

    # -------------------------------------------------
    # 4️⃣ Apply adjustment
    # -------------------------------------------------
    llm_low = round(base_range["low"] * adjustment_factor, 2)
    llm_mid = round(base_range["mid"] * adjustment_factor, 2)
    llm_high = round(base_range["high"] * adjustment_factor, 2)

    # -------------------------------------------------
    # 5️⃣ Final response
    # -------------------------------------------------
    return {
        "llm_predicted_cpm": {
            "low": llm_low,
            "mid": llm_mid,
            "high": llm_high,
        },
        "base_model_range": base_range,
        "adjustment_factor": round(adjustment_factor, 3),
        "tool_impacts": impacts,
        "explanation": (
            "LLM adjusted CPM based on audience quality, geography, "
            "seasonality, inventory pressure, and brand context."
        ),
        "confidence_note": (
            f"Base model conformal coverage: "
            f"{base_range['confidence']:.2f}"
        ),
    }
