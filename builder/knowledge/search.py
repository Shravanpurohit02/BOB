from builder.knowledge.database import database

class SearchEngine:

    def search(self, query: str):
        results = []

        query = query.lower()

        for doc in database.all():
            if query in doc.text.lower():
                results.append(doc)

        return results

search = SearchEngine()
