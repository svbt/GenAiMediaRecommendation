import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings
import json

class LLMClient:
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_recommendations(self, prompt: str) -> dict:
        if settings.ENV == "local":
            # Mock response for local dev
            return {
                "response": json.dumps([
                    {"contentId": "m-789", "score": 0.98, "reason": "Sci-fi thriller"},
                    {"contentId": "m-234", "score": 0.85, "reason": "Sci-fi epic"}
                ])
            }
        response = requests.post(settings.OLLAMA_ENDPOINT, json={
            "model": "mistral:7b",
            "prompt": prompt,
            "stream": False
        })
        response.raise_for_status()
        return response.json()
