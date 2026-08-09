
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True)
class ProviderProfile:
    name: str
    display_name: str
    base_url: str

    default_model: str
    supported_models: tuple[str, ...]

    max_context_tokens: int
    max_output_tokens: int
    max_request_bytes: int

    reserved_output_tokens: int = 4096

    supports_streaming: bool = True
    supports_tools: bool = False
    supports_json: bool = True
    supports_images: bool = False
    supports_audio: bool = False
    supports_system_prompt: bool = True
    supports_parallel_tool_calls: bool = False

    timeout: float = 120.0
    max_retries: int = 3
    backoff_factor: float = 2.0

    compression_threshold: float = 0.80
    target_context_utilization: float = 0.70
    safety_margin_tokens: int = 2048

    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def usable_input_tokens(self) -> int:
        usable = (
            self.max_context_tokens
            - self.reserved_output_tokens
            - self.safety_margin_tokens
        )
        return max(usable, 0)

    def supports_model(self, model: str) -> bool:
        return model in self.supported_models
