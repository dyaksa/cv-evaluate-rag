from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey, Float, LargeBinary, Integer, Index, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from internal.db import Base
import enum


class DocType(str, enum.Enum):
    job = "job"
    rubric = "rubric"
    resume = "resume"

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    email = Column(String, primary_key=True, unique=True)
    password = Column(String, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())

class Document(Base):
    __tablename__ = "documents"
    id = Column(String, primary_key=True)
    doc_type = Column(Enum(DocType), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    content_hash = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, server_default=func.now())

class Embedding(Base):
    __tablename__ = "embeddings"
    id = Column(String, primary_key=True)
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    vector = Column(LargeBinary, nullable=False)  # JSON list[float]
    dim = Column(Integer, nullable=False)


class EvaluationStatus(str, enum.Enum):
    uploaded = "uploaded"
    queued = "queued"
    processing = "processing"
    completed = "completed"

class Evaluation(Base):
    __tablename__ = "evaluations"
    id = Column(String, primary_key=True)
    upload_id = Column(String, ForeignKey("uploads.id", ondelete="CASCADE"), nullable=False)
    cv_match_rate = Column(Float, nullable=True)     # 0..1
    cv_feedback = Column(Text, nullable=True)
    project_score = Column(Float, nullable=True)     # 0..10 (weighted 1..5 -> 10?)
    overall_summary = Column(Text, nullable=True)
    status = Column(Enum(EvaluationStatus), default=EvaluationStatus.queued, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

class Upload(Base):
    __tablename__ = "uploads"
    id = Column(String, primary_key=True) 
    title = Column(String, nullable=False)
    file_path = Column(Text, nullable=False)
    job_context = Column(Text, nullable=False)
    rubric_context = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())