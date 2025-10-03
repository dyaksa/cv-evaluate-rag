from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):

    """Application settings loaded from environment variables or a .env file."""
    APP_NAME: str
    APP_VERSION: str
    APP_PORT: int

    DEBUG: bool

    GOOGLE_API_KEY: str

    DATABASE_URL: str = "sqlite:///./storage/app.db"

    GOOGLE_LLM_MODEL: str = "gemini-2.5-flash-lite"
    GOOGLE_EMBEDDING_MODEL: str = "models/text-embedding-004"


    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0

    REDIS_STREAM_KEY: str = "ingest_stream"
    REDIS_CONSUMER_GROUP: str = "ingest_group"

    UPLOAD_FOLDER: str = "storage/files/"
    JWT_SECRET_KEY: str = "secret-key"

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance so environment variables only parsed once."""
    return Settings()


settings = get_settings()