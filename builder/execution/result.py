from dataclasses import dataclass, field


@dataclass(slots=True)
class ExecutionResult:

    success: bool = False

    message: str = ""

    elapsed: float = 0.0

    completed_stages: list[str] = field(default_factory=list)

    failed_stages: list[str] = field(default_factory=list)

    validation: dict = field(default_factory=dict)

    testing: dict = field(default_factory=dict)

    artifacts: list[str] = field(default_factory=list)

    changeset: str = ""
