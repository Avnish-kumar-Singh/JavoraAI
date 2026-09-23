"""
Tool Registry

Tools are now constructed lazily and memoized. Only the tool actually
selected for a question is ever built.
"""

from typing import Callable, Dict

from app.core.enums import ToolName
from app.config.logging_config import logger
from app.tools.base_tool import BaseTool


def _llm_tool() -> BaseTool:
    from app.tools.llm_tool import LLMTool

    return LLMTool()


def _rag_tool() -> BaseTool:
    from app.tools.rag_tool import RAGTool

    return RAGTool()


def _web_tool() -> BaseTool:
    from app.tools.web_tool import WebTool

    return WebTool()


def _dsa_tool() -> BaseTool:
    from app.tools.dsa_tool import DSATool

    return DSATool()


def _review_tool() -> BaseTool:
    from app.tools.code_review_tool import CodeReviewTool

    return CodeReviewTool()


def _java_compiler_tool() -> BaseTool:
    from app.tools.java_compiler_tool import JavaCompilerTool

    return JavaCompilerTool()


class ToolRegistry:
    _FACTORIES: Dict[str, Callable[[], BaseTool]] = {
        ToolName.LLM.value: _llm_tool,
        ToolName.RAG.value: _rag_tool,
        ToolName.WEB.value: _web_tool,
        ToolName.DSA.value: _dsa_tool,
        ToolName.REVIEW.value: _review_tool,
        ToolName.JAVA_COMPILER.value: _java_compiler_tool,
    }

    # Shared across every ToolRegistry instance in the process.
    _instances: Dict[str, BaseTool] = {}

    def get_tool(self, tool_name: str) -> BaseTool:
        if tool_name in self._instances:
            return self._instances[tool_name]

        factory = self._FACTORIES.get(tool_name)
        if factory is None:
            raise ValueError(f"Unknown tool: {tool_name}")

        logger.info(f"Instantiating tool on first use: {tool_name}")
        tool = factory()
        self._instances[tool_name] = tool
        return tool

    def available_tools(self) -> list[str]:
        return list(self._FACTORIES.keys())
