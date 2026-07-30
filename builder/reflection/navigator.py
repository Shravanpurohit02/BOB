from __future__ import annotations

from builder.reflection.query import query
from builder.reflection.reference_index import reference_index
from builder.reflection.reverse_index import reverse_index
from builder.reflection.call_graph import call_graph


class ReflectionNavigator:
    """
    High-level navigation API over the reflection subsystem.
    """

    def module(
        self,
        workspace: str,
        path: str,
    ):
        return query.module(
            workspace,
            path,
        )

    def symbol(
        self,
        workspace: str,
        qualified_name: str,
    ):
        return query.symbol(
            workspace,
            qualified_name,
        )

    def search(
        self,
        workspace: str,
        text: str,
    ):
        return query.search(
            workspace,
            text,
        )

    def module_symbols(
        self,
        workspace: str,
        module: str,
    ):
        return reverse_index.symbols(
            workspace,
            module,
        )

    def symbol_modules(
        self,
        workspace: str,
        symbol: str,
    ):
        return reference_index.references(
            workspace,
            symbol,
        )

    def callees(
        self,
        workspace: str,
        module: str,
    ):
        return call_graph.callees(
            workspace,
            module,
        )

    def callers(
        self,
        workspace: str,
        symbol: str,
    ):
        return call_graph.callers(
            workspace,
            symbol,
        )

    def overview(
        self,
        workspace: str,
    ):

        modules = query.modules(workspace)
        symbols = query.symbols(workspace)

        return {
            "modules": len(modules),
            "symbols": len(symbols),
            "call_graph": call_graph.forward(workspace),
            "reference_index": reference_index.build(workspace),
            "reverse_index": reverse_index.build(workspace),
        }


navigator = ReflectionNavigator()

