"""Plugin lifecycle, registration, and optional entry-point discovery."""
from typing import Any, Dict, Iterable, Iterator


class Plugin:
    name = "plugin"

    def setup(self, _context: Any) -> None:
        pass

    def teardown(self, _context: Any) -> None:
        pass


class PluginManager:
    def __init__(self) -> None:
        self.plugins: Dict[str, Plugin] = {}
        self._started = False

    def register(self, plugin: Plugin) -> Plugin:
        self.plugins[plugin.name] = plugin
        return plugin

    def load(self, plugins: Iterable[Plugin], context: Any) -> None:
        for plugin in plugins:
            self.register(plugin)
            plugin.setup(context)
        self._started = True

    def discover(self, group: str = "coding_agent.plugins") -> Iterator[Plugin]:
        from importlib.metadata import entry_points
        points = entry_points()
        selected = points.select(group=group) if hasattr(points, "select") else points.get(group, [])
        for point in selected:
            loaded = point.load()
            yield loaded() if isinstance(loaded, type) else loaded

    def unload(self, context: Any) -> None:
        for plugin in reversed(list(self.plugins.values())):
            plugin.teardown(context)
        self._started = False
