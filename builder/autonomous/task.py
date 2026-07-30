from dataclasses import dataclass, field
from uuid import uuid4


@dataclass(slots=True)
class AutonomousTask:

    id: str = field(default_factory=lambda: uuid4().hex)

    objective: str = ""

    status: str = "pending"

    phases: list[str] = field(default_factory=list)

    completed: list[str] = field(default_factory=list)

    context: dict = field(default_factory=dict)
