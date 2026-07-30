from dataclasses import dataclass
from time import monotonic


@dataclass(slots=True)
class Timeout:

    seconds: float = 300.0

    def __post_init__(self):
        self.started = monotonic()

    @property
    def expired(self):
        return (monotonic() - self.started) >= self.seconds

    def remaining(self):
        return max(
            0.0,
            self.seconds - (monotonic() - self.started),
        )


class TimeoutError(RuntimeError):
    pass


def ensure(timeout: Timeout):

    if timeout.expired:
        raise TimeoutError(
            f"Execution timeout after {timeout.seconds:.2f}s"
        )
