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

    DATABASE_URL: str = Field(os.getenv("APP_DATABASE_URL", "sqlite:///./storage/app.db"), alias=AliasChoices("DATABASE_URL", "APP_DATABASE_URL"))


    REDIS_HOST: str = Field(os.getenv("APP_REDIS_HOST", "localhost"), alias=AliasChoices("REDIS_HOST", "APP_REDIS_HOST"))
    REDIS_PORT: int = Field(os.getenv("APP_REDIS_PORT", 6379), alias=AliasChoices("REDIS_PORT", "APP_REDIS_PORT"))
    REDIS_PASSWORD: str = Field(os.getenv("APP_REDIS_PASSWORD", ""), alias=AliasChoices("REDIS_PASSWORD", "APP_REDIS_PASSWORD"))
    REDIS_DB: int = Field(os.getenv("APP_REDIS_DB", 0), alias=AliasChoices("REDIS_DB", "APP_REDIS_DB"))

    REDIS_STREAM_KEY: str = Field(os.getenv("APP_REDIS_STREAM_KEY", "ingest_stream"), alias=AliasChoices("REDIS_STREAM_KEY", "APP_REDIS_STREAM_KEY"))
    REDIS_CONSUMER_GROUP: str = Field(os.getenv("APP_REDIS_CONSUMER_GROUP", "ingest_group"), alias=AliasChoices("REDIS_CONSUMER_GROUP", "APP_REDIS_CONSUMER_GROUP"))

    UPLOAD_FOLDER: str = Field(os.getenv("APP_UPLOAD_FOLDER", "storage/files/"), alias=AliasChoices("UPLOAD_FOLDER", "APP_UPLOAD_FOLDER"))
    JWT_SECRET_KEY: str = Field(os.getenv("APP_JWT_SECRET_KEY", "secret-key"), alias=AliasChoices("JWT_SECRET_KEY", "APP_JWT_SECRET_KEY"))

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