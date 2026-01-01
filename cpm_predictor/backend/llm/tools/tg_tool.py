from backend.llm.prompts import tool_prompt
from backend.llm.gemini_client import call_gemini

task = """
Evaluate how the target group's age, gender, and socio-economic indicators
typically affect CPM in programmatic video buying.

Consider:
- Working-age cohorts (25–44) often command premium CPMs.
- Female skewed audiences may attract brand advertisers.
- High purchasing power audiences (NCCS AB / HHI Top segments)
  usually increase CPM but only if inventory is competitive.

Do NOT over-adjust unless historical evidence supports it.
"""

def run_tg_tool(raw_input: dict, model_context: dict):
    payload = {
        "TG": raw_input.get("TG"),
        "decoded_TG": model_context.get("decoded_tg"),
        "model_range": model_context["model_prediction"]
    }

    prompt = tool_prompt(
        "tg_tool",
        task,
        payload
    )

    return call_gemini(prompt)
