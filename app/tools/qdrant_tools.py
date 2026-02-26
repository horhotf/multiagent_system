from __future__ import annotations

from typing import Any

from qdrant_client import QdrantClient

from app.config import settings


class QdrantSearchTools:
    def __init__(self) -> None:
        self.client = QdrantClient(url=settings.qdrant_url)

    def _search(self, collection_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        query_vector = payload.get("query_vector") or [0.0] * 4
        limit = int(payload.get("limit", 5))
        results = self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit,
            with_payload=True,
        )
        items = [
            {
                "id": point.id,
                "score": point.score,
                "payload": point.payload,
            }
            for point in results
        ]
        return {"items": items, "collection": collection_name}

    def search_docs(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._search("docs_space", payload)

    def search_tables(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._search("tables_space", payload)
