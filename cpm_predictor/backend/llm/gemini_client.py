# backend/llm/gemini_client.py
import os
from dotenv import load_dotenv
from google import genai

load_dotenv(override=True)

CLIENT = None
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    CLIENT = genai.Client(api_key=api_key)


def call_gemini(prompt: str) -> dict:
    if CLIENT is None:
        raise RuntimeError("Gemini client not initialized")

    response = CLIENT.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )

    return response.text
