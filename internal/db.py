from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings

dsn = f"{settings.DB_DRIVER}://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
engine = create_engine(
    dsn,
    pool_size=settings.DB_POOL_MIN,
    max_overflow=settings.DB_POOL_MAX - settings.DB_POOL_MIN,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)
Base = declarative_base()