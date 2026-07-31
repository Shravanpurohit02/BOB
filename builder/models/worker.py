from dataclasses import dataclass, field
from datetime import datetime, UTC
from uuid import uuid4

@dataclass(slots=True)
class Worker:
    id: str = field(default_factory=lambda: uuid4().hex)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    name: str = ""
    agent: str = ""
    status: str = "idle"
    current_task: str | None = None
