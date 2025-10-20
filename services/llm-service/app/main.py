from fastapi import FastAPI
from app.api.v1.endpoints import llm
from app.kafka.producer import publish_message
from app.dependencies import get_llm_client, get_embedding_client, get_kafka_producer, get_kafka_consumer, get_redis_client
import json
import asyncio

app = FastAPI(title="LLM Service")

app.include_router(llm.router, prefix="/api/v1/llm", tags=["llm"])

async def process_message(message, llm_client, embedding_client, producer, redis_client):
    data = json.loads(message.value().decode("utf-8"))
    user_id = data["userId"]
    context = data["context"]
    
    # Check Redis cache
    cached_recs = redis_client.get(f"recs:{user_id}")
    if cached_recs:
        publish_message(producer, "rec.ready", cached_recs)
        return

    # Generate query embedding for candidate retrieval
    query_text = f"{context['prefs']['genres']} {context.get('last_5_watched', [])}"
    query_embedding = embedding_client.generate_embedding(query_text)
    candidates = embedding_client.get_candidate_content(query_embedding, limit=10)

    # Build prompt with candidates
    prompt = f"""
    System: Recommend 5 movies from the provided catalog based on user preferences.
    User: Preferences: {json.dumps(context['prefs'])}
    Last watched: {context.get('last_5_watched', [])}
    Catalog: {json.dumps(candidates)}
    Output: JSON list of 5 movie IDs with scores and reasons.
    """

    # Call LLM (Mistral 7B)
    llm_response = llm_client.generate_recommendations(prompt)
    llm_output = llm_response["response"]

    # Publish raw LLM output
    publish_message(producer, "llm.raw", json.dumps({
        "requestId": data["requestId"],
        "userId": user_id,
        "prompt": prompt,
        "response": llm_output,
        "ts": data["ts"]
    }))

    # Process and publish recommendations
    recs = json.loads(llm_output)
    rec_response = {
        "requestId": data["requestId"],
        "userId": user_id,
        "recs": recs,
        "ts": data["ts"]
    }
    rec_response_str = json.dumps(rec_response)
    publish_message(producer, "rec.ready", rec_response_str)

    # Cache recommendations in Redis
    redis_client.setex(f"recs:{user_id}", 3600, rec_response_str)  # Cache for 1 hour

@app.on_event("startup")
async def startup_event():
    consumer = get_kafka_consumer()
    consumer.subscribe(["rec.request"])
    llm_client = get_llm_client()
    embedding_client = get_embedding_client()
    producer = get_kafka_producer()
    redis_client = get_redis_client()

    while True:
        msg = consumer.poll(1.0)
        if msg and not msg.error():
            await process_message(msg, llm_client, embedding_client, producer, redis_client)
        await asyncio.sleep(0.1)
