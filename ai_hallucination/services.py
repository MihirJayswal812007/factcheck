import os
import asyncio
import json
import google.generativeai as genai
from typing import List, AsyncGenerator
from tenacity import retry, wait_exponential, stop_after_attempt

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use Flash for better reliability on Render
model = genai.GenerativeModel('gemini-2.0-flash')
sem = asyncio.Semaphore(2)

class AIService:
    @staticmethod
    @retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
    async def analyze_text(text: str):
        prompt = f"""
        Analyze for factual accuracy. Return ONLY a raw JSON object. 
        Do not include markdown or backticks.
        {{ "score": 0-100, "summary": "...", "claims": [], "citations": [] }}
        Text: {text}
        """
        async with sem:
            response = await model.generate_content_async(prompt)
            # Remove any markdown backticks the AI might add
            text_response = response.text.strip().replace("```json", "").replace("```", "")
            return text_response

    @staticmethod
    async def stream_chat(history: List[dict], user_message: str) -> AsyncGenerator[str, None]:
        chat = model.start_chat(history=history)
        response = await chat.send_message_async(user_message, stream=True)
        async for chunk in response:
            yield chunk.text