from dataclasses import dataclass, field
from uuid import uuid4

@dataclass(slots=True)
class Node:
    id: str = field(default_factory=lambda: uuid4().hex)
    name: str = ""
    type: str = ""
