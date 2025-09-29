from __future__ import annotations
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from core.config import settings
import numpy as np
from typing import List
import hashlib


def to_blob(vec: List[float] | np.ndarray) -> bytes:
    arr = np.asarray(vec, dtype=np.float32)
    return arr.tobytes()

def from_blob(blob: bytes) ->np.ndarray:
    return np.frombuffer(blob, dtype=np.float32)

def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) or 1e-9
    return float(np.dot(a, b) / denom)

def text_hash(text: str) -> str:
    norm = " ".join(text.split()).lower()
    return hashlib.sha256(norm.encode()).hexdigest()

def embed_texts(texts: List[str]) -> List[np.ndarray]:
    emb = GoogleGenerativeAIEmbeddings(model=settings.GOOGLE_EMBEDDING_MODEL, api_key=settings.GOOGLE_API_KEY)
    vectors = emb.embed_documents(texts)
    return [np.asarray(vec, dtype=np.float32) for vec in vectors]

def embed_query(text: str) -> np.ndarray:
    emb = GoogleGenerativeAIEmbeddings(model=settings.GOOGLE_EMBEDDING_MODEL, api_key=settings.GOOGLE_API_KEY)
    vector = emb.embed_query(text)
    return np.asarray(vector, dtype=np.float32)

def embbed_text(text: str) -> list[float]:
    """Mengembalikan embedding (1x768) untuk teks."""
    model = GoogleGenerativeAIEmbeddings(model=settings.GOOGLE_EMBEDDING_MODEL, api_key=settings.GOOGLE_API_KEY)
    embedding = model.embed_query(text)
    return embedding

def embed_batch(texts: list[str]) -> list[list[float]]:
    """Mengembalikan list embedding (Nx768) untuk list teks."""
    if not texts:
        return []
    
    all_embeddings = []

    for i in range(0, len(texts), 16):
        batch = texts[i:i + 16]
        model = GoogleGenerativeAIEmbeddings(model=settings.GOOGLE_EMBEDDING_MODEL, api_key=settings.GOOGLE_API_KEY)
        batch_embeddings = model.embed_documents(batch)
        if i == 0:
            all_embeddings = batch_embeddings
        else:
            all_embeddings.extend(batch_embeddings)
    
    return all_embeddings
    