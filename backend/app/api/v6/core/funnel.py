"""Upload do Funil Oficial Ativo — Adendo V2.1, secao 3 e 9.

O documento enviado pelo administrador (Owner/Gestor Comercial) vira a base
vetorial oficial que o Agente Comercial deve seguir ao pé da letra. O
conteúdo Leadzy/MSA Turbo do Documento Mestre é, por decisão registrada no
plano da Fase 1, o primeiro documento carregado aqui — não um sistema
paralelo.
"""
import uuid

from fastapi import APIRouter, UploadFile

from app.core.schemas import FunnelUploadOut
from app.services import qdrant_client
from app.services.document_ingestion import chunk_text, extract_text
from app.services.embeddings import get_embedding

router = APIRouter(prefix="/api/v6/core/funnel", tags=["funnel"])


@router.post("/upload-document", response_model=FunnelUploadOut, status_code=201)
async def upload_document(file: UploadFile) -> FunnelUploadOut:
    content = await file.read()
    text = extract_text(file.filename or "documento.txt", content)
    chunks = chunk_text(text)

    document_id = str(uuid.uuid4())
    collection = qdrant_client.settings.qdrant_collection_active_funnel

    for index, chunk in enumerate(chunks):
        vector = get_embedding(chunk)
        qdrant_client.upsert_point(
            collection,
            vector,
            payload={
                "document_id": document_id,
                "chunk_index": index,
                "text": chunk,
                "source_filename": file.filename,
            },
        )

    return FunnelUploadOut(
        document_id=document_id,
        chunks_generated=len(chunks),
        vector_collection_target=collection,
        status="INDEXED_SUCCESSFULLY",
    )
