from dataclasses import dataclass, field
from uuid import uuid4

@dataclass(slots=True)
class Capability:
    id: str = field(default_factory=lambda: uuid4().hex)
    name: str = ""
    version: str = "1.0"
    provider: str = ""
    enabled: bool = True
