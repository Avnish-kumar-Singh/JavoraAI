from app.tools.dsa_tool import DSATool

tool = DSATool()

state = {
    "user_query": "Solve LeetCode 345 with the optimal solution.",
    "response": "",
    "status": ""
}

result = tool.execute(state)

print(result["response"])