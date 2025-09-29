from internal.db import SessionLocal
from model.model import Embedding, Document
from helpers.utils import normalize
from rag.embbedings import to_blob, from_blob, text_hash, cosine_sim
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from core.config import settings
from datetime import datetime
from sqlalchemy import select
from google.api_core.exceptions import ResourceExhausted, DeadlineExceeded
import backoff
import numpy as np
import uuid

class EmbeddingRepository:
    def __init__(self):
        self.emb = GoogleGenerativeAIEmbeddings(model=settings.GOOGLE_EMBEDDING_MODEL, api_key=settings.GOOGLE_API_KEY)

    def upsert_document_end_embedding(self, title: str, doc_type: str, text: str):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", " ", ""]
        )

        chunks = splitter.split_text(text)
        sess = SessionLocal()
        results = []

        for chunk in chunks:
            normalize_chunk = normalize(chunk)
            h = text_hash(normalize_chunk)
            exists = sess.query(Document).filter(Document.content_hash == h).first()

            if exists:
                results.append(exists.id)
                continue

            d = Document(id=str(uuid.uuid4()), doc_type=doc_type, title=title, content=normalize_chunk, content_hash=h, created_at=datetime.now())
            sess.add(d); sess.flush()

            vec = self.emb.embed_query(chunk)
            e = Embedding(id=str(uuid.uuid4()), document_id=d.id, vector=to_blob(vec), dim=len(vec))
            sess.add(e);
            results.append(d.id)

        sess.commit()
        return results

    @backoff.on_exception(backoff.expo, (ResourceExhausted, DeadlineExceeded), max_tries=3)
    def build_context(self, resume_text: str, top_k: int = 4):
        try:
            top_job = self.top_k_similiar(resume_text, top_k=top_k, where_kind="job")
            top_rubric = self.top_k_similiar(resume_text, top_k=top_k, where_kind="rubric")
        except Exception as e:
            raise Exception(f"Error building context: {e}")

        job_ctx = "\n\n---\n".join([d.content for _, d in top_job])
        rubric_ctx = "\n\n---\n".join([d.content for _, d in top_rubric])
        return job_ctx, rubric_ctx
    
    def top_k_similiar(self, query: str, top_k: int = 4, where_kind: str = None):
        sess = SessionLocal()
        q_vec = np.array(self.emb.embed_query(query), dtype=np.float32)
        q = select(Embedding, Document).join(Document, Embedding.document_id == Document.id)
        if where_kind:
            q = q.where(Document.doc_type == where_kind)
        all_embeddings = sess.execute(q).all()

        sims = []
        for row in all_embeddings:
            emb = row[0]  # Embedding object
            doc = row[1]  # Document object
            v = from_blob(emb.vector)
            sim = cosine_sim(q_vec, v)
            sims.append((sim, doc))
        
        sims.sort(key=lambda x: x[0], reverse=True)
        top_docs = [(sim, doc) for sim, doc in sims[:top_k]]
        return top_docs
