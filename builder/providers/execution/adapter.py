from builder.providers.client import manager
from builder.providers.runtime import router

class Adapter:

    def client(self, provider=None):
        provider = provider or router.default()
        return provider, manager.client(provider)

adapter = Adapter()
