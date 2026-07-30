from dataclasses import dataclass, field


@dataclass(slots=True)
class PipelineContext:

    objective: str = ""
    workspace: str = ""

    changeset: object = None
    output: object = None
    semantic: object = None
    plan: object = None
    impact: object = None
    validation: object = None
    testing: object = None
    finalization: object = None


@dataclass(slots=True)
class PipelineResult:

    success: bool = False

    stages: list[str] = field(default_factory=list)

    context: PipelineContext | None = None
