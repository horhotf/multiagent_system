from fastapi import FastAPI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from app.api.routes import router
from app.config import settings

app = FastAPI(title=settings.app_name)
app.include_router(router)


@app.on_event("startup")
def startup() -> None:
    client = QdrantClient(url=settings.qdrant_url)
    for collection in ("docs_space", "tables_space"):
        exists = client.collection_exists(collection)
        if not exists:
            client.create_collection(
                collection_name=collection,
                vectors_config=VectorParams(size=4, distance=Distance.COSINE),
            )


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}
