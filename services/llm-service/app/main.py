from fastapi import FastAPI
from app.api.v1.endpoints import llm
from app.kafka.producer import publish_message
from app.dependencies import get_llm_client, get_embedding_client, get_kafka_producer, get_kafka_consumer, get_redis_client
import json
import asyncio

app = FastAPI(title="LLM Service")

print("LLM Service")

app.include_router(llm.router, prefix="/api/v1/llm", tags=["llm"])

import json

async def process_message(message, llm_client, embedding_client, producer, redis_client):
    # Decode the message value (the JSON payload)
    data = json.loads(message.value().decode("utf-8"))
    
    # Extract user_id and programe_title from the JSON data
    user_id = data["userId"]
    programe_title = data["programe_title"]

    print("process message:", data)
    
    # Check Redis cache
    cached_recs = redis_client.get(f"recs:{user_id}")
    if cached_recs:
        publish_message(producer, "rec.ready", cached_recs)
        return
    
    # Make POST requests to the embedding-service's endpoint
    response = embedding_client.post("/generate_embedding", json={"text": programe_title})
    query_embedding = response.json()["embedding"]

    response = embedding_client.post("/get_candidate_content", json={"query_embedding": query_embedding, "limit": 10})
    candidates = response.json()["candidates"]

    # Build prompt with candidates
    prompt = f"""
    System: Recommend exactly 5 movies that are similar to the provided Movie Title. 
    Also, for each recommendation, specify its OTT provider (e.g., Netflix, Hulu, etc.) and the movie title itself if that information is available in the catalog data.
    Respond *only* with a JSON list containing 5 items. Each item must have 'contentId', 'title' (the movie title), 'score' (a float from 0 to 1), 'reason' (why it's similar), and 'provider' (the OTT provider name).

    Movie Title: {programe_title}

    Catalog: {json.dumps(candidates)}

    Output format example:
    [
      {{"contentId": "m-789", "title": "Spectre", "score": 0.95, "reason": "Action-packed spy thriller, similar themes.", "provider": "Netflix"}},
      {{"contentId": "m-234", "title": "Tenet", "score": 0.88, "reason": "High-stakes mission and suspense.", "provider": "Hulu"}}
    ]
    """

    # Call OpenAI APIs
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
    print("startup_event: ")
    consumer = get_kafka_consumer()
    consumer.subscribe(["rec.request"])
    llm_client = get_llm_client()
    embedding_client = get_embedding_client()
    producer = get_kafka_producer()
    redis_client = get_redis_client()

    while True:
        msg = consumer.poll(1.0)
        if msg and not msg.error():
            print("rec.request message")
            await process_message(msg, llm_client, embedding_client, producer, redis_client)
        await asyncio.sleep(0.1)
