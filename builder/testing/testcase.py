from dataclasses import dataclass

@dataclass(slots=True)
class TestCase:
    name: str
    callback: callable
