import re
from dataclasses import dataclass, field

from .qualified_symbols import qualified_symbol_indexer


@dataclass(slots=True)
class ResolutionResult:
    query: str
    exact: list = field(default_factory=list)
    prefix: list = field(default_factory=list)
    contains: list = field(default_factory=list)


class SymbolResolver:

    def __init__(self):
        self.index = None

    def build(self, workspace: str):
        self.index = qualified_symbol_indexer.build(workspace)

    def _tokens(self, query: str):

        tokens = []

        for token in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", query):
            token = token.lower()

            if token in {
                "delete",
                "remove",
                "update",
                "modify",
                "change",
                "replace",
                "rename",
                "create",
                "add",
                "using",
                "with",
                "file",
                "files",
                "from",
                "into",
                "the",
                "and",
                "or",
                "py",
            }:
                continue

            tokens.append(token)

        return tokens

    def resolve(self, query: str):

        result = ResolutionResult(query=query)

        if self.index is None:
            return result

        seen = set()

        for token in self._tokens(query):

            for symbol in self.index.symbols:

                name = symbol.name.lower()
                cls = (symbol.cls or "").split(".")[-1].lower()
                module_base = symbol.module.split(".")[-1].lower()

                score = None

                if token == name:
                    score = "exact"

                elif token == cls:
                    score = "exact"

                elif token == module_base:
                    score = "exact"

                elif name.startswith(token):
                    score = "prefix"

                elif cls.startswith(token):
                    score = "prefix"

                elif module_base.startswith(token):
                    score = "prefix"

                elif token in name:
                    score = "contains"

                elif token in cls:
                    score = "contains"

                if score is None:
                    continue

                if symbol.id in seen:
                    continue

                seen.add(symbol.id)

                getattr(result, score).append(symbol)

        return result


symbol_resolver = SymbolResolver()
