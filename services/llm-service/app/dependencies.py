from app.core.llm_client import LLMClient
from app.core.embedding import EmbeddingClient
from app.kafka.producer import create_kafka_producer
from app.kafka.consumer import create_kafka_consumer
import redis

def get_llm_client():
    return LLMClient()

def get_embedding_client():
    return EmbeddingClient()

def get_kafka_producer():
    return create_kafka_producer()

def get_kafka_consumer();
    return create_kafka_consumer()

def get_redis_client():
    return redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)
