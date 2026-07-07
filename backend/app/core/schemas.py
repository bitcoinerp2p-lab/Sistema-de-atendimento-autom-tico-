"""Schemas Pydantic compartilhados, espelhando os contratos JSON dos
documentos de especificação (V1 secao "Matriz de Agentes", V2 secao 7,
Adendo V2.1 secao 9).
"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class EventIn(BaseModel):
    event_id: str
    event_type: str
    timestamp: datetime
    actor_source: str
    payload: dict[str, Any] = Field(default_factory=dict)


class EventOut(BaseModel):
    id: str
    event_type: str
    actor_source: str
    lead_id: str | None
    created_at: datetime


class ContextFragment(BaseModel):
    fragment_id: str
    similarity_score: float
    text_content: str


class ContextRetrievalOut(BaseModel):
    context_fragments: list[ContextFragment]


class FunnelUploadMetadata(BaseModel):
    uploaded_by: str
    document_type: str
    apply_immediately: bool = True


class FunnelUploadOut(BaseModel):
    document_id: str
    chunks_generated: int
    vector_collection_target: str
    status: str


class AbandonmentTelemetryData(BaseModel):
    lead_id: str
    last_interaction_timestamp: datetime
    elapsed_seconds_without_response: int
    current_funnel_stage: str
    read_receipt_confirmed: bool


class AbandonmentAlertIn(BaseModel):
    alert_id: str
    timestamp: datetime
    session_key: str
    telemetry_data: AbandonmentTelemetryData
