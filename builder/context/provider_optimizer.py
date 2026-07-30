from builder.context.token_budget import manager
from builder.context.compression import compressor


class ProviderContextOptimizer:

    RESERVED_OUTPUT_TOKENS = 8192

    def optimize(
        self,
        provider,
        prompt,
        files,
    ):

        budget = manager.budget(provider)

        available = max(
            0,
            budget - self.RESERVED_OUTPUT_TOKENS,
        )

        prompt_cost = manager.estimate(prompt)

        file_budget = max(
            0,
            available - prompt_cost,
        )

        optimized = compressor.compress_files(
            files,
            file_budget,
        )

        return {
            "budget": budget,
            "prompt_tokens": prompt_cost,
            "file_budget": file_budget,
            "files": optimized,
        }


optimizer = ProviderContextOptimizer()
