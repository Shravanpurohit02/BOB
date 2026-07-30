import json
from dataclasses import asdict
from pathlib import Path

from builder.models.event import Event

EVENT_FILE = Path(".builder/state/events.json")

class EventBus:

    def __init__(self):
        self._events = []
        self._load()

    def _load(self):
        if EVENT_FILE.exists():
            self._events = [
                Event(**e)
                for e in json.loads(EVENT_FILE.read_text(encoding="utf-8"))
            ]

    def _save(self):
        EVENT_FILE.parent.mkdir(parents=True, exist_ok=True)
        EVENT_FILE.write_text(
            json.dumps(
                [asdict(e) for e in self._events],
                indent=2,
            ),
            encoding="utf-8",
        )

    def publish(self, name: str, source: str, **payload):
        event = Event(
            name=name,
            source=source,
            payload=payload,
        )
        self._events.append(event)
        self._save()
        return event

    def all(self):
        return list(self._events)

event_bus = EventBus()
