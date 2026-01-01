from backend.llm.prompts import tool_prompt
from backend.llm.gemini_client import call_gemini


def run_inventory_tool(raw_input: dict):
    payload = {
        "Device": raw_input.get("Device"),
        "Mobile/CTV": raw_input.get("Mobile / CTV"),
        "Format": raw_input.get("Video_Ad_Format")
    }

    prompt = tool_prompt(
        "inventory_tool",
        "Analyze inventory scarcity and device pressure.",
        payload
    )

    return call_gemini(prompt)
