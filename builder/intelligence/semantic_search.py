from .qualified_symbols import qualified_symbol_indexer


class SemanticSearch:

    def __init__(self):
        self.index = None

    def build(self, workspace: str):
        self.index = qualified_symbol_indexer.build(workspace)

    def search(self, text: str, limit: int = 25):

        words = [w.lower() for w in text.split() if w.strip()]
        scored = []

        for symbol in self.index.symbols:

            score = 0

            sid = symbol.id.lower()
            name = symbol.name.lower()
            module = symbol.module.lower()
            cls = (symbol.cls or "").lower()

            for w in words:
                if w == name:
                    score += 100
                if w in name:
                    score += 60
                if w in cls:
                    score += 40
                if w in module:
                    score += 20
                if w in sid:
                    score += 10

            if score:
                scored.append((score, symbol))

        scored.sort(key=lambda x: (-x[0], x[1].id))
        return [s for _, s in scored[:limit]]


semantic_search = SemanticSearch()
