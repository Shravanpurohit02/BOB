from dataclasses import dataclass


@dataclass(slots=True)
class CancellationToken:

    cancelled: bool = False

    reason: str = ""

    def cancel(self, reason="Cancelled"):

        self.cancelled = True
        self.reason = reason


class CancellationError(RuntimeError):
    pass


def ensure(token: CancellationToken):

    if token.cancelled:
        raise CancellationError(token.reason)
