from dataclasses import dataclass, field

from builder.providers.chat.messages import Message

@dataclass(slots=True)
class ChatRequest:
    model: str
    messages: list[Message] = field(default_factory=list)
    temperature: float = 0.2
    max_tokens: int = 4096
    stream: bool = False
