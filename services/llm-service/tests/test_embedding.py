import pytest
from app.core.embedding import EmbeddingClient

def test_embedding_client():
    client = EmbeddingClient()
    embedding = client.generate_embedding("Test text")
    assert len(embedding) == 384  # all-MiniLM-L6-v2 dimension
