from dataclasses import dataclass, field

from .symbol_indexer import indexer
from .dependency_map import dependency_map


@dataclass(slots=True)
class WorkspaceIndex:

    modules:int=0

    symbols:int=0

    imports:int=0

    dependency_graph:dict=field(default_factory=dict)

    symbol_index:object=None


class WorkspaceIndexer:

    def build(
        self,
        workspace:str,
    ):

        symbol_index=indexer.build(workspace)

        graph=dependency_map.build(workspace)

        imports=sum(
            len(v)
            for v in graph.values()
        )

        return WorkspaceIndex(
            modules=len(symbol_index.modules),
            symbols=len(symbol_index.symbols),
            imports=imports,
            dependency_graph=graph,
            symbol_index=symbol_index,
        )


workspace_indexer=WorkspaceIndexer()
