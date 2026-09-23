"""
Answer Agent
"""

from app.graph.state import AgentState
from app.config.logging_config import logger
from app.core.cache import make_key, response_cache
from app.core.container import (
    get_llm_service,
    get_prompt_builder,
    get_response_planner,
)


class AnswerAgent:
    def __init__(self):
        # All shared — no per-instance ChatOllama clients any more.
        self.llm = get_llm_service()
        self.prompt_builder = get_prompt_builder()
        self.response_planner = get_response_planner()

    def build_prompt(self, state: AgentState):
        question = state["user_query"]
        context = state.get("context", "")
        history = state.get("messages", [])

        plan = self.response_planner.plan(question)
        prompt = self.prompt_builder.build(
            question=question,
            context=context,
            response_plan=plan,
            history=history,
        )
        return prompt, plan

    def generate(self, state: AgentState) -> AgentState:
        question = state["user_query"]
        context = state.get("context", "")

        cache_key = make_key("answer", question, context)
        cached = response_cache.get(cache_key)
        if cached is not None:
            logger.info("Cache hit — skipping generation")
            state["response"] = cached
            state["status"] = "SUCCESS"
            return state

        prompt, plan = self.build_prompt(state)

        response = self.llm.invoke(
            prompt=prompt,
            question=question,
            max_tokens=plan["max_tokens"],
        )

        state["response"] = response
        state["status"] = "SUCCESS"

        if isinstance(response, str) and not response.startswith("Error:"):
            response_cache.set(cache_key, response)

        return state
