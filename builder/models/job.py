from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

@dataclass(slots=True)
class Job:
    id: str = field(default_factory=lambda: uuid4().hex)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    name: str = ""
    worker: str = ""
    status: str = "pending"
    payload: dict = field(default_factory=dict)
