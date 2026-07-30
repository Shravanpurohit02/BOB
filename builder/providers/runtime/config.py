from dataclasses import dataclass


@dataclass(slots=True)
class ProviderRuntime:
    #
    # Existing fields (backward compatible)
    #
    name: str
    api_key: str
    base_url: str
    model: str
    enabled: bool

    #
    # Identity
    #
    display_name: str = ""
    api_type: str = "native"

    #
    # Policy
    #
    free_tier: bool = False
    priority: int = 100
    auto_select: bool = True

    #
    # Capabilities
    #
    supports_streaming: bool = True
    supports_tools: bool = False
    supports_vision: bool = False
    supports_reasoning: bool = False
    supports_embeddings: bool = False

    #
    # Model metadata
    #
    context_window: int = 0
    max_output_tokens: int = 0

    #
    # Runtime metadata (read-only defaults)
    #
    healthy: bool = True
    average_latency: float = 0.0
    success_rate: float = 1.0
    failure_count: int = 0
