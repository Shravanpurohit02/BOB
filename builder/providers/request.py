from dataclasses import dataclass, field
from uuid import uuid4

@dataclass(slots=True)
class ProviderRequest:
    id: str = field(default_factory=lambda: uuid4().hex)
    prompt: str = ""
    model: str = ""
    temperature: float = 0.2
