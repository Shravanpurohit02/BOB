from dataclasses import dataclass, field
from uuid import uuid4

@dataclass(slots=True)
class Plugin:
    id: str = field(default_factory=lambda: uuid4().hex)
    name: str = ""
    version: str = "0.1.0"
    enabled: bool = True
