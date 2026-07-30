from dataclasses import dataclass, field


@dataclass(slots=True)
class ImpactModule:
    name: str
    risk: str = "low"


@dataclass(slots=True)
class ImpactSymbol:
    name: str
    module: str
    kind: str = ""


@dataclass(slots=True)
class ImpactReport:
    target: str

    modules: list[ImpactModule] = field(default_factory=list)
    symbols: list[ImpactSymbol] = field(default_factory=list)

    references: list = field(default_factory=list)
    callers: list = field(default_factory=list)
    callees: list = field(default_factory=list)

    tests: list[str] = field(default_factory=list)
    validation_scope: list[str] = field(default_factory=list)

    risk: str = "low"
