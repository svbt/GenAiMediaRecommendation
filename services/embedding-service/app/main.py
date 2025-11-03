from fastapi import FastAPI, HTTPException
from app.core.embedding import TextRequest, EmbeddingResponse, CandidateRequest, CandidateResponse, EmbeddingClient

# --- Application setup ---
app = FastAPI(title="Embedding Service")

print("Embedding Service")

# Create a singleton instance of the EmbeddingClient
# This will be created when the application starts up
try:
    embedding_client = EmbeddingClient()
except Exception as e:
    print(f"Error initializing EmbeddingClient: {e}")
    embedding_client = None

# Define API routes using the FastAPI instance
@app.post("/generate_embedding", response_model=EmbeddingResponse)
def generate_embedding_route(request: TextRequest):
    if not embedding_client:
        raise HTTPException(status_code=503, detail="Service not available")
    try:
        embedding = embedding_client.generate_embedding(request.text)
        return {"embedding": embedding}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get_candidate_content", response_model=CandidateResponse)
def get_candidate_content_route(request: CandidateRequest):
    if not embedding_client:
        raise HTTPException(status_code=503, detail="Service not available")
    try:
        candidates = embedding_client.get_candidate_content(request.query_embedding, request.limit)
        return {"candidates": candidates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))