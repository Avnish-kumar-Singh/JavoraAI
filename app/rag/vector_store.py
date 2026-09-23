"""
Vector Store

Stores embeddings in ChromaDB.
"""

from langchain_chroma import Chroma

from app.rag.embeddings import EmbeddingGenerator
from app.config.settings import settings
from app.config.logging_config import logger


class VectorStore:
    def __init__(self):
        self.embedding_model = EmbeddingGenerator()
        self.db = Chroma(
            persist_directory=settings.CHROMA_PATH,
            embedding_function=self.embedding_model.embeddings,
        )

    def add_documents(self, documents):
        logger.info(f"Adding {len(documents)} document(s) to ChromaDB...")
        self.db.add_documents(documents)

    def get_vector_store(self):
        return self.db

    def document_exists(self, source: str) -> bool:
        results = self.db.get(where={"source": source}, limit=1)
        return len(results["ids"]) > 0
