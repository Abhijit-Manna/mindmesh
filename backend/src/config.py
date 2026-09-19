from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    # App Config
    APP_NAME: str = "MindMesh API"
    
    # OpenRouter / LLM Settings
    GEMINI_API_KEY_BA: str
    GEMINI_API_KEY_SA: str 
    GEMINI_API_KEY_TA: str 
    GEMINI_API_KEY_DP: str 
    GEMINI_API_KEY_DO: str | None = None
    GEMINI_API_KEY_RW: str | None = None
    GEMINI_API_KEY_EV: str | None = None
    GEMINI_MODEL: str
    EVALUATION_MODEL: str

    # Serper.dev
    SERPER_API_KEY: str

    # Agent Retry Settings
    MAX_AGENT_RETRIES: int = 2

    # Evaluation Settings
    ENABLE_EVALUATION: bool = True
    EVALUATION_THRESHOLD: float = 0.70

    # Agent Runtime
    AGENT_TIMEOUT_SECONDS: int = 120

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()