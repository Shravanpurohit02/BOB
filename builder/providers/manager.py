from __future__ import annotations

from builder.providers.runtime.loader import loader
from builder.providers.runtime.router import router


class ProviderManager:
    """
    Backward-compatible provider manager backed by the runtime subsystem.
    """

    def __init__(self):
        self.loader = loader
        self.router = router

    def load(self):
        if hasattr(self.loader, "load"):
            return self.loader.load()
        if hasattr(self.loader, "reload"):
            return self.loader.reload()
        return None

    def providers(self):
        if hasattr(self.loader, "providers"):
            providers = self.loader.providers
            return providers() if callable(providers) else providers
        return []

    def get(self, *args, **kwargs):
        if hasattr(self.router, "get"):
            return self.router.get(*args, **kwargs)
        if hasattr(self.router, "route"):
            return self.router.route(*args, **kwargs)
        raise AttributeError("Runtime router exposes neither 'get' nor 'route'.")

    def generate(self, request):
        provider = self.get(request)
        if hasattr(provider, "generate"):
            return provider.generate(request)
        raise AttributeError(f"{provider!r} does not implement generate().")


manager = ProviderManager()
