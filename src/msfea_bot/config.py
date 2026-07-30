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

    # Generation sampling (ADR-0012). This bot does grounded extraction from
    # retrieved context, not creative writing, so decoding is deterministic by
    # default. Temperature 0 also makes the answer eval reproducible, which §2
    # depends on: a metric can only prove a change helped if re-running it on
    # unchanged code gives the same result.
    # Measured 2026-07-30: temperature 0 alone is NOT enough — Gemini still varied
    # its wording across identical calls (2 distinct answers in 3 runs). Pinning a
    # seed as well made 3/3 runs identical. Any fixed value works; what matters is
    # that it does not change between runs.
    llm_temperature: float = 0.0
    llm_seed: int = 42
    llm_max_output_tokens: int = 1024

    # Embeddings (local/open by default — §3, ADR-0004)
    embedding_model: str = "BAAI/bge-small-en-v1.5"

    # Vector store: PostgreSQL + pgvector
    database_url: str = "postgresql://msfea:msfea@localhost:5432/msfea"

    # Retrieval / generation knobs
    top_k: int = 5
    similarity_threshold: float = 0.0

    # Escalation target shown when the bot refuses
    escalation_contact: str = ""

    # API / widget: comma-separated allowed CORS origins. Empty (default) = deny
    # all cross-origin requests (same-origin still works). Set to the exact page
    # origin(s) that embed the widget in production, e.g. "https://www.aub.edu.lb".
    # Avoid "*" in production — it lets any site call the API and drain LLM quota.
    cors_allow_origins: str = ""

    # Safety (Phase 8)
    rate_limit_requests: int = 20  # max requests per client per window
    rate_limit_window_seconds: float = 60.0
    trust_proxy_headers: bool = False  # set True only behind a trusted reverse proxy

    # Admin dashboard: shared secret protecting /admin endpoints. Empty = admin
    # disabled (endpoints return 403). Set a strong value in production.
    admin_token: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_allow_origins.split(",") if o.strip()]


settings = Settings()
