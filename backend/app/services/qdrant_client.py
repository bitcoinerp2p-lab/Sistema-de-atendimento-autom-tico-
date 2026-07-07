"""Cliente Qdrant com as duas coleções isoladas exigidas pela especificação:

- `commercial_objections`: objeções históricas mapeadas de conversas reais.
- `active_sales_funnel`: Funil Oficial Ativo (seedado com Leadzy/MSA Turbo,
  depois atualizado só via upload homologado — Adendo V2.1).

As duas rodam em paralelo no mesmo cluster vetorial, diferenciadas pelo nome
da coleção (Adendo V2.1, secao 10, item 3).
"""
import uuid
from functools import lru_cache

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.core.config import get_settings

settings = get_settings()

SIMILARITY_THRESHOLD = 0.78
TOP_K = 3


@lru_cache
def get_qdrant() -> QdrantClient:
    return QdrantClient(url=settings.qdrant_url)


def ensure_collections() -> None:
    client = get_qdrant()
    for collection in (
        settings.qdrant_collection_objections,
        settings.qdrant_collection_active_funnel,
    ):
        if not client.collection_exists(collection):
            client.create_collection(
                collection_name=collection,
                vectors_config=qmodels.VectorParams(
                    size=settings.qdrant_vector_size,
                    distance=qmodels.Distance.COSINE,
                ),
            )


def upsert_point(collection: str, vector: list[float], payload: dict, point_id: str | None = None) -> str:
    client = get_qdrant()
    pid = point_id or str(uuid.uuid4())
    client.upsert(
        collection_name=collection,
        points=[qmodels.PointStruct(id=pid, vector=vector, payload=payload)],
    )
    return pid


def search(
    collection: str,
    vector: list[float],
    top_k: int = TOP_K,
    score_threshold: float = SIMILARITY_THRESHOLD,
) -> list[qmodels.ScoredPoint]:
    client = get_qdrant()
    return client.search(
        collection_name=collection,
        query_vector=vector,
        limit=top_k,
        score_threshold=score_threshold,
    )
