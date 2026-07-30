from dataclasses import dataclass, field


@dataclass(slots=True)
class SemanticSymbol:

    name: str
    module: str
    kind: str
    line: int

    references: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SemanticRepository:

    modules: dict = field(default_factory=dict)

    symbols: dict = field(default_factory=dict)

    references: dict = field(default_factory=dict)

    call_graph: dict = field(default_factory=dict)

    reverse_index: dict = field(default_factory=dict)
