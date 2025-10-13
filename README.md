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
│  ├─ auth/           (Python, Flask for rest Apis, integrate with Amazon APIs)
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

web-ui/ folder structure

```
media-recs/
├─ docker-compose.yml
├─ services/
│  └─ web-ui/
│     ├─ Dockerfile
│     ├─ package.json
│     ├─ src/
│     └─ public/

```

auth/ folder structure

```
auth/
├── app/
│   ├── __init__.py
│   ├── core/
│   │   ├── config.py         # Handles settings and environment variables
│   │   ├── security.py       # JWT and password hashing logic
│   │   └── oauth.py          # OAuth clients setup
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           └── auth.py   # API routes for login, token, etc.
│   ├── dependencies.py       # Dependency injection for common objects
│   └── main.py             # Main FastAPI application
├── tests/
├── .env.example
├── Dockerfile
└── requirements.txt
```