from builder.models.capability import Capability

class CapabilityRegistry:

    def __init__(self):
        self._items = {}

    def register(self, capability: Capability):
        self._items[capability.name] = capability

    def get(self, name: str):
        return self._items.get(name)

    def all(self):
        return list(self._items.values())

capabilities = CapabilityRegistry()
