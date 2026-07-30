from builder.knowledge.document import Document

class KnowledgeBase:

    def __init__(self):
        self._docs = {}

    def add(self, document: Document):
        self._docs[document.id] = document

    def all(self):
        return list(self._docs.values())

database = KnowledgeBase()
