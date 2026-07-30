from __future__ import annotations

from collections import defaultdict

from .models import Event


class EventBus:

    def __init__(self):

        self._handlers = defaultdict(list)

        self._history = []

    def subscribe(
        self,
        topic,
        handler,
    ):
        if handler not in self._handlers[topic]:
            self._handlers[topic].append(handler)

    def unsubscribe(
        self,
        topic,
        handler,
    ):
        if handler in self._handlers[topic]:
            self._handlers[topic].remove(handler)

    def publish(
        self,
        topic,
        source="",
        payload=None,
        metadata=None,
    ):

        event = Event(
            topic=topic,
            source=source,
            payload=payload or {},
            metadata=metadata or {},
        )

        self._history.append(event)

        for handler in list(self._handlers[topic]):
            handler(event)

        return event

    def history(
        self,
        topic=None,
    ):
        if topic is None:
            return list(self._history)

        return [
            e
            for e in self._history
            if e.topic == topic
        ]

    def clear(self):
        self._history.clear()


engine = EventBus()
