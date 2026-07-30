from dataclasses import dataclass

@dataclass(slots=True)
class RetryPolicy:
    max_attempts: int = 3

policy = RetryPolicy()
