from __future__ import annotations

from builder.kernel.kernel import Kernel


class KernelRegistry:
    """
    Registry of active Builder kernel instances.
    """

    def __init__(self) -> None:

        self._kernels: dict[str, Kernel] = {}

    def clear(
        self,
    ) -> None:

        self._kernels.clear()

    def add(
        self,
        name: str,
        kernel: Kernel,
    ) -> None:

        self._kernels[name] = kernel

    def remove(
        self,
        name: str,
    ) -> None:

        self._kernels.pop(
            name,
            None,
        )

    def get(
        self,
        name: str,
    ) -> Kernel | None:

        return self._kernels.get(name)

    def exists(
        self,
        name: str,
    ) -> bool:

        return name in self._kernels

    def names(
        self,
    ) -> list[str]:

        return sorted(
            self._kernels.keys()
        )

    def kernels(
        self,
    ) -> list[Kernel]:

        return [
            self._kernels[name]
            for name in self.names()
        ]

    def count(
        self,
    ) -> int:

        return len(self._kernels)


registry = KernelRegistry()

