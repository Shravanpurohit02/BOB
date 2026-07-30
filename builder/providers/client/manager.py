from builder.providers.client.factory import factory

class ClientManager:

    def __init__(self):
        self._clients = {}

    def client(self, provider=None):
        key = provider.name if provider else "default"

        if key not in self._clients:
            self._clients[key] = factory.create(provider)

        return self._clients[key]

manager = ClientManager()
