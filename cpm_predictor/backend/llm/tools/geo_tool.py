from cpm_predictor.backend.llm.prompts import tool_prompt
from cpm_predictor.backend.llm.gemini_client import call_gemini

task = """
Evaluate how geographic targeting affects CPM.

Consider:
- Metro and Tier-1 cities generally have higher CPMs.
- Mixed metro + non-metro markets tend to normalize CPM.
- If historical similar campaigns in these markets show
  consistent CPM uplift or suppression, reflect that.
- Geography alone rarely shifts CPM more than ±15%.

Prefer historical delivered CPMs over assumptions.
"""


def run_geo_tool(raw_input: dict, similar_campaigns: list):
    payload = {
        "Markets": raw_input.get("Markets"),
        "similar_campaigns": similar_campaigns  # treat as LIST
    }

    prompt = tool_prompt(
        "geo_tool",
        task,
        payload
    )

    return call_gemini(prompt)

