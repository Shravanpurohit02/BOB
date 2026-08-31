from __future__ import annotations

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

        for token in re.findall(
            r"[A-Za-z_][A-Za-z0-9_]*",
            query,
        ):
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
                "insert",
                "using",
                "with",
                "file",
                "files",
                "function",
                "functions",
                "class",
                "classes",
                "method",
                "methods",
                "symbol",
                "symbols",
                "from",
                "into",
                "to",
                "the",
                "and",
                "or",
                "new",
                "existing",
                "py",
            }:
                continue

            tokens.append(token)

        return tokens

    def _target_tokens(self, query: str):
        """
        Extract likely symbol targets from natural-language edit requests.

        The resolver deliberately prefers explicit symbol references
        appearing after an edit verb and before a file/context phrase.
        Filename/module tokens are excluded from symbol targeting.
        """

        text = query.strip()

        patterns = (
            # delete/replace/rename/remove <symbol> ...
            r"\b(?:delete|remove|replace|rename|modify|change)"
            r"\s+(?:the\s+)?"
            r"([A-Za-z_][A-Za-z0-9_]*)"
            r"\s+(?:function|method|class|symbol)\b",

            # delete <symbol> from ...
            r"\b(?:delete|remove|replace|rename|modify|change)"
            r"\s+(?:the\s+)?"
            r"([A-Za-z_][A-Za-z0-9_]*)"
            r"\s+(?:from|in|within)\b",

            # replace the <symbol> function ...
            r"\b(?:the\s+)?"
            r"([A-Za-z_][A-Za-z0-9_]*)"
            r"\s+(?:function|method|class|symbol)\b",

            # explicit qualified symbol
            r"\b([A-Za-z_][A-Za-z0-9_]*"
            r"(?:\.[A-Za-z_][A-Za-z0-9_]*)+)\b",
        )

        targets = []

        for pattern in patterns:
            for match in re.finditer(
                pattern,
                text,
                re.IGNORECASE,
            ):
                value = match.group(1).strip().lower()

                if value and value not in targets:
                    targets.append(value)

        return targets

    def resolve(
        self,
        query: str,
        files: list[str] | None = None,
    ):
        result = ResolutionResult(query=query)

        if self.index is None:
            return result

        allowed_modules = None

        if files:
            allowed_modules = {
                f.removesuffix(".py").replace("/", ".")
                for f in files
            }

        target_tokens = self._target_tokens(query)

        # For explicit edit requests, resolve only the requested target.
        # Do not treat every symbol in the containing file as a target.
        tokens = target_tokens or self._tokens(query)

        seen = set()

        for token in tokens:
            qualified_token = token.split(".")

            for symbol in self.index.symbols:

                if (
                    allowed_modules is not None
                    and symbol.module not in allowed_modules
                ):
                    continue

                name = symbol.name.lower()
                qualified_name = symbol.qualified_name.lower()
                cls = (
                    (symbol.cls or "")
                    .split(".")[-1]
                    .lower()
                )

                score = None

                if token == qualified_name:
                    score = "exact"

                elif token == name or token == cls:
                    score = "exact"

                elif (
                    len(qualified_token) == 1
                    and name.startswith(token)
                ):
                    score = "prefix"

                elif (
                    len(qualified_token) == 1
                    and token in name
                ):
                    score = "contains"

                if score is None:
                    continue

                if symbol.id in seen:
                    continue

                seen.add(symbol.id)

                getattr(result, score).append(symbol)

        return result


symbol_resolver = SymbolResolver()


__all__ = (
    "ResolutionResult",
    "SymbolResolver",
    "symbol_resolver",
)
