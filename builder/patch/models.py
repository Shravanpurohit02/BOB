from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass(slots=True)
class Patch:

    id: str = field(default_factory=lambda: uuid4().hex)

    path: str = ""

    original: str = ""

    updated: str = ""

    # Integrity
    original_hash: str = ""

    updated_hash: str = ""

    created_at: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )

    committed_at: str | None = None

    rolled_back_at: str | None = None

    validated: bool = False

    compiled: bool = False

    tested: bool = False

    committed: bool = False

    rolled_back: bool = False

    metadata: dict = field(default_factory=dict)
