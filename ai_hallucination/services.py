import os
import asyncio
import google.generativeai as genai
from tenacity import retry, wait_exponential, stop_after_attempt

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ✅ VALID MODEL NAME
model = genai.GenerativeModel("gemini-1.5-flash")

sem = asyncio.Semaphore(2)

class AIService:

    @staticmethod
    @retry(wait=wait_exponential(min=2, max=10), stop=stop_after_attempt(3))
    async def analyze_text(text: str) -> str:
        prompt = f"""
Analyze the following text for factual accuracy.
Return ONLY raw JSON. No markdown.

{{
  "score": 0-100,
  "summary": "string",
  "claims": [],
  "citations": []
}}

Text:
{text}
"""
        async with sem:
            response = await model.generate_content_async(prompt)
            return response.text.strip().replace("```json", "").replace("```", "")
