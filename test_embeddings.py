from app.rag.loader import DocumentLoader
from app.rag.splitter import DocumentSplitter
from app.rag.embeddings import EmbeddingGenerator

loader = DocumentLoader()
documents = loader.load("data/uploads/test.txt")

splitter = DocumentSplitter(
    chunk_size=50,
    chunk_overlap=10,
)

chunks = splitter.split(documents)

texts = [chunk.page_content for chunk in chunks]

embedder = EmbeddingGenerator()

vectors = embedder.generate(texts)

print()

print("Number of Chunks:", len(chunks))

print("Number of Embeddings:", len(vectors))

print("Embedding Dimension:", len(vectors[0]))