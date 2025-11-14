from kafka import KafkaProducer
import json, os

producer = KafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

def publish_login(user_id: int, email: str):
    producer.send(
        "user.login",
        key=str(user_id).encode(),
        value={"user_id": user_id, "email": email, "event": "login"},
    )
    producer.flush()
