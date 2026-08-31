from builder.providers.health import engine as health_engine
from builder.providers.health.circuit import engine as circuit_engine


class RuntimeRegistry:
    def __init__(self):
        self.providers = {}

    #
    # Existing API
    #

    def register(self, provider):
        self.providers[provider.name] = provider

    def get(self, name):
        return self.providers.get(name)

    def all(self):
        return list(self.providers.values())

    #
    # Capability Queries
    #

    def enabled(self):
        return [p for p in self.providers.values() if p.enabled]

    def healthy(self):
        return [p for p in self.enabled() if p.healthy]

    def free(self):
        return [p for p in self.enabled() if p.free_tier]

    def compatible(self, api_type):
        return [p for p in self.enabled() if p.api_type == api_type]

    def supports(self, capability):

        attribute = f"supports_{capability}"

        return [
            p
            for p in self.enabled()
            if getattr(
                p,
                attribute,
                False,
            )
        ]

    #
    # Selection
    #

    def highest_priority(self):

        providers = sorted(
            self.enabled(),
            key=lambda p: p.priority,
        )

        return providers[0] if providers else None

    def best(self):

        providers = [p for p in self.healthy() if circuit_engine.allow(p.name)]

        if not providers:
            return None

        ranking = {p.provider: p.score for p in health_engine.ranking()}

        providers.sort(
            key=lambda p: (
                -ranking.get(p.name, 100.0),
                p.priority,
                not p.free_tier,
            )
        )

        return providers[0]

    def best_order(self):

        providers = [p for p in self.healthy() if circuit_engine.allow(p.name)]

        ranking = {p.provider: p.score for p in health_engine.ranking()}

        providers.sort(
            key=lambda p: (
                -ranking.get(p.name, 100.0),
                p.priority,
                not p.free_tier,
            )
        )

        return providers


registry = RuntimeRegistry()
