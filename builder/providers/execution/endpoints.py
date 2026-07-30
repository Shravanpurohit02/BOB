from __future__ import annotations


class EndpointRouter:
    """
    Resolves the correct REST endpoint for each provider API type.
    """

    DEFAULTS = {
        "openai": "/chat/completions",
        "openrouter": "/chat/completions",
        "groq": "/chat/completions",
        "nvidia": "/chat/completions",
        "cerebras": "/chat/completions",
        "mistral": "/chat/completions",
        "huggingface": "/chat/completions",
        "anthropic": "/v1/messages",
    }

    def endpoint(self, provider, model=None):

        api_type = getattr(provider, "api_type", "openai")

        if api_type == "gemini":
            model_name = model or getattr(provider, "model", "")
            return f"/models/{model_name}:generateContent"

        return self.DEFAULTS.get(
            api_type,
            "/chat/completions",
        )


router = EndpointRouter()
