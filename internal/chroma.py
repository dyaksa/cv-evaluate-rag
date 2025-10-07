from langchain_chroma.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from core.config import settings
import uuid

class ChromaClient:
    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(model=settings.GOOGLE_EMBEDDING_MODEL, google_api_key=settings.GOOGLE_API_KEY)
        self.db = Chroma(
            collection_name=settings.CHROMA_COLLECTION_NAME,
            embedding_function=self.embeddings,
            persist_directory=settings.CHROMA_DB_DIR
        )
    
    def add_texts(self, texts: list[str], metadatas: list[dict] = None) -> list[str]:
        """Add texts to the Chroma collection."""
        ids = [str(uuid.uuid4()) for _ in texts]
        self.db.add_texts(texts=texts, metadatas=metadatas, ids=ids)
        return ids
    
    def query(self, query_text: str, top_k: int = 4, doc_type: str = "") -> list[tuple[float, dict]]:
        """Query the Chroma collection for similar texts."""
        results = self.db.similarity_search_with_score(
            query_text, 
            k=top_k,
            filter={"doc_type": doc_type}
        )
        return results