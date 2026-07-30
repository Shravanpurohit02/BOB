from dataclasses import dataclass

@dataclass(slots=True)
class ValidationResult:
    path: str
    success: bool
    message: str = ""
