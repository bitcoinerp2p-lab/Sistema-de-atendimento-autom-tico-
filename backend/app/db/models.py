"""SQLAlchemy models for the ORION OS Core Engine — Fase 1.

Only the tables needed for the MVP Estrutural are defined here:
- Lead: registro mínimo de negócio.
- Event: barramento de eventos persistido, append-only (auditoria imutável).
- AgentReputation: score dinâmico por agente (R em [0.0, 10.0]).
- PendingFunnelUpdate: fila de homologação humana obrigatória (V2.1 secao 4.2).
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _new_lead_id() -> str:
    return f"usr_{uuid.uuid4().hex[:12]}"


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_new_lead_id)
    phone: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    current_stage: Mapped[str] = mapped_column(String, default="funnel_1_captacao")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )


class Event(Base):
    """Registro append-only do barramento de eventos.

    Nunca é atualizado ou apagado após a criação — é a trilha de auditoria
    imutável exigida pela Constituição (Lei da Memória) e pela Convenção de
    Codificação da Especificação V2 ("Imutabilidade Relacional").
    """

    __tablename__ = "events"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    event_type: Mapped[str] = mapped_column(String, index=True)
    actor_source: Mapped[str] = mapped_column(String, index=True)
    lead_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("leads.id"), nullable=True, index=True
    )
    payload_data: Mapped[dict] = mapped_column(JSON)
    auth_signature: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, index=True
    )


class AgentReputation(Base):
    """Score de reputação dinâmica por agente (Documento Mestre, Sistema de Confiança;
    Especificação V2, secao 7).
    """

    __tablename__ = "agent_reputation"

    agent_identifier: Mapped[str] = mapped_column(String, primary_key=True)
    score: Mapped[float] = mapped_column(Float, default=10.0)
    successful_interactions: Mapped[int] = mapped_column(default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )


class PendingFunnelUpdate(Base):
    """Fila de homologação humana obrigatória antes de qualquer atualização do
    Funil Oficial Ativo (Adendo V2.1, secao 4.2).
    """

    __tablename__ = "pending_funnel_updates"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    source_agent: Mapped[str] = mapped_column(String)
    proposed_text: Mapped[str] = mapped_column(Text)
    context_objection: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String, nullable=True)
