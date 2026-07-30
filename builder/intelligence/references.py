from dataclasses import dataclass, field


@dataclass(slots=True)
class Definition:
    name: str
    module: str
    kind: str
    line: int


@dataclass(slots=True)
class Reference:
    name: str
    module: str
    kind: str
    line: int


@dataclass(slots=True)
class ReferenceIndex:
    definitions: list[Definition] = field(default_factory=list)
    references: list[Reference] = field(default_factory=list)
    definitions_by_name: dict[str, list[Definition]] = field(default_factory=dict)
    references_by_name: dict[str, list[Reference]] = field(default_factory=dict)
