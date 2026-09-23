"""
Base Tool

All tools inherit from this class.
"""

from abc import ABC, abstractmethod
from app.graph.state import AgentState


class BaseTool(ABC):

    @abstractmethod
    def execute(self, state: AgentState) -> AgentState:
        """
        Execute the tool.
        """
        pass