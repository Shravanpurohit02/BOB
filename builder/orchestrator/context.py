from dataclasses import dataclass, field


@dataclass(slots=True)
class BuildContext:

    project: str

    files: int

    modules: int

    dependencies: int

    repository: list[str] = field(default_factory=list)

    def __str__(self):

        lines = [
            f"Project: {self.project}",
            f"Files: {self.files}",
            f"Modules: {self.modules}",
            f"Dependencies: {self.dependencies}",
            "",
            "Repository Files:",
        ]

        lines.extend(sorted(self.repository))

        return "\n".join(lines)
