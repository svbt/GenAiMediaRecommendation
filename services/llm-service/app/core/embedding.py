from sentence_transformers import SentenceTransformer
import psycopg2
from app.core.config import settings

class EmbeddingClient:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.conn = psycopg2.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            dbname=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD
        )

    def generate_embedding(self, text: str) -> list:
        return self.model.encode(text).tolist()

    def get_candidate_content(self, query_embedding: list, limit: int = 10) -> list:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT content_id FROM content_embeddings ORDER BY embedding <-> %s LIMIT %s",
            (query_embedding, limit)
        )
        return [row[0] for row in cur.fetchall()]

    def __del__(self):
        self.conn.close()
