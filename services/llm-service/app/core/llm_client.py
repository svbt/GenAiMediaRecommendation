import json
from openai import OpenAI
from app.core.config import settings

class LLMClient:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-3.5-turbo"

    def generate_recommendations(self, prompt: str) -> dict:
        if settings.ENV == "local":
            return {
                "response": json.dumps([
                    {"contentId": "m-789", "score": 0.98, "reason": "Sci-fi thriller"},
                    {"contentId": "m-234", "score": 0.85, "reason": "Sci-fi epic"}
                ])
            }
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a content recommendation expert. Respond only in the specified JSON format."},
                {"role": "user", "content": prompt}
            ],
        )
        content = response.choices[0].message.content
        return {"response": content}
        