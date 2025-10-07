from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pydantic import Field, AliasChoices
from dotenv import load_dotenv
import os


load_dotenv() 

class Settings(BaseSettings):
    """Application settings loaded from environment variables or a .env file."""
    APP_NAME: str = Field(os.getenv("APP_NAME", "Rakamin Test"), alias=AliasChoices("APP_NAME", "APP_APP_NAME"))
    APP_VERSION: str = Field(os.getenv("APP_VERSION", "0.1.0"), alias=AliasChoices("APP_VERSION", "APP_APP_VERSION"))
    APP_PORT: int = Field(os.getenv("APP_PORT", 8001), alias=AliasChoices("APP_PORT", "APP_APP_PORT"))

    DEBUG: bool = Field(os.getenv("APP_DEBUG", False), alias=AliasChoices("APP_DEBUG", "APP_APP_DEBUG"))

    GOOGLE_API_KEY: str = Field(os.getenv("APP_GOOGLE_API_KEY", ""), alias=AliasChoices("GOOGLE_API_KEY", "APP_GOOGLE_API_KEY"))
    GOOGLE_LLM_MODEL: str = Field(os.getenv("APP_GOOGLE_LLM_MODEL", "gemini-2.5-flash-lite"), alias=AliasChoices("GOOGLE_LLM_MODEL", "APP_GOOGLE_LLM_MODEL"))
    GOOGLE_EMBEDDING_MODEL: str = Field(os.getenv("APP_GOOGLE_EMBEDDING_MODEL", "models/text-embedding-004"), alias=AliasChoices("GOOGLE_EMBEDDING_MODEL", "APP_GOOGLE_EMBEDDING_MODEL"))

    #database
    DB_DRIVER: str = Field(os.getenv("APP_DB_DRIVER", "postgresql+psycopg2"), alias=AliasChoices("DB_DRIVER", "APP_DB_DRIVER"))
    DB_HOST: str = Field(os.getenv("APP_DB_HOST", "localhost"), alias=AliasChoices("DB_HOST", "APP_DB_HOST"))
    DB_PORT: int = Field(os.getenv("APP_DB_PORT", 5432), alias=AliasChoices("DB_PORT", "APP_DB_PORT"))
    DB_USER: str = Field(os.getenv("APP_DB_USER", "user"), alias=AliasChoices("DB_USER", "APP_DB_USER"))
    DB_PASSWORD: str = Field(os.getenv("APP_DB_PASSWORD", "password"), alias=AliasChoices("DB_PASSWORD", "APP_DB_PASSWORD"))
    DB_NAME: str = Field(os.getenv("APP_DB_NAME", "database"), alias=AliasChoices("DB_NAME", "APP_DB_NAME"))
    DB_POOL_MIN: int = Field(os.getenv("APP_DB_POOL_MIN", 1), alias=AliasChoices("DB_POOL_MIN", "APP_DB_POOL_MIN"))
    DB_POOL_MAX: int = Field(os.getenv("APP_DB_POOL_MAX", 10), alias=AliasChoices("DB_POOL_MAX", "APP_DB_POOL_MAX"))
    DB_POOL_TIMEOUT: int = Field(os.getenv("APP_DB_POOL_TIMEOUT", 30), alias=AliasChoices("DB_POOL_TIMEOUT", "APP_DB_POOL_TIMEOUT"))

    CELERY_BROKER_URL: str = Field(os.getenv("APP_CELERY_BROKER_URL", "redis://localhost:6379/0"), alias=AliasChoices("CELERY_BROKER_URL", "APP_CELERY_BROKER_URL"))

    REDIS_HOST: str = Field(os.getenv("APP_REDIS_HOST", "localhost"), alias=AliasChoices("REDIS_HOST", "APP_REDIS_HOST"))
    REDIS_PORT: int = Field(os.getenv("APP_REDIS_PORT", 6379), alias=AliasChoices("REDIS_PORT", "APP_REDIS_PORT"))
    REDIS_PASSWORD: str = Field(os.getenv("APP_REDIS_PASSWORD", ""), alias=AliasChoices("REDIS_PASSWORD", "APP_REDIS_PASSWORD"))
    REDIS_DB: int = Field(os.getenv("APP_REDIS_DB", 0), alias=AliasChoices("REDIS_DB", "APP_REDIS_DB"))

    REDIS_STREAM_KEY: str = Field(os.getenv("APP_REDIS_STREAM_KEY", "ingest_stream"), alias=AliasChoices("REDIS_STREAM_KEY", "APP_REDIS_STREAM_KEY"))
    REDIS_CONSUMER_GROUP: str = Field(os.getenv("APP_REDIS_CONSUMER_GROUP", "ingest_group"), alias=AliasChoices("REDIS_CONSUMER_GROUP", "APP_REDIS_CONSUMER_GROUP"))

    UPLOAD_FOLDER: str = Field(os.getenv("APP_UPLOAD_FOLDER", "storage/files/"), alias=AliasChoices("UPLOAD_FOLDER", "APP_UPLOAD_FOLDER"))
    JWT_SECRET_KEY: str = Field(os.getenv("APP_JWT_SECRET_KEY", "secret-key"), alias=AliasChoices("JWT_SECRET_KEY", "APP_JWT_SECRET_KEY"))

    OPENROUTER_BASE_URL_MODEL: str = Field(os.getenv("APP_OPENROUTER_BASE_URL_MODEL", "https://openrouter.ai/api/v1"), alias=AliasChoices("OPENROUTER_BASE_URL_MODEL", "APP_OPENROUTER_BASE_URL_MODEL"))
    OPENROUTER_API_KEY: str = Field(os.getenv("APP_OPENROUTER_API_KEY", ""), alias=AliasChoices("OPENROUTER_API_KEY", "APP_OPENROUTER_API_KEY"))
    OPENROUTER_LLM_MODEL: str = Field(os.getenv("APP_OPENROUTER_LLM_MODEL", "z-ai/glm-4.5-air"), alias=AliasChoices("OPENROUTER_LLM_MODEL", "APP_OPENROUTER_LLM_MODEL"))
    ZHIPU_EMBEDDING_MODEL: str = Field(os.getenv("APP_ZHIPU_EMBEDDING_MODEL", "embedding-2"), alias=AliasChoices("ZHIPU_EMBEDDING_MODEL", "APP_ZHIPU_EMBEDDING_MODEL"))
    ZHIPU_API_KEY: str = Field(os.getenv("APP_ZHIPU_API_KEY", ""), alias=AliasChoices("ZHIPU_API_KEY", "APP_ZHIPU_API_KEY"))

    MINIO_URL: str = Field(os.getenv("APP_MINIO_URL", "http://localhost:9000"), alias=AliasChoices("MINIO_URL", "APP_MINIO_URL"))
    MINIO_ACCESS_KEY: str = Field(os.getenv("APP_MINIO_ACCESS_KEY", "minioadmin"), alias=AliasChoices("MINIO_ACCESS_KEY", "APP_MINIO_ACCESS_KEY"))
    MINIO_SECRET_KEY: str = Field(os.getenv("APP_MINIO_SECRET_KEY", "minioadmin"), alias=AliasChoices("MINIO_SECRET_KEY", "APP_MINIO_SECRET_KEY"))
    MINIO_BUCKET_NAME: str = Field(os.getenv("APP_MINIO_BUCKET_NAME", "my-bucket"), alias=AliasChoices("MINIO_BUCKET_NAME", "APP_MINIO_BUCKET_NAME"))

    #chorma db
    CHROMA_DB_DIR: str = Field(os.getenv("APP_CHROMA_DB_DIR", "./storage/chromadb"), alias=AliasChoices("CHROMA_DB_DIR", "APP_CHROMA_DB_DIR"))
    CHROMA_COLLECTION_NAME: str = Field(os.getenv("APP_CHROMA_COLLECTION_NAME", "resume_evaluation_collection"), alias=AliasChoices("CHROMA_COLLECTION_NAME", "APP_CHROMA_COLLECTION_NAME"))

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",
        env_prefix="APP_",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance so environment variables only parsed once."""
    return Settings()


settings = get_settings()