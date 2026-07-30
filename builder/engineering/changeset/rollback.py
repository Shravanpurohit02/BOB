from dataclasses import dataclass, field


@dataclass(slots=True)
class RollbackPlan:

    required: bool = True

    steps: list[str] = field(default_factory=list)
