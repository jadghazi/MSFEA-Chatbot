"""Central configuration.

Every environment variable the app reads is loaded and validated *here* and
nowhere else (AGENTS.md §6). Import the singleton `settings` from this module.
"""

from typing import Literal
from datetime import date

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All runtime configuration, sourced from environment variables / `.env`.

    See `.env.example` for documentation of each field.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLM provider (swapped behind msfea_bot.llm — AGENTS.md §3)
    llm_provider: str = "placeholder"
    llm_api_key: str = ""
    llm_model: str = ""
    # Occasional staff review uses a separate model and quota from student answers.
    curation_llm_model: str = "gemini-3.1-flash-lite"
    curation_llm_daily_call_limit: int = Field(default=400, ge=1, le=500)
    curation_llm_requests_per_minute: int = Field(default=12, ge=1, le=30)
    # Actual answer previews share the student model's quota; leave most for students.
    curation_preview_daily_call_limit: int = Field(default=60, ge=1, le=500)

    # Legacy sampling profile (ADR-0012). Fixed temperature/seed reduce variation
    # but do not guarantee identical answers. Newer Gemini models omit these
    # deprecated fields and use an explicitly recorded thinking profile instead.
    llm_temperature: float = 0.0
    llm_seed: int = 42
    llm_max_output_tokens: int = Field(default=1024, ge=128, le=8192)
    # Shared app/worker paid-call admission. Prices are dollars per million tokens.
    llm_calls_enabled: bool = True
    llm_daily_request_limit: int = Field(default=100, ge=1, le=100000)
    llm_daily_token_limit: int = Field(default=500000, ge=10000, le=100000000)
    llm_daily_cost_limit_usd: float = Field(default=0.50, gt=0, le=1000)
    llm_input_price_per_million: float = Field(default=0.75, gt=0, le=1000)
    llm_output_price_per_million: float = Field(default=3.75, gt=0, le=1000)
    curation_input_price_per_million: float = Field(default=0.25, gt=0, le=1000)
    curation_output_price_per_million: float = Field(default=1.50, gt=0, le=1000)
    llm_price_valid_until: date = date(2026, 12, 31)
    llm_global_concurrency: int = Field(default=8, ge=1, le=32)
    ip_daily_request_limit: int = Field(default=200, ge=1, le=10000)
    session_question_limit: int = Field(default=40, ge=1, le=1000)
    # Student/preview Gemini API compatibility. Newer models deprecate sampling
    # parameters; preserve the legacy profile until a measured migration.
    llm_gemini_use_sampling_params: bool = True
    llm_gemini_thinking_level: Literal["low", "medium", "high"] | None = None

    # Embeddings (local/open by default — §3, ADR-0004)
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    # Pinned to an exact Hugging Face commit, not just the tag. "Reproducible from
    # source" (AGENTS.md §2) means a rebuild must produce the *same* vectors: the
    # `v1.5` name alone would still let re-uploaded weights change them silently,
    # and a rebuilt image querying a persisted pgdata volume would then compare new
    # vectors against old ones with no error — just quietly worse retrieval.
    # Empty = track the tag (not recommended outside experiments).
    embedding_model_revision: str = "5c38ec7c405ec4b44b94cc5a9bb96e735b38267a"

    # Vector store: PostgreSQL + pgvector
    database_url: str = "postgresql://msfea:msfea@localhost:5432/msfea"
    # Guarded validation uses a separate database. Draft vectors must never enter
    # the student-serving store.
    validation_database_url: str = ""
    # Deployment commit bound into validation fingerprints.
    app_commit: str = ""

    # Internal publication-guard coordination. These endpoints are private to the
    # Compose network and additionally require a dedicated service token.
    curation_worker_token: str = ""
    n8n_webhook_secret: str = ""
    n8n_base_url: str = "http://n8n:5678"
    app_internal_url: str = "http://app:8000"
    curation_outbox_max_attempts: int = Field(default=8, ge=1, le=20)
    curation_validation_timeout_minutes: int = Field(default=60, ge=15, le=1440)
    curation_publication_timeout_minutes: int = Field(default=60, ge=15, le=1440)

    # Retrieval / generation knobs. Explicit comparisons use at least 12 hits;
    # normal questions keep this depth (see the synthesis experiments).
    # Swept against context-recall after the KB grew to 183 chunks (ADR-0016):
    # k=5 -> 92%, k=7 -> 95%, k=10 -> 97%. 7 is the knee — it recovers a real case
    # for two extra chunks (~1k chars), where 10 doubles the context for one more.
    top_k: int = 7
    # Calibrated in ADR-0020 against answerable, terse/misspelled valid, and
    # clearly off-topic queries. Below this cosine score, skip the paid LLM call.
    similarity_threshold: float = Field(default=0.60, ge=0.0, le=1.0)

    # Escalation target shown when the bot refuses
    escalation_contact: str = ""

    # API / widget: comma-separated allowed CORS origins. Empty (default) = deny
    # all cross-origin requests (same-origin still works). Set to the exact page
    # origin(s) that embed the widget in production, e.g. "https://www.aub.edu.lb".
    # Avoid "*" in production — it lets any site call the API and drain LLM quota.
    cors_allow_origins: str = ""

    # Safety (Phase 8)
    rate_limit_requests: int = 60  # max requests per client per window
    rate_limit_window_seconds: float = 60.0
    trust_proxy_headers: bool = False  # set True only behind a trusted reverse proxy
    # Docker enables this so readiness means the local embedding/NER models are
    # loaded; tests and host development keep startup fast by default.
    warm_models_on_startup: bool = False

    # Admin dashboard: shared secret protecting /admin endpoints. Empty = admin
    # disabled (endpoints return 403). Set a strong value in production.
    admin_token: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_allow_origins.split(",") if o.strip()]


settings = Settings()
