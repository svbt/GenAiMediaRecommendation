from confluent_kafka import Consumer
from app.core.config import settings

def create_kafka_consumer():
    return Consumer({
        "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
        "group.id": "llm-service",
        "auto.offset.reset": "earliest"
    })
