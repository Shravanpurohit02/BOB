from __future__ import annotations

from builder.reflection.query import query
from builder.reflection.semantic_models import (
    SemanticRepository,
    SemanticSymbol,
)


class SemanticEngine:
    def build(self, workspace: str):
        repo = SemanticRepository()

        for module in query.modules(workspace):
            key = getattr(module, "path", None) or getattr(module, "name", str(module))
            repo.modules[key] = module

        for symbol in query.symbols(workspace):
            qualified = f"{symbol.module}:{symbol.name}"

            repo.symbols[qualified] = SemanticSymbol(
                name=symbol.name,
                module=symbol.module,
                kind=symbol.kind,
                line=getattr(symbol, "line", 0),
            )

        return repo

    def search(self, workspace: str, text: str, *, limit: int = 25):
        text = text.lower().strip()
        matches = []

        for symbol in query.symbols(workspace):
            qualified = f"{symbol.module}:{symbol.name}".lower()

            score = 0
            if symbol.name.lower() == text:
                score += 100
            if qualified == text:
                score += 120
            if text in symbol.name.lower():
                score += 50
            if text in qualified:
                score += 30

            if score:
                matches.append((score, symbol))

        matches.sort(key=lambda x: x[0], reverse=True)
        return [s for _, s in matches[:limit]]

    def first(self, workspace: str, text: str):
        results = self.search(workspace, text, limit=1)
        return results[0] if results else None


semantic_engine = SemanticEngine()
engine = semantic_engine
