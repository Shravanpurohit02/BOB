from __future__ import annotations
from typing import ClassVar

from collections import defaultdict

from builder.ast.module_indexer import module_indexer as ast_symbols


class ReferenceIndex:
    """
    Repository-wide symbol reference index.

    Maps every discovered symbol to the modules that define it.
    """

    IGNORE = {
        "__pycache__",
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "venv",
    }

    def build(
        self,
        workspace: str,
    ) -> dict[str, list[str]]:

        modules = ast_symbols.build(workspace)

        index: dict[str, set[str]] = defaultdict(set)

        for module in modules:
            rel = module.path.replace("\\", "/")

            for symbol in (
                module.classes
                + module.functions
                + module.async_functions
                + module.methods
                + module.async_methods
                + module.global_variables
                + module.constants
            ):
                index[symbol].add(rel)

        return {key: sorted(value) for key, value in index.items()}

    def references(
        self,
        workspace: str,
        symbol: str,
    ) -> list[str]:

        return self.build(workspace).get(
            symbol,
            [],
        )

    def contains(
        self,
        workspace: str,
        symbol: str,
    ) -> bool:

        return symbol in self.build(workspace)

    def symbols(
        self,
        workspace: str,
    ) -> list[str]:

        return sorted(self.build(workspace))


reference_index = ReferenceIndex()