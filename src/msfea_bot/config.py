"""Central configuration.

Every environment variable the app reads is loaded and validated *here* and
nowhere else (CLAUDE.md §6). Import the singleton `settings` from this module.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All runtime configuration, sourced from environment variables / `.env`.

    See `.env.example` for documentation of each field.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLM provider (swapped behind msfea_bot.llm — CLAUDE.md §3)
    llm_provider: str = "placeholder"
    llm_api_key: str = ""
    llm_model: str = ""

    # Embeddings (local/open by default — §3, ADR-0004)
    embedding_model: str = "BAAI/bge-small-en-v1.5"

    # Vector store: PostgreSQL + pgvector
    database_url: str = "postgresql://msfea:msfea@localhost:5432/msfea"

    # Retrieval / generation knobs
    top_k: int = 5
    similarity_threshold: float = 0.0

    # Escalation target shown when the bot refuses
    escalation_contact: str = ""

    # API / widget: comma-separated allowed CORS origins ("*" for dev)
    cors_allow_origins: str = "*"

    # Safety (Phase 8)
    rate_limit_requests: int = 20  # max requests per client per window
    rate_limit_window_seconds: float = 60.0
    trust_proxy_headers: bool = False  # set True only behind a trusted reverse proxy

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_allow_origins.split(",") if o.strip()]


settings = Settings()
