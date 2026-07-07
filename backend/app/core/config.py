"""Central configuration for the ORION OS Core Engine.

Reads everything from environment variables (see infra/.env.example).
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- General ---
    app_name: str = "ORION OS Core Engine"
    environment: str = "development"

    # --- Postgres ---
    database_url: str = "postgresql+asyncpg://orion:orion@localhost:5432/orion"

    # --- Redis ---
    redis_url: str = "redis://localhost:6379/0"
    redis_session_ttl_seconds: int = 900
    redis_lock_ttl_seconds: int = 5

    # --- Qdrant ---
    qdrant_url: str = "http://localhost:6333"
    qdrant_vector_size: int = 1536
    qdrant_collection_objections: str = "commercial_objections"
    qdrant_collection_active_funnel: str = "active_sales_funnel"

    # --- Agent runtime (OpenClaw stand-in, see Fase 1 do plano) ---
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-5"

    # --- Constitutional switches ---
    # Nunca deve ser True nesta fase: nenhum agente cria pedidos/pagamentos.
    scale_tracking_enabled: bool = False

    # --- Security ---
    jwt_secret: str = "change-me-in-production"
    hmac_shared_secret: str = "change-me-in-production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
