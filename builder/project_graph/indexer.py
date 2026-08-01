from __future__ import annotations

from builder.ast.symbols import symbols as ast_symbols
from builder.project_graph.database import database
from builder.project_graph.edge import ProjectEdge
from builder.project_graph.node import ProjectNode


class ProjectGraphIndexer:
    """
    Builds the project dependency graph from AST modules.
    """

    def build(
        self,
        workspace: str,
    ):

        database.clear()

        modules = ast_symbols.build(workspace)

        paths = {module.name: module.path for module in modules}

        for module in modules:
            node = ProjectNode(
                path=module.path,
                imports=sorted(module.imports),
                exports=sorted(module.exports),
            )

            database.add_node(node)

        for module in modules:
            for imported in module.imports:
                target = paths.get(imported)

                if target is None:
                    continue

                database.add_edge(
                    ProjectEdge(
                        source=module.path,
                        target=target,
                        relationship="imports",
                    )
                )

        return database

    def nodes(
        self,
        workspace: str,
    ):

        return self.build(workspace).all_nodes()

    def edges(
        self,
        workspace: str,
    ):

        return self.build(workspace).all_edges()


indexer = ProjectGraphIndexer()
