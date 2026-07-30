from dataclasses import dataclass, field
from uuid import uuid4

from builder.intelligence.models import ImpactReport


@dataclass(slots=True)
class EditPlan:

    create_files: list[str] = field(default_factory=list)

    modify_files: list[str] = field(default_factory=list)

    delete_files: list[str] = field(default_factory=list)

    affected_modules: list[str] = field(default_factory=list)

    affected_symbols: list[str] = field(default_factory=list)

    affected_imports: list[str] = field(default_factory=list)

    validation_scope: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Task:
    id: str = field(default_factory=lambda: uuid4().hex)
    title: str = ""
    objective: str = ""
    status: str = "pending"

    priority: int = 100

    dependencies: list[str] = field(
        default_factory=list,
    )

    retries: int = 0

    metadata: dict = field(
        default_factory=dict,
    )


@dataclass(slots=True)
class Job:
    id: str = field(default_factory=lambda: uuid4().hex)
    title: str = ""
    tasks: list[Task] = field(default_factory=list)


@dataclass(slots=True)
class Milestone:
    id: str = field(default_factory=lambda: uuid4().hex)
    title: str = ""
    jobs: list[Job] = field(default_factory=list)


@dataclass(slots=True)
class EngineeringPlan:

    id: str = field(default_factory=lambda: uuid4().hex)

    objective: str = ""

    workspace: str = "."

    metadata: dict = field(default_factory=dict)

    milestones: list[Milestone] = field(default_factory=list)

    impact: ImpactReport | None = None

    edit: EditPlan = field(default_factory=EditPlan)
