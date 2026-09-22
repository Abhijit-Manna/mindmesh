from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):

    # ==========================================
    # App Config
    # ==========================================
    APP_NAME: str = "MindMesh API"

    # API secret for /blueprints endpoints. Leave empty to disable
    # header checking (development only).
    API_SECRET_KEY: str = ""

    # ==========================================
    # Gemini API Keys
    # ==========================================
    GEMINI_API_KEY_BA: str = ""
    GEMINI_API_KEY_SA: str = ""
    GEMINI_API_KEY_TA: str = ""
    GEMINI_API_KEY_DP: str = ""
    GEMINI_API_KEY_RW: str = ""
    GEMINI_API_KEY_EV: str = ""

    # ==========================================
    # Agent Models
    # ==========================================
    BA_MODEL: str = ""
    SA_MODEL: str = ""
    TA_MODEL: str = ""
    DP_MODEL: str = ""
    RW_MODEL: str = ""

    # ==========================================
    # Evaluation Model
    # ==========================================
    EVALUATION_MODEL: str = ""

    # ==========================================
    # OpenRouter Fallback
    # ==========================================
    # Used automatically when an agent's or evaluator's primary LLM call
    # fails (demand spike, resource exhaustion, rate limit, outage, ...).
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_FALLBACK_MODEL: str = "openrouter/google/gemini-2.0-flash-001"
    ENABLE_OPENROUTER_FALLBACK: bool = True
    OPENROUTER_FALLBACK_ON_ALL_ERRORS: bool = True

    # ==========================================
    # Serper.dev
    # ==========================================
    SERPER_API_KEY: str = ""

    # ==========================================
    # Agent Retry Settings
    # ==========================================
    MAX_AGENT_RETRIES: int = 2

    # ==========================================
    # Evaluation Settings
    # ==========================================
    ENABLE_EVALUATION: bool = True
    EVALUATION_THRESHOLD: float = 0.70

    # ==========================================
    # Agent Runtime
    # ==========================================
    AGENT_TIMEOUT_SECONDS: int = 120

    # ==========================================
    # Logging
    # ==========================================
    LOG_LEVEL: str = "INFO"

    # ==========================================
    # Pydantic Settings Configuration
    # ==========================================
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()