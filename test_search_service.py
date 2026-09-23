from app.web.search_service import SearchService

service = SearchService()

result = service.search("Latest Java 24 features")

print(result)