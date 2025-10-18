CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS content_embeddings (
    content_id VARCHAR(50),
    embedding VECTOR(384)  -- Matches all-MiniLM-L6-v2 dimension
);
