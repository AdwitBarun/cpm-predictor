from cpm_predictor.backend.llm.prompts import tool_prompt
from cpm_predictor.backend.llm.gemini_client import call_gemini

task = """
Evaluate brand and campaign context.

Consider:
- Well-known brands may face higher competition in auctions.
- Large seasonal campaigns may drive CPM up.
- Negative or uncertain brand news should not be assumed unless evident.

If brand context is unclear, remain neutral.
"""

def run_brand_tool(raw_input: dict):
    payload = {
        "campaign_name": str(raw_input.get("Campaign Name", "")),
        "advertiser": str(raw_input.get("Advertiser", ""))
    }

    prompt = tool_prompt(
        "brand_tool",
        task,
        payload
    )

    return call_gemini(prompt)
