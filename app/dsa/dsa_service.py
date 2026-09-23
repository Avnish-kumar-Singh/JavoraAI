"""
DSA Service
"""

from app.core.container import get_llm_service
from app.dsa.dsa_prompt_builder import DSAPromptBuilder
from app.dsa.solution_formatter import SolutionFormatter
from app.dsa.dsa_models import DSAResponse


class DSAService:

    def __init__(self):

        self.llm = get_llm_service()
        self.prompt_builder = DSAPromptBuilder()
        self.formatter = SolutionFormatter()

    def solve(self, question: str) -> DSAResponse:
        """
        Solve a DSA question using the LLM.
        """

        prompt = self.prompt_builder.build(question)

        answer = self.llm.invoke(
            prompt=prompt,
            question=question,
            max_tokens=1800,
        )

        return self.formatter.format(answer)