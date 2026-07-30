from dataclasses import dataclass, field


@dataclass(slots=True)
class ValidationSummary:

    passed: bool = False

    checks: list[str] = field(default_factory=list)

    failures: list[str] = field(default_factory=list)
