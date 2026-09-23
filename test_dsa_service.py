from app.dsa.dsa_service import DSAService

service = DSAService()

response = service.solve(
    "Solve LeetCode 345 using the optimal approach."
)

print(response.answer)