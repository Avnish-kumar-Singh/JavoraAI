"""
LLM Tool
"""

from app.tools.base_tool import BaseTool
from app.graph.state import AgentState
from app.core.container import get_answer_agent


class LLMTool(BaseTool):
    def execute(self, state: AgentState) -> AgentState:
        return get_answer_agent().generate(state)
