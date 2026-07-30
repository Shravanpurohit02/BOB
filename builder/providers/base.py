from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseProvider(ABC):
    """
    Abstract base class implemented by all providers.
    """

    name: str = ""

    enabled: bool = True

    @abstractmethod
    def generate(
        self,
        prompt: str,
        **kwargs: Any,
    ) -> Any:
        """
        Execute a generation request.
        """

    def health(
        self,
    ) -> dict[str, Any]:

        return {
            "provider": self.name,
            "enabled": self.enabled,
        }

    def configure(
        self,
        **kwargs: Any,
    ) -> None:

        for key, value in kwargs.items():
            setattr(self, key, value)

    def enable(
        self,
    ) -> None:

        self.enabled = True

    def disable(
        self,
    ) -> None:

        self.enabled = False


