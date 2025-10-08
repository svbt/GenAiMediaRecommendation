# GenAiMediaRecommendation

```
Web UI ──(HTTP/gRPC)──> Auth Service ──(Kafka Pub)──> user-login-topic ──(Sub)──> User Service
                                                                 │
                                                                 ▼
                                                       rec-request-topic ──(Sub)──> Rec Service ──(gRPC/Async)──> LLM Service
                                                                 │                                           │
                                                                 ▼                                           ▼
                                                       rec-response-topic <──(Pub)──                  Vector DB (Embeddings)
                                                                 │
                                                                 ▼
Web UI <──(WebSocket/Polling + gRPC Fallback)── Rec Service (Enriched Recs)
```
