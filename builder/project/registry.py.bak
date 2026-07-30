from builder.project.model import ProjectFile

class ProjectRegistry:

    def __init__(self):
        self._files = {}

    def add(self, file: ProjectFile):
        self._files[file.path] = file

    def get(self, path: str):
        return self._files.get(path)

    def all(self):
        return list(self._files.values())

registry = ProjectRegistry()
