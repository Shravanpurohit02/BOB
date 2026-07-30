from .symbol_indexer import indexer


class IntelligenceQuery:

    def build(
        self,
        workspace: str,
    ):
        return indexer.build(workspace)

    def module(
        self,
        index,
        module: str,
    ):
        return [
            s
            for s in index.symbols
            if s.module == module
        ]

    def symbol(
        self,
        index,
        name: str,
    ):
        return [
            s
            for s in index.symbols
            if s.name == name
        ]

    def functions(
        self,
        index,
    ):
        return [
            s
            for s in index.symbols
            if s.kind == "function"
        ]

    def classes(
        self,
        index,
    ):
        return [
            s
            for s in index.symbols
            if s.kind == "class"
        ]


query = IntelligenceQuery()
