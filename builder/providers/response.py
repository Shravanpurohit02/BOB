from dataclasses import dataclass

@dataclass(slots=True)
class ProviderResponse:
    success: bool
    content: str = ""
    provider: str = ""
