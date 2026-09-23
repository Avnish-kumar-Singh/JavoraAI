"""
Application Settings
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    # ---------------- Ollama / LLM ----------------
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    MODEL_NAME: str = "qwen2.5:latest"
    EMBEDDING_MODEL: str = "nomic-embed-text:latest"

    # Keeps the model resident in Ollama's memory between requests.
    # Without this Ollama evicts the model after 5 minutes and every
    # "first" request pays a multi-second model load.
    OLLAMA_KEEP_ALIVE: str = "30m"

    # Context window. Smaller = faster prefill. The prompts this app
    # builds are ~1-2k tokens, so 4096 is plenty.
    NUM_CTX: int = 4096

    # Request timeout in seconds for a single LLM call.
    LLM_TIMEOUT: int = 180

    # ---------------- RAG ----------------
    CHROMA_PATH: str = "./data/chroma_db"
    RETRIEVER_K: int = 4
    RETRIEVER_FETCH_K: int = 8

    # ---------------- Response sizing ----------------
    SHORT_RESPONSE_TOKENS: int = 600
    MEDIUM_RESPONSE_TOKENS: int = 1100
    LONG_RESPONSE_TOKENS: int = 1800

    # ---------------- Cache ----------------
    ENABLE_RESPONSE_CACHE: bool = True
    CACHE_MAX_ENTRIES: int = 256
    CACHE_TTL_SECONDS: int = 3600

    # ---------------- API / Auth ----------------
    DATABASE_URL: str = "sqlite:///./data/javamentor.db"
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7
    CORS_ORIGINS: str = "*"

    LOG_LEVEL: str = "INFO"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
