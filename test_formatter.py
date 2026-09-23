from app.web.search_provider import SearchProvider
from app.web.search_formatter import SearchFormatter

provider = SearchProvider()
formatter = SearchFormatter()

response = provider.search("Latest Java 24 features")

formatted = formatter.format(response)

print(formatted)