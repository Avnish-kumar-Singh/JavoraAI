"""
Document Loader

Loads PDF, TXT and DOCX files.
"""

from pathlib import Path

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
)

from app.config.logging_config import logger


class DocumentLoader:

    def load(self, file_path: str):

        path = Path(file_path)

        suffix = path.suffix.lower()

        logger.info(f"Loading document: {path.name}")

        if suffix == ".pdf":
            loader = PyPDFLoader(file_path)

        elif suffix == ".txt":
            loader = TextLoader(file_path, encoding="utf-8")

        elif suffix == ".docx":
            loader = Docx2txtLoader(file_path)

        else:
            raise ValueError(f"Unsupported file type: {suffix}")

        documents = loader.load()

        logger.info(f"Loaded {len(documents)} document(s).")

        return documents