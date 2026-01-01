from cpm_predictor.backend.llm.prompts import tool_prompt
from cpm_predictor.backend.llm.gemini_client import call_gemini

task = """
Review remaining campaign attributes not covered by other tools.

Consider:
- Budget scale anomalies
- Unusual combinations of inputs
- Operational constraints

Only suggest adjustment if there is a clear, logical reason.
Otherwise, remain neutral.
"""

def run_residual_context_tool(raw_input: dict, used_keys: list):
    residual_data = {
        k: v for k, v in raw_input.items()
        if k not in used_keys
    }

    payload = {
        "residual_columns": residual_data
    }

    prompt = tool_prompt(
        "residual_context_tool",
        task,
        payload
    )

    return call_gemini(prompt)
