from dataclasses import dataclass, field
from pathlib import Path
import re


@dataclass(slots=True)
class FileResolutionResult:
    query: str
    exact: list[str] = field(default_factory=list)
    partial: list[str] = field(default_factory=list)


class FileResolver:

    STOP_WORDS = {
        "add", "create", "delete", "remove", "update", "modify",
        "change", "replace", "rename", "move", "copy", "fix",
        "implement", "refactor", "generate", "write", "using",
        "use", "with", "into", "from", "to", "and", "or",
        "the", "a", "an",
    }

    IGNORE = {
        ".git",
        ".builder",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".venv",
        "venv",
        "node_modules",
        "build",
        "dist",
    }

    def __init__(self):
        self.files = {}

    def build(self, workspace: str):

        self.files.clear()

        root = Path(workspace)

        for file in root.rglob("*"):

            if not file.is_file():
                continue

            if any(part in self.IGNORE for part in file.parts):
                continue

            rel = file.relative_to(root).as_posix()

            self.files[rel] = {
                "path": rel,
                "name": file.name,
                "stem": file.stem,
                "suffix": file.suffix,
            }

    def _tokens(self, query: str):

        return [
            t.lower()
            for t in re.findall(r"[A-Za-z0-9_.-]+", query)
            if t.lower() not in self.STOP_WORDS
        ]

    def resolve(self, query: str):

        result = FileResolutionResult(query=query)

        seen = set()

        for token in self._tokens(query):

            for file in self.files.values():

                path = file["path"].lower()
                name = file["name"].lower()
                stem = file["stem"].lower()

                if token == name or token == stem:

                    if path not in seen:
                        seen.add(path)
                        result.exact.append(file["path"])

                elif (
                    token in path
                    or token in name
                    or token in stem
                ):

                    if path not in seen:
                        seen.add(path)
                        result.partial.append(file["path"])

        return result


file_resolver = FileResolver()
