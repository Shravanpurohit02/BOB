from __future__ import annotations

from dataclasses import dataclass
from time import time


@dataclass(slots=True)
class ProviderHealth:
    provider: str

    successes: int = 0
    failures: int = 0

    validation_failures: int = 0
    semantic_failures: int = 0
    compatibility_repairs: int = 0

    retries: int = 0

    total_latency: float = 0.0

    consecutive_failures: int = 0

    last_success: float = 0.0
    last_failure: float = 0.0

    def record_success(self, latency: float):

        self.successes += 1
        self.total_latency += latency
        self.consecutive_failures = 0
        self.last_success = time()

    def record_failure(self, latency: float):

        self.failures += 1
        self.total_latency += latency
        self.consecutive_failures += 1
        self.last_failure = time()

    @property
    def average_latency(self):

        total = self.successes + self.failures

        if total == 0:
            return 0.0

        return self.total_latency / total

    @property
    def score(self):

        score = 100.0

        score -= self.failures * 5
        score -= self.validation_failures * 8
        score -= self.semantic_failures * 10
        score -= self.consecutive_failures * 6
        score -= self.average_latency * 2

        return max(0.0, round(score, 2))
