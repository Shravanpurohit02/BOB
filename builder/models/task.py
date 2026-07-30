from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

@dataclass(slots=True)
class Task:
    id: str = field(default_factory=lambda: uuid4().hex)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    name: str = ""
    status: str = "pending"
    payload: dict = field(default_factory=dict)
