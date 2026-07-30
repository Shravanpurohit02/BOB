from builder.models.plugin import Plugin

class PluginRegistry:

    def __init__(self):
        self._plugins = {}

    def register(self, plugin: Plugin):
        self._plugins[plugin.name] = plugin

    def get(self, name: str):
        return self._plugins.get(name)

    def all(self):
        return list(self._plugins.values())

registry = PluginRegistry()
