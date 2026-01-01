from backend.llm.prompts import tool_prompt
from backend.llm.gemini_client import call_gemini


def run_geo_tool(raw_input: dict, similarity_context: dict):
    payload = {
        "Markets": raw_input.get("Markets"),
        "similar_campaigns": similarity_context
    }

    prompt = tool_prompt(
        "geo_tool",
        "Analyze geography purchasing power and market demand.",
        payload
    )

    return call_gemini(prompt)
