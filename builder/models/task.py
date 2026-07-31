from dataclasses import dataclass, field
from datetime import datetime, UTC
from uuid import uuid4

@dataclass(slots=True)
class Task:
    id: str = field(default_factory=lambda: uuid4().hex)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    name: str = ""
    status: str = "pending"
    payload: dict = field(default_factory=dict)
