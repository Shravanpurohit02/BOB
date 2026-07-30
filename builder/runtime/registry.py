from __future__ import annotations

from builder.runtime.runtime import Runtime


class RuntimeRegistry:
    """
    In-memory registry of active Builder runtimes.
    """

    def __init__(self) -> None:

        self._runtimes: dict[str, Runtime] = {}

    def clear(
        self,
    ) -> None:

        self._runtimes.clear()

    def add(
        self,
        runtime: Runtime,
    ) -> None:

        self._runtimes[runtime.workspace] = runtime

    def remove(
        self,
        workspace: str,
    ) -> None:

        self._runtimes.pop(
            workspace,
            None,
        )

    def get(
        self,
        workspace: str,
    ) -> Runtime | None:

        return self._runtimes.get(
            workspace,
        )

    def exists(
        self,
        workspace: str,
    ) -> bool:

        return workspace in self._runtimes

    def runtimes(
        self,
    ) -> list[Runtime]:

        return sorted(
            self._runtimes.values(),
            key=lambda runtime: runtime.workspace,
        )

    def workspaces(
        self,
    ) -> list[str]:

        return sorted(
            self._runtimes.keys()
        )

    def count(
        self,
    ) -> int:

        return len(self._runtimes)


registry = RuntimeRegistry()

