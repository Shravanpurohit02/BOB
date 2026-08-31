from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class ProviderCatalogEntry:
    name: str
    display_name: str
    env_prefix: str
    api_type: str

    default_model: str = ""
    default_base_url: str = ""

    free_tier: bool = True

    supports_streaming: bool = True
    supports_tools: bool = False
    supports_vision: bool = False
    supports_reasoning: bool = False
    supports_embeddings: bool = False

    context_window: int = 0
    max_output_tokens: int = 0

    priority: int = 100

    aliases: tuple[str, ...] = field(default_factory=tuple)


PROVIDERS = (
    ProviderCatalogEntry(
        name="gemini",
        default_model="gemini-2.5-pro",
        default_base_url="https://generativelanguage.googleapis.com",
        display_name="Google Gemini",
        env_prefix="GEMINI",
        api_type="gemini",
        supports_tools=True,
        supports_vision=True,
        supports_reasoning=True,
        context_window=2_000_000,
        max_output_tokens=65_536,
        priority=20,
    ),
    ProviderCatalogEntry(
        name="anthropic",
        default_model="claude-sonnet-4-5",
        default_base_url="https://api.anthropic.com",
        display_name="Anthropic",
        env_prefix="ANTHROPIC",
        api_type="anthropic",
        supports_tools=True,
        supports_vision=True,
        supports_reasoning=True,
        context_window=1_000_000,
        max_output_tokens=64_000,
        priority=30,
    ),
    ProviderCatalogEntry(
        name="openai",
        default_model="gpt-4.1-mini",
        default_base_url="https://api.openai.com/v1",
        display_name="OpenAI",
        env_prefix="OPENAI",
        api_type="openai",
        supports_tools=True,
        supports_vision=True,
        supports_reasoning=True,
        context_window=400_000,
        max_output_tokens=128_000,
        priority=40,
    ),
    ProviderCatalogEntry(
        name="groq",
        default_model="llama-3.3-70b-versatile",
        default_base_url="https://api.groq.com/openai/v1",
        display_name="Groq",
        env_prefix="GROQ",
        api_type="openai",
        supports_tools=True,
        supports_reasoning=True,
        context_window=131_072,
        max_output_tokens=32_768,
        priority=50,
    ),
    ProviderCatalogEntry(
        name="openrouter",
        default_model="openai/gpt-oss-120b",
        default_base_url="https://openrouter.ai/api/v1",
        display_name="OpenRouter",
        env_prefix="OPENROUTER",
        api_type="openai",
        supports_tools=True,
        supports_reasoning=True,
        context_window=200_000,
        max_output_tokens=65_536,
        priority=60,
    ),
    ProviderCatalogEntry(
        name="cerebras",
        default_model="llama-3.3-70b",
        default_base_url="https://api.cerebras.ai/v1",
        display_name="Cerebras",
        env_prefix="CEREBRAS",
        api_type="openai",
        supports_reasoning=True,
        context_window=128_000,
        max_output_tokens=32_768,
        priority=70,
    ),
    ProviderCatalogEntry(
        name="nvidia",
        default_model="meta/llama-3.3-70b-instruct",
        default_base_url="https://integrate.api.nvidia.com/v1",
        display_name="NVIDIA NIM",
        env_prefix="NVIDIA",
        api_type="openai",
        supports_reasoning=True,
        context_window=128_000,
        max_output_tokens=32_768,
        priority=10,
    ),
    ProviderCatalogEntry(
        name="mistral",
        default_model="mistral-large-latest",
        default_base_url="https://api.mistral.ai/v1",
        display_name="Mistral",
        env_prefix="MISTRAL",
        api_type="openai",
        supports_reasoning=True,
        context_window=128_000,
        max_output_tokens=32_768,
        priority=80,
    ),
    ProviderCatalogEntry(
        name="huggingface",
        default_model="Qwen/Qwen3-Coder-480B-A35B-Instruct",
        default_base_url="https://router.huggingface.co/v1",
        display_name="Hugging Face",
        env_prefix="HUGGINGFACE",
        api_type="openai",
        context_window=128_000,
        max_output_tokens=32_768,
        priority=90,
    ),
)
