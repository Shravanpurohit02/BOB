from builder.providers.runtime.config import ProviderRuntime
from builder.providers.runtime.context_budget import ContextBudgetEngine
from builder.providers.runtime.registry import RuntimeRegistry


def make_runtime(name, model, context_window, max_output_tokens):
    return ProviderRuntime(
        name=name,
        api_key="test-key",
        base_url="https://example.test",
        model=model,
        enabled=True,
        context_window=context_window,
        max_output_tokens=max_output_tokens,
    )


def test_budget_resolves_provider():
    from builder.providers.runtime import context_budget

    original = context_budget.registry
    registry = RuntimeRegistry()
    registry.register(
        make_runtime(
            "openai",
            "gpt-test",
            400_000,
            128_000,
        )
    )

    context_budget.registry = registry

    try:
        result = ContextBudgetEngine().budget(
            provider="openai",
            model="gpt-test",
        )

        assert result.context_window == 400_000
        assert result.max_output_tokens == 128_000
        assert result.available_input_tokens == 270_976
    finally:
        context_budget.registry = original


def test_budget_resolves_model_when_provider_is_missing():
    from builder.providers.runtime import context_budget

    original = context_budget.registry
    registry = RuntimeRegistry()
    registry.register(
        make_runtime(
            "gemini",
            "gemini-test",
            2_000_000,
            65_536,
        )
    )

    context_budget.registry = registry

    try:
        result = ContextBudgetEngine().budget(
            provider="",
            model="GEMINI-TEST",
        )

        assert result.context_window == 2_000_000
        assert result.max_output_tokens == 65_536
        assert result.available_input_tokens == 1_933_440
    finally:
        context_budget.registry = original


def test_unknown_provider_uses_safe_fallback():
    from builder.providers.runtime import context_budget

    original = context_budget.registry
    registry = RuntimeRegistry()
    context_budget.registry = registry

    try:
        result = ContextBudgetEngine().budget(
            provider="does-not-exist",
            model="unknown",
        )

        assert result.context_window == 8192
        assert result.max_output_tokens == 2048
        assert result.available_input_tokens == 5120
    finally:
        context_budget.registry = original


def test_missing_provider_and_model_use_safe_fallback():
    from builder.providers.runtime import context_budget

    original = context_budget.registry
    registry = RuntimeRegistry()
    context_budget.registry = registry

    try:
        result = ContextBudgetEngine().budget()

        assert result.context_window == 8192
        assert result.max_output_tokens == 2048
        assert result.available_input_tokens == 5120
    finally:
        context_budget.registry = original
