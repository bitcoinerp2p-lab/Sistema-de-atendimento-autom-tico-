"""Telemetria de abandono de funil — Adendo V2.1, secao 6 e 9.2.

Persiste o alerta como evento imutável. A geração do "cartão de recuperação"
completo (score de reativação, motivo provável) fica para quando o Painel de
Recuperação de Leads (frontend, Fase 2/3) existir — aqui só garantimos que o
sinal chega e fica auditável.
"""
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import AbandonmentAlertIn
from app.db.models import Event
from app.db.session import get_db

router = APIRouter(prefix="/api/v6/core/telemetry", tags=["telemetry"])


@router.post("/abandonment-alert", status_code=201)
async def abandonment_alert(
    alert: AbandonmentAlertIn, db: AsyncSession = Depends(get_db)
) -> dict:
    event = Event(
        id=str(uuid.uuid4()),
        event_type="ABANDONMENT_ALERT",
        actor_source="telemetry_monitor",
        lead_id=alert.telemetry_data.lead_id,
        payload_data=alert.model_dump(mode="json"),
    )
    db.add(event)
    await db.commit()
    return {"status": "received", "alert_id": alert.alert_id}
