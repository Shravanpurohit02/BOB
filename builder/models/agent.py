from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

@dataclass(slots=True)
class Agent:
    id: str = field(default_factory=lambda: uuid4().hex)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    name: str = ""
    role: str = ""
    enabled: bool = True
    status: str = "idle"
