from __future__ import annotations

from collections import defaultdict

from builder.ast.call_graph import call_graph as ast_call_graph


class ReflectionCallGraph:
    """
    Reflection wrapper around the AST call graph.

    Provides forward and reverse call relationships.
    """

    def build(self, workspace: str) -> dict[str, list[str]]:
        return ast_call_graph.build(workspace)

    def forward(self, workspace: str) -> dict[str, list[str]]:
        return self.build(workspace)

    def reverse(self, workspace: str) -> dict[str, list[str]]:
        reverse: dict[str, set[str]] = defaultdict(set)

        for module, calls in self.build(workspace).items():
            for call in calls:
                reverse[call].add(module)

        return {
            key: sorted(value)
            for key, value in reverse.items()
        }

    def callees(self, workspace: str, module: str) -> list[str]:
        return self.build(workspace).get(module, [])

    def callers(self, workspace: str, symbol: str) -> list[str]:
        return self.reverse(workspace).get(symbol, [])


call_graph = ReflectionCallGraph()
