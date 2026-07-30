from builder.knowledge.indexer import indexer
from builder.knowledge.search import search

class KnowledgeEngine:

    def build(self, workspace: str):
        return indexer.build(workspace)

    def search(self, query: str):
        return search.search(query)

engine = KnowledgeEngine()
