class TokenBudgetManager:

    DEFAULT_BUDGET = 120000

    PROVIDER_LIMITS = {
        "openai": 128000,
        "anthropic": 200000,
        "gemini": 1000000,
        "groq": 131072,
        "openrouter": 200000,
        "mistral": 32000,
        "cerebras": 128000,
        "nvidia": 128000,
        "huggingface": 32768,
    }

    def budget(self, provider=None):

        if not provider:
            return self.DEFAULT_BUDGET

        return self.PROVIDER_LIMITS.get(
            provider.name.lower(),
            self.DEFAULT_BUDGET,
        )

    def estimate(self, text):

        return max(
            1,
            len(text) // 4,
        )

    def remaining(
        self,
        provider,
        prompt,
    ):

        limit = self.budget(provider)

        used = self.estimate(prompt)

        return max(
            0,
            limit - used,
        )


manager = TokenBudgetManager()
