from backend.llm.tools.tg_tool import run_tg_tool
from backend.llm.tools.geo_tool import run_geo_tool
from backend.llm.tools.seasonality_tool import run_seasonality_tool
from backend.llm.tools.inventory_tool import run_inventory_tool
from backend.llm.tools.brand_tool import run_brand_tool
from backend.llm.tools.residual_context_tool import run_residual_context_tool


def run_llm_reasoning(
    raw_input: dict,
    model_output: dict,
    similarity_output: list,
    decoded_tg: str
):
    model_context = {
        "model_prediction": model_output,
        "decoded_tg": decoded_tg
    }

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

    # Aggregate adjustments
    adjustment_factor = 1.0
    impacts = []

    for res in tool_results:
        adjustment_factor *= res.get("adjustment_factor", 1.0)
        impacts.append(res)

    base = model_output
    llm_low = base["low"] * adjustment_factor
    llm_mid = base["mid"] * adjustment_factor
    llm_high = base["high"] * adjustment_factor

    return {
        "llm_predicted_cpm": {
            "low": llm_low,
            "mid": llm_mid,
            "high": llm_high
        },
        "tool_impacts": impacts,
        "explanation": "LLM adjusted CPM based on market, audience and seasonal context.",
        "confidence_note": f"Base model confidence: {base['confidence']:.2f}"
    }
