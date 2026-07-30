from dataclasses import dataclass, field


@dataclass(slots=True)
class CallSite:
    module: str
    path: str
    function: str
    line: int
    cls: str = ""


@dataclass(slots=True)
class CallEdge:
    caller: CallSite
    callee: str


@dataclass(slots=True)
class ImportEdge:
    module: str
    imported: str


@dataclass(slots=True)
class InheritanceEdge:
    cls: str
    base: str
