from builder.context.cache import cache
from builder.context.compression import compressor
from builder.context.provider_optimizer import optimizer
from builder.context.token_budget import manager

NAME = "Context Intelligence"
CATEGORY = "Autonomous"
DESCRIPTION = "Validates token budgeting, compression, optimization and context cache."


def run() -> bool:

    try:

        class Provider:
            name = "openai"

        prompt = "Implement dependency graph"

        files = [
            {
                "path": "demo.py",
                "lines": 100,
                "source": "print('x')\n" * 100,
            }
        ]

        budget = manager.budget(
            Provider(),
        )

        estimate = manager.estimate(
            prompt,
        )

        compressed = compressor.compress_files(
            files,
            500,
        )

        optimized = optimizer.optimize(
            Provider(),
            prompt,
            files,
        )

        cache.put(
            "/repo",
            prompt,
            optimized,
        )

        cached = cache.get(
            "/repo",
            prompt,
        )

        ok = (
            budget == 128000
            and estimate > 0
            and len(compressed) == 1
            and optimized["budget"] == 128000
            and cached is not None
            and cached["value"]["budget"] == 128000
        )

        cache.invalidate(
            "/repo",
            prompt,
        )

        return ok

    except Exception:
        return False
