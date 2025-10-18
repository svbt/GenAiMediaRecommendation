from fastapi import APIRouter, Depends
from app.core.llm_client import LLMClient
from app.dependencies import get_llm_client
import json

router = APIRouter()

@router.post("/generate")
async def generate_recommendations(data: dict, llm_client: LLMClient = Depends(get_llm_client)):
    prompt = f"""
    System: Recommend 5 movies based on user preferences and catalog.
    User: {json.dumps(data['context'])}
    Output: JSON list of 5 movie IDs with scores and reasons.
    """
    response = llm_client.generate_recommendations(prompt)
    return response
