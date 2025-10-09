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
Possible Git Repo Layout
```
media-recs/
├─ docker-compose.yml
├─ services/
│  ├─ web-ui/         (React)
│  ├─ auth/           (Node/Express or Spring)
│  ├─ user-service/   (Go/Java/Python)
│  ├─ rec-orchestrator/ (FastAPI)
│  ├─ llm-service/    (Python LangChain connector)
│  ├─ ingestion/      (scrapers/provider metadata)
│  ├─ producer/consumer-examples/  (cppkafka or other)
├─ infra/             (k8s manifests / terraform)
├─ docs/
├─ scripts/           (makefile, helpers)
└─ README.md

```
