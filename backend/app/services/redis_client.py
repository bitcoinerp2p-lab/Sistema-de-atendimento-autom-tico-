"""Cliente Redis: sessão curta (TTL) e lock distribuído por lead.

Nota de honestidade técnica: isto implementa um lock single-instance
(SET NX PX + release via Lua comparando um token), não o algoritmo Redlock
completo (que exige um quorum de instâncias Redis independentes). Para a
Fase 1, rodando um único Redis local, isso é suficiente para evitar que dois
webhooks do mesmo lead sejam processados em paralelo. Se o ORION OS crescer
para múltiplas instâncias de Redis, trocar por uma lib Redlock real (ex.:
`python-redlock`) antes de produção.
"""
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import redis.asyncio as redis

from app.core.config import get_settings

settings = get_settings()

_client: redis.Redis | None = None

_RELEASE_LOCK_SCRIPT = """
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
"""


def get_redis() -> redis.Redis:
    global _client
    if _client is None:
        _client = redis.from_url(settings.redis_url, decode_responses=True)
    return _client


@asynccontextmanager
async def lead_lock(lead_id: str, timeout_seconds: int | None = None) -> AsyncGenerator[bool, None]:
    """Adquire um lock exclusivo `lock:lead:<id>` antes de processar um payload.

    Uso:
        async with lead_lock(lead_id) as acquired:
            if not acquired:
                # outra requisição já está processando este lead
                ...
    """
    client = get_redis()
    key = f"lock:lead:{lead_id}"
    token = str(uuid.uuid4())
    ttl = timeout_seconds or settings.redis_lock_ttl_seconds

    acquired = await client.set(key, token, nx=True, ex=ttl)
    try:
        yield bool(acquired)
    finally:
        if acquired:
            await client.eval(_RELEASE_LOCK_SCRIPT, 1, key, token)


async def cache_session_message(lead_id: str, message: str) -> None:
    """Guarda a última mensagem da conversa com TTL curto (Camada Volátil)."""
    client = get_redis()
    key = f"session:{lead_id}:last_message"
    await client.set(key, message, ex=settings.redis_session_ttl_seconds)
