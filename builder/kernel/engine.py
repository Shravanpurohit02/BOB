from __future__ import annotations

from builder.kernel.context import Context
from builder.kernel.kernel import Kernel
from builder.kernel.registry import registry
from builder.kernel.state import KernelState
from builder.runtime.runtime import Runtime


class KernelEngine:
    """
    High-level Builder kernel lifecycle manager.
    """

    def create(
        self,
        name: str,
        workspace: str,
    ) -> Kernel:

        runtime = Runtime(
            workspace=workspace,
        )

        kernel = Kernel(
            runtime=runtime,
        )

        kernel.state = KernelState().values
        kernel.context = Context().values

        registry.add(
            name,
            kernel,
        )

        return kernel

    def get(
        self,
        name: str,
    ) -> Kernel | None:

        return registry.get(name)

    def remove(
        self,
        name: str,
    ) -> None:

        registry.remove(name)

    def exists(
        self,
        name: str,
    ) -> bool:

        return registry.exists(name)

    def reset(
        self,
        name: str,
    ) -> None:

        kernel = self.get(name)

        if kernel is not None:
            kernel.reset()

    def kernels(
        self,
    ) -> list[Kernel]:

        return registry.kernels()

    def count(
        self,
    ) -> int:

        return registry.count()


engine = KernelEngine()

