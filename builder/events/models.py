from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(slots=True)
class Event:

    id: str = field(default_factory=lambda: uuid4().hex)

    topic: str = ""

    source: str = ""

    timestamp: str = field(default_factory=utc_now)

    payload: dict = field(default_factory=dict)

    metadata: dict = field(default_factory=dict)
