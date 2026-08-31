"""BOB application bridge for external clients."""

from .service import ApplicationBridge, BridgeRequestError

__all__ = ["ApplicationBridge", "BridgeRequestError"]
