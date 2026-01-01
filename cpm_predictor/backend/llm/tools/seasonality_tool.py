from backend.llm.prompts import tool_prompt
from backend.llm.gemini_client import call_gemini


def run_seasonality_tool(raw_input: dict):
    payload = {
        "start_date": raw_input.get("Start Date"),
        "end_date": raw_input.get("End Date"),
        "market": "India"
    }

    prompt = tool_prompt(
        "seasonality_tool",
        "Analyze seasonal demand including festivals and global events.",
        payload
    )

    return call_gemini(prompt)
