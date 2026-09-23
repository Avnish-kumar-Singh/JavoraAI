"""
Retriever

Retrieves the most relevant chunks from ChromaDB.
"""

from app.rag.vector_store import VectorStore
from app.config.settings import settings
from app.config.logging_config import logger


class Retriever:
    def __init__(self):
        self.vector_store = VectorStore()
        self.retriever = self.vector_store.get_vector_store().as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": settings.RETRIEVER_K,
                "fetch_k": settings.RETRIEVER_FETCH_K,
                "lambda_mult": 0.7,
            },
        )

    def retrieve(self, query: str):
        docs = self.retriever.invoke(query)
        logger.info(f"Retrieved {len(docs)} document(s).")
        return docs
