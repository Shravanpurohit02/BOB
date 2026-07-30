from dataclasses import dataclass, field
from uuid import uuid4

@dataclass(slots=True)
class Symbol:
    id: str = field(default_factory=lambda: uuid4().hex)
    module: str = ""
    name: str = ""
    kind: str = ""
