from dataclasses import dataclass, field

@dataclass(slots=True)
class RegressionResult:
    total: int = 0
    passed: int = 0
    failed: int = 0
    tests: list[str] = field(default_factory=list)
