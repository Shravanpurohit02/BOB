from builder.providers.runtime.loader import loader


class ProviderRouter:

    def _registry(self):
        return loader.load()

    def available(self):
        return self._registry().best_order()

    def healthy(self):
        return self._registry().healthy()

    def free(self):
        return self._registry().free()

    def supports(self, capability):
        return self._registry().supports(capability)

    def compatible(self, api_type):
        return self._registry().compatible(api_type)

    def best(self):
        return self._registry().best()

    def default(self):
        provider = self.best()

        if provider is not None:
            return provider

        provider = self._registry().highest_priority()

        if provider is not None:
            return provider

        available = self.available()

        return available[0] if available else None


router = ProviderRouter()
