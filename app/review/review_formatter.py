"""
Review Formatter
"""

from app.review.review_models import ReviewResponse


class ReviewFormatter:

    def format(self, review: str) -> ReviewResponse:
        """
        Convert the raw LLM response into a ReviewResponse object.
        """

        return ReviewResponse(
            review=review.strip()
        )