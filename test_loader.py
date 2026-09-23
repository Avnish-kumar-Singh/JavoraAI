from app.rag.loader import DocumentLoader

loader = DocumentLoader()

docs = loader.load("data/uploads/test.txt")

print()

print("Number of Documents:", len(docs))

print()

print(docs[0].page_content)