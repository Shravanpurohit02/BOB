from pathlib import Path

from builder.graph.edge import Edge
from builder.graph.graph import graph
from builder.graph.node import Node

class GraphBuilder:

    def build(self, workspace: str):
        previous = None

        for path in sorted(Path(workspace).rglob("*")):
            if not path.is_file():
                continue

            node = graph.add_node(
                Node(
                    name=path.name,
                    type=path.suffix.lstrip(".") or "file",
                )
            )

            if previous:
                graph.add_edge(
                    Edge(
                        source=previous.id,
                        target=node.id,
                    )
                )

            previous = node

        return graph

builder = GraphBuilder()
