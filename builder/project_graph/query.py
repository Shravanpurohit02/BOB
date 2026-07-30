from __future__ import annotations

from builder.project_graph.database import database
from builder.project_graph.indexer import indexer


class ProjectGraphQuery:
    """
    Query interface for the project graph.
    """

    def build(
        self,
        workspace: str,
    ):

        return indexer.build(workspace)

    def nodes(
        self,
        workspace: str,
    ):

        return self.build(
            workspace
        ).all_nodes()

    def edges(
        self,
        workspace: str,
    ):

        return self.build(
            workspace
        ).all_edges()

    def node(
        self,
        workspace: str,
        path: str,
    ):

        self.build(workspace)

        return database.node(path)

    def outgoing(
        self,
        workspace: str,
        path: str,
    ):

        return [
            edge
            for edge in self.edges(workspace)
            if edge.source == path
        ]

    def incoming(
        self,
        workspace: str,
        path: str,
    ):

        return [
            edge
            for edge in self.edges(workspace)
            if edge.target == path
        ]

    def dependencies(
        self,
        workspace: str,
        path: str,
    ) -> list[str]:

        return sorted(
            {
                edge.target
                for edge in self.outgoing(
                    workspace,
                    path,
                )
            }
        )

    def dependents(
        self,
        workspace: str,
        path: str,
    ) -> list[str]:

        return sorted(
            {
                edge.source
                for edge in self.incoming(
                    workspace,
                    path,
                )
            }
        )


query = ProjectGraphQuery()

