# from app.graph.builder import build_graph

# graph = build_graph()

# state = {
#     "messages": [],
#     "user_query": "Explain JVM in simple language.",
#     "intent": "",
#     "selected_tool": "",
#     "context": "",
#     "response": "",
#     "status": "",
#     "error": "",
# }

# result = graph.invoke(state)

# print("\n========== FINAL RESPONSE ==========\n")

# print(result["response"])



from app.graph.builder import build_graph

print("Building Graph...")

graph = build_graph()

print("Graph Built Successfully!")

state = {
    "messages": [],
    "user_query": "Explain JVM",
    "intent": "",
    "selected_tool": "",
    "context": "",
    "response": "",
    "status": "initialized",
    "error": "",
}

print("Invoking Graph...")

result = graph.invoke(state)

print("\n========== FINAL RESPONSE ==========\n")

print(result["response"])