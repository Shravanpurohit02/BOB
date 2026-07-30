from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass(slots=True)
class StagedDirectory:
    path: str


@dataclass(slots=True)
class StagedFile:
    path: str
    source: str = ""
    action: str = "create"


@dataclass(slots=True)
class StagingSession:
    id: str = field(default_factory=lambda: uuid4().hex)
    created_at: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )
    root: str = ""
    files: list[StagedFile] = field(default_factory=list)
    directories: list[StagedDirectory] = field(default_factory=list)
