from sentence_transformers import SentenceTransformer
import psycopg2
from app.core.config import settings
from pydantic import BaseModel

# --- Pydantic models for request/response bodies ---
class TextRequest(BaseModel):
    text: str

class EmbeddingResponse(BaseModel):
    embedding: list

class CandidateRequest(BaseModel):
    query_embedding: list
    limit: int = 10

class CandidateResponse(BaseModel):
    candidates: list

# --- Original EmbeddingClient class definition ---
class EmbeddingClient:
    def __init__(self):
        print("EmbeddingClient and connect to Postgres DB")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.conn = psycopg2.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            dbname=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD
        )

    def generate_embedding(self, text: str) -> list:
        print("generate_embedding for text: ", text)
        return self.model.encode(text).tolist()

    def get_candidate_content(self, query_embedding: list, limit: int = 10) -> list:
        print("get_candidate_content: query_embedding: ", query_embedding)
        cur = self.conn.cursor()
        # You may need to adapt this line depending on your database library's
        # exact formatting for embeddings.
        cur.execute(
            "SELECT content_id FROM content_embeddings ORDER BY embedding <-> %s LIMIT %s",
            (str(query_embedding), limit)
        )
        rows = cur.fetchall()
        print("rows: ", rows)
        return [row[0] for row in rows]

    def __del__(self):
        self.conn.close()
