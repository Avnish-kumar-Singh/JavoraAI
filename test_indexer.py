from app.rag.indexer import DocumentIndexer

indexer = DocumentIndexer()

indexer.index_documents("data/knowledge/uploads")
indexer.index_documents("data/knowledge/java_docs")
indexer.index_documents("data/knowledge/spring_docs")
indexer.index_documents("data/knowledge/interview_docs")
indexer.index_documents("data/knowledge/dsa")

print("All documents indexed successfully.")