import os
import asyncio
import google.generativeai as genai
from typing import List, AsyncGenerator
from tenacity import retry, wait_exponential, stop_after_attempt

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-pro')

# Concurrency Limit: Default 2 concurrent requests
sem = asyncio.Semaphore(2)

class AIService:
    @staticmethod
    @retry(wait=wait_exponential(multiplier=1, min=2, max=128), stop=stop_after_attempt(7))
    async def analyze_text(text: str):
        prompt = f"""
        Analyze for factual accuracy and citations. Return JSON only:
        {{ "score": 0-100, "summary": "...", 
           "claims": [{{ "text": "...", "status": "verified|questionable|false", "reason": "..." }}],
           "citations": [{{ "text": "...", "status": "valid|invalid|unknown", "reason": "..." }}] }}
        Text: {text}
        """
        async with sem:
            response = await model.generate_content_async(prompt)
            return response.text

    @staticmethod
    async def stream_chat(history: List[dict], user_message: str) -> AsyncGenerator[str, None]:
        # Implementation of Streaming Pattern
        chat = model.start_chat(history=history)
        response = await chat.send_message_async(user_message, stream=True)
        async for chunk in response:
            yield chunk.text