from confluent_kafka import Producer
from app.core.config import settings

def create_kafka_producer():
    return Producer({"bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS})

def publish_message(producer: Producer, topic: str, message: str):
    producer.produce(topic, message.encode("utf-8"))
    producer.flush()
