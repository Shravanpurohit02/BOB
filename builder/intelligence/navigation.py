from .cross_reference import cross_reference_engine


class Navigator:

    def __init__(self):
        self._db = None

    def build(self, workspace: str):
        self._db = cross_reference_engine.build(workspace)

    def find_definition(self, name: str):
        return self._db["definitions"].get(name, [])

    def find_references(self, name: str):
        return self._db["references"].get(name, [])

    def find_callers(self, name: str):

        callers = set()

        for d in self.find_definition(name):
            key = f"{d.module}:{d.name}"
            callers.update(self._db["callers"].get(key, []))

        return sorted(callers)

    def find_usages(self, name: str):

        usages = []

        for d in self.find_definition(name):
            key = f"{d.module}:{d.name}"
            usages.extend(self._db["usages"].get(key, []))

        return usages


navigator = Navigator()
