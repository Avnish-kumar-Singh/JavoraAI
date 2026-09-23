from app.graph.state import AgentState

state: AgentState = {
    "messages": [],
    "user_query": "What is JVM?",
    "intent": "",
    "selected_tool": "",
    "context": "",
    "response": "",
    "status": "initialized",
    "error": "",
}

print(state)