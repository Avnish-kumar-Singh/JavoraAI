"""
Web Tool
"""

from app.tools.base_tool import BaseTool
from app.config.logging_config import logger
from app.core.cache import make_key, response_cache
from app.core.container import get_llm_service


class WebTool(BaseTool):
    MAX_TOKENS = 900

    def __init__(self):
        from app.web.search_service import SearchService

        self.search_service = SearchService()
        self.llm = get_llm_service()

    def execute(self, state):
        query = state["user_query"]
        logger.info("Web Tool Started")

        cache_key = make_key("web", query)
        cached = response_cache.get(cache_key)
        if cached is not None:
            logger.info("Cache hit — skipping web search")
            state["context"], state["response"] = cached
            state["status"] = "SUCCESS"
            return state

        try:
            search_context = self.search_service.search(query)
        except Exception:
            logger.exception("Web search failed")
            search_context = ""

        if not search_context.strip():
            state["context"] = ""
            state["status"] = "SUCCESS"
            state["response"] = self.llm.invoke(
                prompt=(
                    f"Answer this Java question from your own knowledge. "
                    f"Note that you may not know the very latest releases.\n\n{query}"
                ),
                max_tokens=self.MAX_TOKENS,
            )
            return state

        prompt = f"""You are JavaMentorAI. Answer the user's question using these web results.

## Web results
{search_context}

## Question
{query}

Summarize the important information in your own words. Do not copy results verbatim. Combine agreeing sources into one answer."""

        response = self.llm.invoke(prompt=prompt, max_tokens=self.MAX_TOKENS)

        state["context"] = search_context
        state["response"] = response
        state["status"] = "SUCCESS"

        if isinstance(response, str) and not response.startswith("Error:"):
            response_cache.set(cache_key, (search_context, response))

        logger.info("Web Tool Finished")
        return state
