"""
Search Formatter
"""

from app.web.search_models import SearchResponse


class SearchFormatter:

    def format(self, response: SearchResponse) -> str:

        if not response.results:
            return "No search results found."

        lines = []

        for index, result in enumerate(response.results, start=1):

            lines.append(f"{index}. {result.title}")
            lines.append(f"URL: {result.url}")
            lines.append(result.snippet)
            lines.append("")

        return "\n".join(lines)