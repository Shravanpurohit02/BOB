from dataclasses import dataclass
from pathlib import Path

@dataclass(slots=True)
class Artifact:
    name: str
    path: Path
    size: int
