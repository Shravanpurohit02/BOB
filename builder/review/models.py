from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass(slots=True)
class ReviewTask:

    id: str = field(default_factory=lambda: uuid4().hex)

    created_at: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )

    reviewed_at: str = ""

    target: str = ""

    issue: str = ""

    proposal: str = ""

    priority: int = 1

    status: str = "pending"

    reviewer: str = ""

    metadata: dict = field(default_factory=dict)
