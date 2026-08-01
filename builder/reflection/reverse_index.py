from __future__ import annotations

from collections import defaultdict

from builder.reflection.reference_index import reference_index


class ReverseIndex:
    """
    Reverse lookup index.

    Produces:
        module -> symbols defined in that module
    """

    def build(
        self,
        workspace: str,
    ) -> dict[str, list[str]]:

        reverse: dict[str, set[str]] = defaultdict(set)

        forward = reference_index.build(workspace)

        for symbol, modules in forward.items():
            for module in modules:
                reverse[module].add(symbol)

        return {module: sorted(symbols) for module, symbols in reverse.items()}

    def symbols(
        self,
        workspace: str,
        module: str,
    ) -> list[str]:

        return self.build(workspace).get(
            module,
            [],
        )

    def contains(
        self,
        workspace: str,
        module: str,
    ) -> bool:

        return module in self.build(workspace)

    def modules(
        self,
        workspace: str,
    ) -> list[str]:

        return sorted(self.build(workspace))


reverse_index = ReverseIndex()
