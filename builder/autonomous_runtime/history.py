from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(slots=True)
class RuntimeEvent:
    timestamp: str
    stage: str
    status: str


class RuntimeHistory:
    def __init__(self):
        self._events = []

    def add(self, stage: str, status: str = "completed"):
        self._events.append(
            RuntimeEvent(
                timestamp=datetime.now(UTC).isoformat(),
                stage=stage,
                status=status,
            )
        )

    def all(self):
        return list(self._events)

    def clear(self):
        self._events.clear()


history = RuntimeHistory()
