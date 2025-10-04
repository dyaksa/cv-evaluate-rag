from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings
from sqlalchemy import event
from rag.embbedings import from_blob
from sqlalchemy.pool import NullPool
import numpy as np

engine = create_engine(
    settings.DATABASE_URL, 
    poolclass=NullPool,
    connect_args={
        "check_same_thread": False,
        "timeout": 10,
    },
    future=True,
    echo=False,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)
Base = declarative_base()


def cosine_sim_blob(a: bytes, b: bytes) -> float:
    va, vb = from_blob(a), from_blob(b)
    if va.shape != vb.shape or va.size == 0:
        return 0.0
    dot = float(np.dot(va, vb))
    denom = float(np.linalg.norm(va) * np.linalg.norm(vb))
    return dot / denom if denom else 0.0

@event.listens_for(engine, "connect")
def register_cosine(dbapi_conn, conn_record):
    dbapi_conn.create_function("cosine_sim", 2, cosine_sim_blob)