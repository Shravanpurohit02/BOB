from dataclasses import dataclass, field

@dataclass(slots=True)
class Context:
    workspace: str = ""
    project: str = ""
    files: list[str] = field(default_factory=list)
