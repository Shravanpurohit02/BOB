from builder.providers.runtime.request_builder import request_builder
from builder.providers.runtime.profile import ProviderProfile
from builder.providers.runtime.registry import registry


registry.register(
    ProviderProfile(
        name="openai",
        display_name="OpenAI",
        base_url="https://api.openai.com/v1/chat/completions",
        default_model="gpt-5",
        supported_models=("gpt-5", "gpt-5-mini"),
        max_context_tokens=128000,
        max_output_tokens=16384,
        max_request_bytes=20_000_000,
        supports_tools=True,
        supports_parallel_tool_calls=True,
    )
)

registry.register(
    ProviderProfile(
        name="anthropic",
        display_name="Anthropic",
        base_url="https://api.anthropic.com/v1/messages",
        default_model="claude-sonnet",
        supported_models=("claude-sonnet",),
        max_context_tokens=200000,
        max_output_tokens=8192,
        max_request_bytes=20_000_000,
        supports_tools=True,
    )
)

registry.register(
    ProviderProfile(
        name="gemini",
        display_name="Gemini",
        base_url="https://generativelanguage.googleapis.com",
        default_model="gemini-2.5-pro",
        supported_models=("gemini-2.5-pro",),
        max_context_tokens=1000000,
        max_output_tokens=65536,
        max_request_bytes=25_000_000,
        supports_tools=True,
        supports_images=True,
    )
)

registry.register(
    ProviderProfile(
        name="groq",
        display_name="Groq",
        base_url="https://api.groq.com/openai/v1/chat/completions",
        default_model="llama",
        supported_models=("llama",),
        max_context_tokens=32768,
        max_output_tokens=8192,
        max_request_bytes=4_000_000,
    )
)

registry.register(
    ProviderProfile(
        name="openrouter",
        display_name="OpenRouter",
        base_url="https://openrouter.ai/api/v1/chat/completions",
        default_model="auto",
        supported_models=("auto",),
        max_context_tokens=200000,
        max_output_tokens=8192,
        max_request_bytes=20_000_000,
        supports_tools=True,
    )
)

registry.register(
    ProviderProfile(
        name="nvidia",
        display_name="NVIDIA",
        base_url="https://integrate.api.nvidia.com/v1/chat/completions",
        default_model="default",
        supported_models=("default",),
        max_context_tokens=128000,
        max_output_tokens=8192,
        max_request_bytes=20_000_000,
    )
)

registry.register(
    ProviderProfile(
        name="cerebras",
        display_name="Cerebras",
        base_url="https://api.cerebras.ai",
        default_model="default",
        supported_models=("default",),
        max_context_tokens=128000,
        max_output_tokens=8192,
        max_request_bytes=20_000_000,
    )
)

registry.register(
    ProviderProfile(
        name="mistral",
        display_name="Mistral",
        base_url="https://api.mistral.ai/v1/chat/completions",
        default_model="mistral-large",
        supported_models=("mistral-large",),
        max_context_tokens=128000,
        max_output_tokens=8192,
        max_request_bytes=20_000_000,
    )
)

registry.register(
    ProviderProfile(
        name="huggingface",
        display_name="Hugging Face",
        base_url="https://router.huggingface.co/v1/chat/completions",
        default_model="default",
        supported_models=("default",),
        max_context_tokens=128000,
        max_output_tokens=8192,
        max_request_bytes=20_000_000,
    )
)
