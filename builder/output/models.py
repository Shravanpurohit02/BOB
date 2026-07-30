from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass(slots=True)
class OutputArtifact:

    id: str = field(default_factory=lambda: uuid4().hex)

    created_at: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )

    objective: str = ""

    workspace: str = ""

    output_directory: str = ""

    files: list[str] = field(default_factory=list)

    metadata: dict = field(default_factory=dict)
