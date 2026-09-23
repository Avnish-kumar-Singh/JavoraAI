from app.nodes.answer_node import answer_node

state = {
    "messages": [],
    "user_query": "Explain JVM in simple language.",
    "intent": "general",
    "selected_tool": "llm",
    "context": "",
    "response": "",
    "status": "",
    "error": "",
}

result = answer_node(state)

print("\n========== AI RESPONSE ==========\n")

print(result["response"])