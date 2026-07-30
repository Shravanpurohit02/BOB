from dataclasses import dataclass

@dataclass(slots=True)
class ExecutionResponse:
    success: bool
    provider: str
    model: str
    text: str
    usage: dict
    raw: dict
