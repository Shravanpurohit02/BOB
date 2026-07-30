from dataclasses import dataclass

@dataclass(slots=True)
class Improvement:
    target: str
    issue: str
    proposal: str
    priority: int = 1
