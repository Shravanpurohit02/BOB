from builder.providers.base import BaseProvider
from builder.providers.response import ProviderResponse
from builder.providers.config import config

class GroqProvider(BaseProvider):

    name = "groq"

    def available(self):
        return bool(config.groq_api_key)

    def generate(self, request):
        raise NotImplementedError("Groq runtime will be added in Provider Sprint")
