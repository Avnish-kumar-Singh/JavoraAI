from app.rag.loader import DocumentLoader
from app.rag.splitter import DocumentSplitter

loader = DocumentLoader()
documents = loader.load("data/uploads/test.txt")

splitter = DocumentSplitter(
    chunk_size=50,
    chunk_overlap=10,
)

chunks = splitter.split(documents)

print()

print("Number of Chunks:", len(chunks))

print()

for i, chunk in enumerate(chunks):
    print("=" * 40)
    print(f"Chunk {i+1}")
    print("=" * 40)
    print(chunk.page_content)