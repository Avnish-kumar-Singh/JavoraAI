from app.web.search_provider import SearchProvider

provider = SearchProvider()

response = provider.search("Java")

print(response)