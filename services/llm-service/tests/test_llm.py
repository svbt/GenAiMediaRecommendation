import pytest
from app.core.llm_client import LLMClient

def test_llm_client_mock():
    llm_client = LLMClient()
    prompt = "Test prompt"
    response = llm_client.generate_recommendations(prompt)
    assert "response" in response
    assert isinstance(json.loads(response["response"]), list)
