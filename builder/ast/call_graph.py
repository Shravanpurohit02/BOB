from __future__ import annotations

import ast
from collections import defaultdict
from pathlib import Path


class CallGraph:

    def build(
        self,
        workspace: str,
    ) -> dict[str, list[str]]:

        graph: dict[str, set[str]] = defaultdict(set)

        root = Path(workspace)

        for file in root.rglob("*.py"):

            try:
                source = file.read_text(
                    encoding="utf-8",
                )

                tree = ast.parse(
                    source,
                    filename=str(file),
                )

            except Exception:
                continue

            module = str(
                file.relative_to(root)
            ).replace("\\", "/")

            for node in ast.walk(tree):

                if not isinstance(
                    node,
                    ast.Call,
                ):
                    continue

                name = self._call_name(
                    node.func
                )

                if name:
                    graph[module].add(name)

        return {
            key: sorted(value)
            for key, value in graph.items()
        }

    def calls_in_module(
        self,
        workspace: str,
        module: str,
    ) -> list[str]:

        return self.build(workspace).get(
            module,
            [],
        )

    def callers(
        self,
        workspace: str,
        symbol: str,
    ) -> list[str]:

        result: list[str] = []

        graph = self.build(
            workspace
        )

        for module, calls in graph.items():

            if symbol in calls:
                result.append(module)

        return sorted(result)

    def _call_name(
        self,
        node: ast.AST,
    ) -> str:

        if isinstance(
            node,
            ast.Name,
        ):
            return node.id

        if isinstance(
            node,
            ast.Attribute,
        ):

            left = self._call_name(
                node.value
            )

            if left:
                return (
                    left
                    + "."
                    + node.attr
                )

            return node.attr

        if isinstance(
            node,
            ast.Call,
        ):
            return self._call_name(
                node.func
            )

        return ""


call_graph = CallGraph()

