from builder.providers.base import BaseProvider
from builder.providers.response import ProviderResponse
from builder.providers.config import config

class GeminiProvider(BaseProvider):

    name = "gemini"

    def available(self):
        return bool(config.gemini_api_key)

    def generate(self, request):
        raise NotImplementedError("Gemini runtime will be added in Provider Sprint")
