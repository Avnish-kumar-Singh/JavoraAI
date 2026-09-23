"""
DSA Solution Formatter
"""

from app.dsa.dsa_models import DSAResponse


class SolutionFormatter:

    def format(self, answer: str) -> DSAResponse:
        """
        Convert the raw LLM response into a DSAResponse object.
        """

        return DSAResponse(
            answer=answer.strip()
        )