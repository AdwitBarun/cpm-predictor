from cpm_predictor.backend.llm.prompts import tool_prompt
from cpm_predictor.backend.llm.gemini_client import call_gemini

task = """
Evaluate seasonal demand effects on CPM.

Consider Indian market specifics:
- Festive periods (Diwali, Navratri, Dussehra, Christmas, New Year)
  typically increase CPM due to advertiser competition.
- IPL season often causes sharp CPM inflation on video inventory.
- Election periods may increase volatility but not always CPM.
- Non-festive months usually remain neutral.

If the campaign dates overlap with known high-demand periods,
apply a moderate adjustment. Otherwise, remain neutral.
"""

def run_seasonality_tool(raw_input: dict):
    payload = {
        "start_date": str(raw_input.get("Start Date", "")),
        "end_date": str(raw_input.get("End Date", "")),
        "market": "India"
    }

    prompt = tool_prompt(
        "seasonality_tool",
        task,
        payload
    )

    return call_gemini(prompt)

