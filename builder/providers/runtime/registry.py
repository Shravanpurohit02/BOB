from __future__ import annotations

from builder.providers.runtime.config import ProviderRuntime


class ProviderRegistry:
    def __init__(self):
        self._providers: dict[str, ProviderRuntime] = {}

    def register(self, profile: ProviderProfile) -> ProviderRuntime:
        self._providers[profile.name.lower()] = profile
        return profile

    def get(self, provider: str) -> ProviderRuntime:
        return self._providers[provider.lower()]

    def exists(self, provider: str) -> bool:
        return provider.lower() in self._providers

    def providers(self) -> list[str]:
        return sorted(self._providers)

    def all(self) -> list[ProviderProfile]:
        return sorted(
            self._providers.values(),
            key=lambda p: p.priority,
        )

    def enabled(self) -> list[ProviderProfile]:
        return [
            p
            for p in self.all()
            if p.enabled
        ]

    def healthy(self) -> list[ProviderProfile]:
        return [
            p
            for p in self.enabled()
            if p.healthy
        ]

    def free(self) -> list[ProviderProfile]:
        return [
            p
            for p in self.enabled()
            if p.free_tier
        ]

    def supports(self, capability: str) -> list[ProviderProfile]:
        key = f"supports_{capability}"

        return [
            p
            for p in self.enabled()
            if bool(getattr(p, key, False))
        ]

    def compatible(self, api_type: str) -> list[ProviderProfile]:
        return [
            p
            for p in self.enabled()
            if p.api_type == api_type
        ]

    def best_order(self) -> list[ProviderProfile]:
        healthy = self.healthy()
        if healthy:
            return healthy
        return self.enabled()

    def highest_priority(self) -> ProviderRuntime | None:
        providers = self.enabled()
        return providers[0] if providers else None

    def best(self) -> ProviderRuntime | None:
        providers = self.best_order()
        return providers[0] if providers else None


registry = ProviderRegistry()
