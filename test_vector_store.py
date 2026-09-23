from app.rag.loader import DocumentLoader
from app.rag.splitter import DocumentSplitter
from app.rag.vector_store import VectorStore

loader = DocumentLoader()

documents = loader.load("data/uploads/test.txt")

splitter = DocumentSplitter(
    chunk_size=50,
    chunk_overlap=10,
)

chunks = splitter.split(documents)

store = VectorStore()

store.add_documents(chunks)

print()

print("Documents stored successfully in ChromaDB!")