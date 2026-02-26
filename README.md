# Multi-Agent Orchestrator MVP

FastAPI-based MVP for local multi-agent orchestration with Docker Compose.

## Components
- API (`FastAPI`, Python 3.11)
- PostgreSQL (tasks, steps, artifacts, schemas/templates/cache)
- Qdrant (collections: `docs_space`, `tables_space`)
- LLM integration via OpenAI-compatible `/chat/completions` endpoint (aider chat compatible)

## Run
```bash
docker compose up --build
```

## API
- `POST /v1/query` (`mode=auto|json_object|search|validate_text|image|pptx`)
- `POST /v1/object/generate`
- `POST /v1/text/validate`
- `GET /v1/artifacts/{id}`

## Tests
```bash
pytest -q
```
