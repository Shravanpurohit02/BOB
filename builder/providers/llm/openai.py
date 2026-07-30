from builder.providers.base import BaseProvider
from builder.providers.response import ProviderResponse
from builder.providers.config import config

class OpenAIProvider(BaseProvider):

    name = "openai"

    def available(self):
        return bool(config.openai_api_key)

    def generate(self, request):
        raise NotImplementedError("OpenAI runtime will be added in Provider Sprint")
