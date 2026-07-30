from dataclasses import dataclass

@dataclass(slots=True)
class CompatibilityResponse:
    text: str
    modified: bool = False
