
from __future__ import annotations
from threading import Lock

from builder.providers.health.models import ProviderHealth


class ProviderHealthEngine:
    def __init__(self):

        self._providers = {}
        self._lock = Lock()

    def provider(self, name):

        with self._lock:
            if name not in self._providers:
                self._providers[name] = ProviderHealth(provider=name)

            return self._providers[name]

    def success(self, name, latency):

        self.provider(name).record_success(latency)

    def failure(self, name, latency):

        self.provider(name).record_failure(latency)

    def retry(self, name):

        self.provider(name).retries += 1

    def validation_failure(self, name):

        self.provider(name).validation_failures += 1

    def semantic_failure(self, name):

        self.provider(name).semantic_failures += 1

    def compatibility_repair(self, name):

        self.provider(name).compatibility_repairs += 1

    def ranking(self):

        return sorted(
            self._providers.values(),
            key=lambda p: p.score,
            reverse=True,
        )


engine = ProviderHealthEngine()
