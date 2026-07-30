from dataclasses import dataclass, field

@dataclass(slots=True)
class BuildRequest:
    objective: str
    workspace: str
    provider: str = ""
    model: str = ""
    context: dict = field(default_factory=dict)
