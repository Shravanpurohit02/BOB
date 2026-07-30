from dataclasses import dataclass

@dataclass(slots=True)
class ChatResponse:
    success: bool
    provider: str
    model: str
    content: str
    raw: dict | None = None
