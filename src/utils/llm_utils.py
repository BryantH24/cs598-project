"""
Call Gemini API Utility Function
"""

from google import genai
from google.genai import types

API_KEY = ""
MODEL_NAME = "gemini-flash-latest"

def call_gemini_api(prompt):
    try:
        client = genai.Client(api_key=API_KEY)

        grounding_tool = types.Tool(google_search=types.GoogleSearch())
        config = types.GenerateContentConfig(tools=[grounding_tool])

        resp = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=config,
        )

        api_result = resp.text.strip()

        if resp.candidates:
            grounding_metadata = resp.candidates[0].grounding_metadata
            used_search = bool(grounding_metadata)
        else:
            used_search = False

        api_result = api_result.strip('"\'')
        return api_result, used_search

    except Exception as e:
        print(f"API Error: {e}")
        return "API_ERROR", False
