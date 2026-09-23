"""
DSA Tool
"""

from app.tools.base_tool import BaseTool
from app.dsa.dsa_service import DSAService
from app.config.logging_config import logger


class DSATool(BaseTool):

    def __init__(self):

        self.service = DSAService()

    def execute(self, state):

        logger.info("DSA Tool Started")

        question = state["user_query"]

        response = self.service.solve(question)

        state["status"] = "SUCCESS"
        state["response"] = response.answer

        logger.info("DSA Tool Finished")

        return state