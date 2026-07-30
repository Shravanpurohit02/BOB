from dataclasses import dataclass

@dataclass(slots=True)
class TestResult:
    name: str
    success: bool
    duration: float
    message: str = ""
