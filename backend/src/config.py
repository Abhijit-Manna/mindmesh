from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # ==========================================
    # App Config
    # ==========================================
    APP_NAME: str = "MindMesh API"

    # ==========================================
    # Gemini API Keys
    # ==========================================
    GEMINI_API_KEY_BA: str
    GEMINI_API_KEY_SA: str
    GEMINI_API_KEY_TA: str
    GEMINI_API_KEY_DP: str
    GEMINI_API_KEY_RW: str
    GEMINI_API_KEY_EV: str

    # ==========================================
    # Agent Models
    # ==========================================
    BA_MODEL: str
    SA_MODEL: str
    TA_MODEL: str
    DP_MODEL: str
    RW_MODEL: str

    # ==========================================
    # Evaluation Model
    # ==========================================
    EVALUATION_MODEL: str

    # ==========================================
    # Serper.dev
    # ==========================================
    SERPER_API_KEY: str

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

    OMNIROUTE_BASE_URL: str
    OMNIROUTE_API_KEY: str
    OPENAI_API_KEY: str
    # ==========================================
    # Pydantic Settings Configuration
    # ==========================================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()