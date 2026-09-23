"""
Code Review Tool
"""

from app.tools.base_tool import BaseTool
from app.review.review_service import ReviewService
from app.config.logging_config import logger


class CodeReviewTool(BaseTool):

    def __init__(self):

        self.service = ReviewService()

    def execute(self, state):

        logger.info("Code Review Tool Started")

        code = state["user_query"]

        response = self.service.review(code)

        state["status"] = "SUCCESS"
        state["response"] = response.review

        logger.info("Code Review Tool Finished")

        return state