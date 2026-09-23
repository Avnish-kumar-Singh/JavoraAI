"""
Search Service
"""

from app.web.search_provider import SearchProvider
from app.web.search_formatter import SearchFormatter


class SearchService:

    def __init__(self):

        self.provider = SearchProvider()
        self.formatter = SearchFormatter()

    def search(self, query: str) -> str:
        """
        Search the web and return formatted results.
        """

        response = self.provider.search(query)

        formatted_response = self.formatter.format(response)

        return formatted_response