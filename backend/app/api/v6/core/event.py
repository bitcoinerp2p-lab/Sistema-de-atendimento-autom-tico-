"""Barramento de eventos: publicação e recuperação de contexto (RAG).

Contratos conforme Especificação V2 Complementar, secao 7.1.
"""
from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import ContextFragment, ContextRetrievalOut, EventIn, EventOut
from app.db.models import Event
from app.db.session import get_db
from app.services import qdrant_client
from app.services.embeddings import get_embedding

router = APIRouter(prefix="/api/v6/core", tags=["event"])


@router.post("/event/publish", response_model=EventOut, status_code=201)
async def publish_event(
    event: EventIn,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(default=None),
) -> Event:
    lead_id = event.payload.get("lead_id")
    row = Event(
        id=event.event_id,
        event_type=event.event_type,
        actor_source=event.actor_source,
        lead_id=lead_id,
        payload_data=event.payload,
        auth_signature=authorization,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


@router.get("/memory/retrieve-context", response_model=ContextRetrievalOut)
async def retrieve_context(lead_id: str, query: str) -> ContextRetrievalOut:
    vector = get_embedding(query)
    fragments: list[ContextFragment] = []

    for collection in (
        qdrant_client.settings.qdrant_collection_active_funnel,
        qdrant_client.settings.qdrant_collection_objections,
    ):
        results = qdrant_client.search(collection, vector)
        for point in results:
            fragments.append(
                ContextFragment(
                    fragment_id=str(point.id),
                    similarity_score=point.score,
                    text_content=(point.payload or {}).get("text", ""),
                )
            )

    return ContextRetrievalOut(context_fragments=fragments)
