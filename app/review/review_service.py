"""
Review Service
"""

from app.core.container import get_llm_service
from app.review.review_prompt_builder import ReviewPromptBuilder
from app.review.review_formatter import ReviewFormatter
from app.review.review_models import ReviewResponse


class ReviewService:

    def __init__(self):

        self.llm = get_llm_service()
        self.prompt_builder = ReviewPromptBuilder()
        self.formatter = ReviewFormatter()

    def review(self, code: str) -> ReviewResponse:
        """
        Review Java code using the LLM.
        """

        prompt = self.prompt_builder.build(code)

        review = self.llm.invoke(
            prompt=prompt,
            question="Review this Java code.",
            max_tokens=1800,
        )

        return self.formatter.format(review)