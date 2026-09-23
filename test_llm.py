from app.services.llm_service import LLMService

llm = LLMService()

response = llm.invoke(
    "Explain JVM in 5 lines."
)

print("\n")
print(response)