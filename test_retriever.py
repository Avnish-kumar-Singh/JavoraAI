from app.rag.retriever import Retriever

retriever = Retriever()

documents = retriever.retrieve(
    "What is JVM?"
)

print()

print("=" * 60)
print("Retrieved Documents")
print("=" * 60)

for index, doc in enumerate(documents, start=1):

    print(f"\nDocument {index}")
    print("-" * 60)
    print(doc.page_content)