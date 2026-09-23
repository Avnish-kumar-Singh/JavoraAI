"""
Embedding Generator

Uses Ollama's nomic-embed-text model.
"""

from langchain_ollama import OllamaEmbeddings

from app.config.settings import settings
from app.config.logging_config import logger


class EmbeddingGenerator:

    def __init__(self):

        logger.info("Initializing Embedding Model...")

        self.embeddings = OllamaEmbeddings(
            model="nomic-embed-text",
            base_url=settings.OLLAMA_BASE_URL,
        )

    def generate(self, texts):

        logger.info(f"Generating embeddings for {len(texts)} chunks...")

        vectors = self.embeddings.embed_documents(texts)

        logger.info("Embeddings generated successfully.")

        return vectors