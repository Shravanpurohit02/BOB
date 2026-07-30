from builder.models.service import Service

class ServiceContainer:

    def __init__(self):
        self._services = {}

    def register(self, name: str, implementation, singleton: bool = True):
        self._services[name] = Service(
            name=name,
            implementation=implementation,
            singleton=singleton,
        )

    def resolve(self, name: str):
        service = self._services.get(name)
        if service is None:
            raise KeyError(name)
        return service.implementation

    def exists(self, name: str):
        return name in self._services

    def all(self):
        return list(self._services.values())

container = ServiceContainer()
