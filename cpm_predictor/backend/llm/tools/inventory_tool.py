from cpm_predictor.backend.llm.prompts import tool_prompt
from cpm_predictor.backend.llm.gemini_client import call_gemini

task = """
Evaluate inventory supply and demand pressure.

Consider:
- CTV inventory is scarcer than mobile and often commands premium CPM.
- Non-skippable formats generally increase CPM.
- Mixed device campaigns usually normalize CPM.
- High planned frequency or reach can increase bid pressure.

Inventory effects are typically incremental, not dominant.
"""

def run_inventory_tool(raw_input: dict):
    payload = {
        "Device": str(raw_input.get("Device", "")),
        "Mobile/CTV": str(raw_input.get("Mobile / CTV", "")),
        "Format": str(raw_input.get("Video_Ad_Format", ""))
    }

    prompt = tool_prompt(
        "inventory_tool",
        task,
        payload
    )

    return call_gemini(prompt)

