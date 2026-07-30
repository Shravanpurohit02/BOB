from dataclasses import dataclass, field
from uuid import uuid4

@dataclass(slots=True)
class Document:
    id: str = field(default_factory=lambda: uuid4().hex)
    path: str = ""
    text: str = ""
