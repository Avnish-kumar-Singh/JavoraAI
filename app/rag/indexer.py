"""
Document Indexer

Indexes supported documents only once.
"""

from pathlib import Path

from app.rag.loader import DocumentLoader
from app.rag.splitter import DocumentSplitter
from app.rag.vector_store import VectorStore
from app.config.logging_config import logger


class DocumentIndexer:

    SUPPORTED_EXTENSIONS = {
        ".pdf",
        ".txt",
        ".docx",
    }

    def __init__(self):

        self.loader = DocumentLoader()
        self.splitter = DocumentSplitter()
        self.vector_store = VectorStore()

    def index_documents(self, folder_path: str):

        folder = Path(folder_path)

        if not folder.exists():
            raise FileNotFoundError(folder_path)

        files = [
            file
            for file in folder.iterdir()
            if file.suffix.lower() in self.SUPPORTED_EXTENSIONS
        ]

        logger.info(f"Found {len(files)} supported document(s).")

        total_chunks = 0

        for file in files:

            source = str(file)

            if self.vector_store.document_exists(source):

                logger.info(
                    f"Skipping already indexed document: {file.name}"
                )

                continue

            logger.info(f"Processing {file.name}")

            documents = self.loader.load(source)

            # Add source metadata
            for document in documents:
                document.metadata["source"] = source

            chunks = self.splitter.split(documents)

            self.vector_store.add_documents(chunks)

            total_chunks += len(chunks)

        logger.info(f"Indexed {total_chunks} chunk(s).")