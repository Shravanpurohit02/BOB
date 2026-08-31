from __future__ import annotations

from builder.project_graph.edge import ProjectEdge
from builder.project_graph.node import ProjectNode


class ProjectGraphDatabase:
    """
    In-memory project graph database.
    """

    def __init__(self) -> None:

        self.nodes: dict[str, ProjectNode] = {}

        self.edges: list[ProjectEdge] = []

    def clear(
        self,
    ) -> None:

        self.nodes.clear()

        self.edges.clear()

    def add_node(
        self,
        node: ProjectNode,
    ) -> None:

        self.nodes[node.path] = node

    def add_edge(
        self,
        edge: ProjectEdge,
    ) -> None:

        self.edges.append(edge)

    def node(
        self,
        path: str,
    ) -> ProjectNode | None:

        return self.nodes.get(path)

    def has_node(
        self,
        path: str,
    ) -> bool:

        return path in self.nodes

    def all_nodes(
        self,
    ) -> list[ProjectNode]:

        return sorted(
            self.nodes.values(),
            key=lambda node: node.path,
        )

    def all_edges(
        self,
    ) -> list[ProjectEdge]:

        return sorted(
            self.edges,
            key=lambda edge: (
                edge.source,
                edge.target,
                edge.relationship,
            ),
        )

    def statistics(
        self,
    ) -> dict[str, int]:

        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
        }


database = ProjectGraphDatabase()
