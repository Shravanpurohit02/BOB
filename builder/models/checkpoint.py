from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

@dataclass(slots=True)
class Checkpoint:
    id: str = field(default_factory=lambda: uuid4().hex)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    name: str = ""
    description: str = ""
