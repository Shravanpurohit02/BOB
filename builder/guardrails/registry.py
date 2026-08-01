from __future__ import annotations

from collections.abc import Iterable

from .config import GuardrailConfig
from .exceptions import RegistryError
from .validators.base import BaseValidator


class ValidatorRegistry:
    """
    Registry for guardrail validators.

    Responsible for:
    - registration
    - ordering
    - enable/disable filtering
    """

    def __init__(
        self,
        config: GuardrailConfig | None = None,
    ) -> None:
        self.config = config or GuardrailConfig()
        self._validators: dict[str, BaseValidator] = {}

    def register(
        self,
        validator: BaseValidator,
    ) -> None:
        if validator.name in self._validators:
            raise RegistryError(f"Validator '{validator.name}' already registered.")

        self._validators[validator.name] = validator

    def unregister(
        self,
        name: str,
    ) -> None:
        self._validators.pop(name, None)

    def get(
        self,
        name: str,
    ) -> BaseValidator:
        try:
            return self._validators[name]
        except KeyError as exc:
            raise RegistryError(f"Unknown validator '{name}'.") from exc

    def exists(
        self,
        name: str,
    ) -> bool:
        return name in self._validators

    def all(self) -> list[BaseValidator]:
        return sorted(
            self._validators.values(),
            key=lambda validator: validator.priority,
        )

    def enabled(self) -> list[BaseValidator]:
        validators: list[BaseValidator] = []

        for validator in self.all():
            if self.config.is_enabled(validator.name):
                validators.append(validator)

        return validators

    def names(self) -> list[str]:
        return list(self._validators.keys())

    def clear(self) -> None:
        self._validators.clear()

    def __contains__(
        self,
        name: str,
    ) -> bool:
        return name in self._validators

    def __len__(self) -> int:
        return len(self._validators)

    def __iter__(self) -> Iterable[BaseValidator]:
        return iter(self.all())
