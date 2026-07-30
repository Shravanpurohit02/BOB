from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from threading import Lock
from time import monotonic


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass(slots=True)
class Circuit:

    state: CircuitState = CircuitState.CLOSED

    consecutive_failures: int = 0

    opened_at: float = 0.0

    cooldown: float = 60.0


class CircuitBreaker:

    FAILURE_THRESHOLD = 3

    def __init__(self):

        self._lock = Lock()

        self._circuits = {}

    def circuit(self, provider):

        with self._lock:

            if provider not in self._circuits:

                self._circuits[provider] = Circuit()

            return self._circuits[provider]

    def allow(self, provider):

        c = self.circuit(provider)

        if c.state == CircuitState.CLOSED:
            return True

        if c.state == CircuitState.HALF_OPEN:
            return True

        if monotonic() - c.opened_at >= c.cooldown:

            c.state = CircuitState.HALF_OPEN

            return True

        return False

    def success(self, provider):

        c = self.circuit(provider)

        c.state = CircuitState.CLOSED

        c.consecutive_failures = 0

    def failure(self, provider):

        c = self.circuit(provider)

        c.consecutive_failures += 1

        if c.consecutive_failures >= self.FAILURE_THRESHOLD:

            c.state = CircuitState.OPEN

            c.opened_at = monotonic()

    def state(self, provider):

        return self.circuit(provider).state.value


engine = CircuitBreaker()
