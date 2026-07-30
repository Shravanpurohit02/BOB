from dataclasses import dataclass, field


@dataclass(slots=True)
class GeneratedDirectory:
    path: str


@dataclass(slots=True)
class GeneratedFile:
    path: str
    action: str
    language: str = "python"
    content: str = ""


@dataclass(slots=True)
class GeneratedArtifact:
    files: list[GeneratedFile] = field(default_factory=list)
    directories: list[GeneratedDirectory] = field(default_factory=list)
