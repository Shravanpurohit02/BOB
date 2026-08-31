from __future__ import annotations

from builder.providers.runtime.config import ProviderRuntime


class ProviderRegistry:
    """Registry for loaded provider runtime configurations."""

    def __init__(self):
        self._providers: dict[str, ProviderRuntime] = {}

    def register(self, runtime: ProviderRuntime) -> ProviderRuntime:
        self._providers[runtime.name.lower()] = runtime
        return runtime

    def get(
        self,
        provider: str = "",
        model: str = "",
    ) -> ProviderRuntime | None:
        if provider:
            runtime = self._providers.get(provider.strip().lower())
            if runtime is not None:
                return runtime

        if model:
            normalized_model = model.strip().lower()
            for runtime in self._providers.values():
                if runtime.model.strip().lower() == normalized_model:
                    return runtime

        return None

    def exists(self, provider: str) -> bool:
        return provider.strip().lower() in self._providers

    def providers(self) -> list[str]:
        return sorted(self._providers)

    def all(self) -> list[ProviderRuntime]:
        return sorted(
            self._providers.values(),
            key=lambda runtime: runtime.priority,
        )

    def enabled(self) -> list[ProviderRuntime]:
        return [
            runtime
            for runtime in self.all()
            if runtime.enabled
        ]

    def healthy(self) -> list[ProviderRuntime]:
        return [
            runtime
            for runtime in self.enabled()
            if runtime.healthy
        ]

    def free(self) -> list[ProviderRuntime]:
        return [
            runtime
            for runtime in self.enabled()
            if runtime.free_tier
        ]

    def supports(self, capability: str) -> list[ProviderRuntime]:
        key = f"supports_{capability}"
        return [
            runtime
            for runtime in self.enabled()
            if bool(getattr(runtime, key, False))
        ]

    def compatible(self, api_type: str) -> list[ProviderRuntime]:
        return [
            runtime
            for runtime in self.enabled()
            if runtime.api_type == api_type
        ]

    def best_order(self) -> list[ProviderRuntime]:
        healthy = self.healthy()
        return healthy if healthy else self.enabled()

    def highest_priority(self) -> ProviderRuntime | None:
        providers = self.enabled()
        return providers[0] if providers else None

    def best(self) -> ProviderRuntime | None:
        providers = self.best_order()
        return providers[0] if providers else None


# Backward/forward-compatible public API name used by runtime tests.
RuntimeRegistry = ProviderRegistry

registry = ProviderRegistry()
