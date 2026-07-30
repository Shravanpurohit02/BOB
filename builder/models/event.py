from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

@dataclass(slots=True)
class Event:
    id: str = field(default_factory=lambda: uuid4().hex)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    name: str = ""
    source: str = ""
    payload: dict = field(default_factory=dict)
