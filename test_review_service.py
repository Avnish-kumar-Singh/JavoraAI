from app.review.review_service import ReviewService

service = ReviewService()

java_code = """
public class Main {

    public static void main(String[] args) {
        System.out.println("Hello");
    }

}
"""

response = service.review(java_code)

print(response.review)