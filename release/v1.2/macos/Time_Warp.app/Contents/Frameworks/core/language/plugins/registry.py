"""
Time_Warp IDE Plugin Registry
Central registry for managing loaded plugins
"""

from typing import Dict, List, Optional, Set, Any
from .base import PluginInterface, PluginType, PluginMetadata
from ..errors.error_manager import TimeWarpError, ErrorCode, ErrorSeverity


class PluginRegistry:
    """Central registry for plugins"""

    def __init__(self):
        self.plugins: Dict[str, PluginInterface] = {}
        self.plugins_by_type: Dict[PluginType, List[PluginInterface]] = {}
        self.enabled_plugins: Set[str] = set()
        self.dependencies: Dict[str, Set[str]] = {}

    def register(self, plugin: PluginInterface) -> bool:
        """Register a plugin"""
        if plugin.metadata.name in self.plugins:
            return False  # Already registered

        # Check dependencies
        if not self._check_dependencies(plugin):
            return False

        self.plugins[plugin.metadata.name] = plugin

        # Add to type registry
        plugin_type = plugin.metadata.plugin_type
        if plugin_type not in self.plugins_by_type:
            self.plugins_by_type[plugin_type] = []
        self.plugins_by_type[plugin_type].append(plugin)

        # Track dependencies
        self.dependencies[plugin.metadata.name] = set(
            plugin.metadata.dependencies or []
        )

        return True

    def unregister(self, plugin_name: str) -> bool:
        """Unregister a plugin"""
        if plugin_name not in self.plugins:
            return False

        plugin = self.plugins[plugin_name]

        # Check if other plugins depend on this one
        dependents = self._get_dependents(plugin_name)
        if dependents:
            return False  # Cannot unregister, other plugins depend on it

        # Cleanup plugin
        if plugin.is_enabled:
            self.disable(plugin_name)

        plugin.cleanup()

        # Remove from registries
        del self.plugins[plugin_name]
        del self.dependencies[plugin_name]

        plugin_type = plugin.metadata.plugin_type
        if plugin_type in self.plugins_by_type:
            self.plugins_by_type[plugin_type].remove(plugin)

        return True

    def enable(self, plugin_name: str) -> bool:
        """Enable a plugin"""
        if plugin_name not in self.plugins:
            return False

        plugin = self.plugins[plugin_name]
        if plugin.is_enabled:
            return True

        # Check dependencies are enabled
        for dep in plugin.metadata.dependencies or []:
            if dep not in self.enabled_plugins:
                return False

        # Enable plugin
        if plugin.initialize({}):
            self.enabled_plugins.add(plugin_name)
            return True

        return False

    def disable(self, plugin_name: str) -> bool:
        """Disable a plugin"""
        if plugin_name not in self.plugins:
            return False

        plugin = self.plugins[plugin_name]
        if not plugin.is_enabled:
            return True

        # Check if other enabled plugins depend on this one
        dependents = self._get_enabled_dependents(plugin_name)
        if dependents:
            return False

        # Disable plugin
        if plugin.cleanup():
            self.enabled_plugins.discard(plugin_name)
            return True

        return False

    def get_plugin(self, plugin_name: str) -> Optional[PluginInterface]:
        """Get a plugin by name"""
        return self.plugins.get(plugin_name)

    def get_plugins_by_type(self, plugin_type: PluginType) -> List[PluginInterface]:
        """Get all plugins of a specific type"""
        return self.plugins_by_type.get(plugin_type, [])

    def get_enabled_plugins_by_type(
        self, plugin_type: PluginType
    ) -> List[PluginInterface]:
        """Get enabled plugins of a specific type"""
        return [p for p in self.get_plugins_by_type(plugin_type) if p.is_enabled]

    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all registered plugins"""
        return [plugin.get_info() for plugin in self.plugins.values()]

    def list_enabled_plugins(self) -> List[str]:
        """List enabled plugin names"""
        return list(self.enabled_plugins)

    def _check_dependencies(self, plugin: PluginInterface) -> bool:
        """Check if plugin dependencies are satisfied"""
        for dep in plugin.metadata.dependencies or []:
            if dep not in self.plugins:
                return False
        return True

    def _get_dependents(self, plugin_name: str) -> List[str]:
        """Get plugins that depend on the given plugin"""
        dependents = []
        for name, deps in self.dependencies.items():
            if plugin_name in deps:
                dependents.append(name)
        return dependents

    def _get_enabled_dependents(self, plugin_name: str) -> List[str]:
        """Get enabled plugins that depend on the given plugin"""
        dependents = self._get_dependents(plugin_name)
        return [name for name in dependents if name in self.enabled_plugins]

    def validate_plugin_order(self) -> List[str]:
        """Get plugins in dependency order"""
        ordered = []
        visited = set()
        temp_visited = set()

        def visit(plugin_name: str):
            if plugin_name in temp_visited:
                raise ValueError(
                    f"Circular dependency detected involving {plugin_name}"
                )
            if plugin_name in visited:
                return

            temp_visited.add(plugin_name)

            # Visit dependencies first
            for dep in self.dependencies.get(plugin_name, []):
                visit(dep)

            temp_visited.remove(plugin_name)
            visited.add(plugin_name)
            ordered.append(plugin_name)

        for plugin_name in self.plugins:
            if plugin_name not in visited:
                visit(plugin_name)

        return ordered

    def enable_all_possible(self) -> Dict[str, bool]:
        """Enable all plugins that can be enabled"""
        results = {}
        ordered_plugins = self.validate_plugin_order()

        for plugin_name in ordered_plugins:
            results[plugin_name] = self.enable(plugin_name)

        return results

    def get_statistics(self) -> Dict[str, Any]:
        """Get plugin statistics"""
        total = len(self.plugins)
        enabled = len(self.enabled_plugins)
        by_type = {}

        for plugin_type, plugins in self.plugins_by_type.items():
            by_type[plugin_type.value] = {
                "total": len(plugins),
                "enabled": len([p for p in plugins if p.is_enabled]),
            }

        return {
            "total_plugins": total,
            "enabled_plugins": enabled,
            "disabled_plugins": total - enabled,
            "by_type": by_type,
        }
