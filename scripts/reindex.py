"""
Build/refresh the RAG vector store from data/knowledge/.

Safe to re-run: DocumentIndexer skips files that are already indexed.

Usage:
    python scripts/reindex.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.rag.indexer import DocumentIndexer  # noqa: E402
from app.config.logging_config import logger  # noqa: E402

KNOWLEDGE_ROOT = Path(__file__).resolve().parents[1] / "data" / "knowledge"


def main():
    if not KNOWLEDGE_ROOT.exists():
        logger.warning(f"No knowledge folder found at {KNOWLEDGE_ROOT}")
        return

    indexer = DocumentIndexer()
    subfolders = [p for p in KNOWLEDGE_ROOT.iterdir() if p.is_dir()]

    if not subfolders:
        logger.warning("No knowledge subfolders to index.")
        return

    for folder in subfolders:
        logger.info(f"Indexing folder: {folder.name}")
        indexer.index_documents(str(folder))

    logger.info("Reindex complete.")


if __name__ == "__main__":
    main()
