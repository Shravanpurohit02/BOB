from __future__ import annotations

from collections import defaultdict

from builder.ast.module import Module


class SymbolGraph:
    """
    Builds a symbol ownership and reference graph.

    Exports:
        module -> exported symbols

    References:
        symbol -> modules containing that symbol

    Ownership:
        symbol -> module defining that symbol
    """

    def build(
        self,
        modules: list[Module],
    ) -> dict[str, dict]:

        exports: dict[str, list[str]] = {}

        references: dict[str, list[str]] = defaultdict(list)

        ownership: dict[str, str] = {}

        for module in modules:

            path = module.path

            symbols = sorted(
                set(
                    module.classes
                    + module.functions
                    + module.async_functions
                    + module.methods
                    + module.async_methods
                    + module.global_variables
                    + module.constants
                )
            )

            exports[path] = list(symbols)

            for symbol in symbols:

                references[symbol].append(path)

                ownership.setdefault(
                    symbol,
                    path,
                )

        return {
            "exports": exports,
            "references": {
                key: sorted(value)
                for key, value in references.items()
            },
            "ownership": ownership,
        }

    def exports(
        self,
        modules: list[Module],
    ) -> dict[str, list[str]]:

        return self.build(
            modules
        )["exports"]

    def references(
        self,
        modules: list[Module],
    ) -> dict[str, list[str]]:

        return self.build(
            modules
        )["references"]

    def ownership(
        self,
        modules: list[Module],
    ) -> dict[str, str]:

        return self.build(
            modules
        )["ownership"]

    def find_symbol(
        self,
        modules: list[Module],
        symbol: str,
    ) -> list[str]:

        return self.references(
            modules
        ).get(
            symbol,
            [],
        )

    def owner(
        self,
        modules: list[Module],
        symbol: str,
    ) -> str | None:

        return self.ownership(
            modules
        ).get(symbol)


symbol_graph = SymbolGraph()

