from __future__ import annotations

import random
import time


class BackoffEngine:
    def __init__(
        self,
        base_delay: float = 1.0,
        max_delay: float = 16.0,
        jitter: bool = True,
    ):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter

    def delay(self, attempt: int) -> float:
        delay = min(
            self.base_delay * (2 ** max(0, attempt - 1)),
            self.max_delay,
        )

        if self.jitter:
            delay += random.uniform(0.0, delay * 0.25)

        return delay

    def sleep(self, attempt: int):
        time.sleep(self.delay(attempt))


engine = BackoffEngine()
