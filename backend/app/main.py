from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v6.core.event import router as event_router
from app.api.v6.core.funnel import router as funnel_router
from app.api.v6.core.telemetry import router as telemetry_router
from app.api.webhook.evolution import router as evolution_router
from app.core.config import get_settings
from app.services.qdrant_client import ensure_collections

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    ensure_collections()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.include_router(event_router)
app.include_router(funnel_router)
app.include_router(telemetry_router)
app.include_router(evolution_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "environment": settings.environment}
