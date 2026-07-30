from builder.providers.client.http import HTTPClient
from builder.providers.runtime import router


class ClientFactory:

    def create(self, provider=None):

        runtime = provider or router.default()

        return HTTPClient(runtime)


factory = ClientFactory()
