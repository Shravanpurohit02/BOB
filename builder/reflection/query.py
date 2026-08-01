from __future__ import annotations

from builder.reflection.database import database
from builder.reflection.indexer import indexer


class ReflectionQuery:
    """
    Query interface for the reflection database.
    """

    def build(
        self,
        workspace: str,
    ):
        return indexer.build(workspace)

    def modules(
        self,
        workspace: str,
    ):
        return self.build(workspace).all_modules()

    def symbols(
        self,
        workspace: str,
    ):
        return self.build(workspace).all_symbols()

    def module(
        self,
        workspace: str,
        path: str,
    ):
        self.build(workspace)
        return database.module(path)

    def symbol(
        self,
        workspace: str,
        qualified_name: str,
    ):
        self.build(workspace)
        return database.symbol(qualified_name)

    def classes(
        self,
        workspace: str,
    ):

        return [symbol for symbol in self.symbols(workspace) if symbol.kind == "class"]

    def functions(
        self,
        workspace: str,
    ):

        return [
            symbol
            for symbol in self.symbols(workspace)
            if symbol.kind
            in (
                "function",
                "async_function",
            )
        ]

    def search(
        self,
        workspace: str,
        text: str,
    ):

        text = text.lower()

        return [
            symbol
            for symbol in self.symbols(workspace)
            if text in symbol.name.lower() or text in symbol.qualified_name.lower()
        ]


query = ReflectionQuery()
