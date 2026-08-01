from typing import ClassVar


class Pipeline:
    STAGES: ClassVar[tuple[str, ...]] = (
        "workspace",
        "reflection",
        "dependency",
        "planning",
        "generation",
        "validation",
        "patch",
        "testing",
        "deployment",
    )

    def stages(self) -> list[str]:
        return list(self.STAGES)


pipeline = Pipeline()
