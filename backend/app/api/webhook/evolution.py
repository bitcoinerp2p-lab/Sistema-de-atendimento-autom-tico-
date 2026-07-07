"""Ingress do WhatsApp via Evolution API — contrato conforme Especificação V2
Complementar, secao 7.2.

Fluxo: Evolution API -> este webhook -> lock distribuído por lead (Redis) ->
lead criado/atualizado no Postgres -> evento LEAD_CRIADO ou MENSAGEM_RECEBIDA
publicado no barramento (tabela `events`).
"""
import uuid
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Event, Lead
from app.db.session import get_db
from app.services.redis_client import cache_session_message, lead_lock

router = APIRouter(prefix="/webhook/evolution", tags=["webhook"])


def _extract_phone(remote_jid: str) -> str:
    return remote_jid.split("@")[0]


def _extract_text(message: dict[str, Any]) -> str:
    if "conversation" in message:
        return message["conversation"]
    for _, value in message.items():
        if isinstance(value, dict) and "text" in value:
            return value["text"]
    return ""


@router.post("/whatsapp/ingress", status_code=202)
async def whatsapp_ingress(payload: dict[str, Any], db: AsyncSession = Depends(get_db)) -> dict:
    data = payload.get("data", {})
    remote_jid = data.get("key", {}).get("remoteJid", "")
    phone = _extract_phone(remote_jid)
    text = _extract_text(data.get("message", {}))

    if not phone:
        return {"status": "ignored", "reason": "remoteJid ausente ou inválido"}

    async with lead_lock(phone) as acquired:
        if not acquired:
            return {"status": "ignored", "reason": "lead já em processamento"}

        result = await db.execute(select(Lead).where(Lead.phone == phone))
        lead = result.scalar_one_or_none()
        is_new = lead is None

        if lead is None:
            lead = Lead(phone=phone)
            db.add(lead)
            await db.flush()

        event_type = "LEAD_CRIADO" if is_new else "MENSAGEM_RECEBIDA"
        event = Event(
            id=str(uuid.uuid4()),
            event_type=event_type,
            actor_source="evolution_api_webhook",
            lead_id=lead.id,
            payload_data={"phone": phone, "text": text, "raw": payload},
        )
        db.add(event)
        await db.commit()

        await cache_session_message(lead.id, text)

    return {"status": "accepted", "lead_id": lead.id, "event_type": event_type}
