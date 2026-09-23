from app.nodes.planner_node import planner_node

state = {
    "messages": [],
    "user_query": "Find bug in this Java code",
    "intent": "",
    "selected_tool": "",
    "context": "",
    "response": "",
    "status": "",
    "error": "",
}

result = planner_node(state)

print(result)