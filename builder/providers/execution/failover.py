
from __future__ import annotations
from dataclasses import dataclass

from builder.providers.runtime import router as runtime_router

RETRY_STATUS = {
    408,
    409,
    425,
    429,
    500,
    502,
    503,
    504,
}

MAX_RETRIES = 2


@dataclass(slots=True)
class ProviderFailure:
    provider: str
    attempts: int
    reason: str


class FailoverEngine:
    def should_retry(self, response):

        if response is None:
            return True

        if getattr(response, "is_success", False):
            return False

        return getattr(response, "status_code", 0) in RETRY_STATUS

    def max_attempts(self):
        return MAX_RETRIES + 1

    def providers(self, request=None):
        # An explicit provider on the request means MANUAL selection.
        # Manual selection is intentionally strict: return only the
        # requested provider and never silently substitute another one.
        requested = ""

        if request is not None:
            requested = str(
                getattr(request, "provider", "") or ""
            ).strip().lower()

        if requested:
            registry = runtime_router._registry()

            if not registry.exists(requested):
                return []

            provider = registry.get(requested)

            if not provider.enabled:
                return []

            return [provider]

        # Empty provider means AUTO selection.
        return list(runtime_router.available())

    def new_failures(self):
        return []

    def record_failure(
        self,
        failures,
        provider,
        attempts,
        reason,
    ):
        failures.append(
            ProviderFailure(
                provider=provider.name,
                attempts=attempts,
                reason=reason,
            )
        )
        return failures


engine = FailoverEngine()
