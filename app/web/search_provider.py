"""
Search Provider

Handles communication with DuckDuckGo Search.
"""

# from duckduckgo_search import DDGS
from ddgs import DDGS
from app.web.search_models import (
    SearchResult,
    SearchResponse,
)


class SearchProvider:

    def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> SearchResponse:

        results = []

        with DDGS() as ddgs:

            response = ddgs.text(
                query,
                max_results=max_results,
            )

            for item in response:

                results.append(

                    SearchResult(
                        title=item.get("title", ""),
                        url=item.get("href", ""),
                        snippet=item.get("body", ""),
                    )

                )

        return SearchResponse(
            query=query,
            results=results,
        )