"""
Time_Warp IDE Plugin Manager
Central management for the plugin system
"""

from typing import Dict, List, Any, Optional, Callable
import os
from .base import PluginInterface, PluginType
from .registry import PluginRegistry
from .loader import PluginLoader
from ..runtime.engine import RuntimeEngine, ExecutionContext
from ..stdlib.core import StandardLibrary


class PluginManager:
    """Central plugin management"""

    def __init__(self, runtime: Optional[RuntimeEngine] = None):
        self.registry = PluginRegistry()
        self.loader = PluginLoader(self.registry)
        self.runtime = runtime
        self.integration_context: Dict[str, Any] = {}

        # Setup default plugin paths
        self._setup_default_paths()

        # Load built-in plugins
        self._load_builtin_plugins()

    def _setup_default_paths(self):
        """Setup default plugin search paths"""
        # Add common plugin directories
        possible_paths = [
            os.path.join(os.getcwd(), "plugins"),
            os.path.join(os.path.expanduser("~"), ".time_warp", "plugins"),
            os.path.join(os.path.dirname(__file__), "builtin"),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                self.loader.add_plugin_path(path)

    def _load_builtin_plugins(self):
        """Load built-in plugins"""
        from .base import MathLibraryPlugin, LoggingPlugin

        # Register built-in plugins
        math_plugin = MathLibraryPlugin()
        logging_plugin = LoggingPlugin()

        self.registry.register(math_plugin)
        self.registry.register(logging_plugin)

    def load_plugins_from_directory(self, directory: str) -> Dict[str, bool]:
        """Load plugins from a directory"""
        self.loader.add_plugin_path(directory)
        plugins = self.loader.load_plugin_directory(directory)

        results = {}
        for plugin in plugins:
            results[plugin.metadata.name] = self.registry.register(plugin)

        return results

    def load_plugin_file(self, filepath: str) -> Dict[str, bool]:
        """Load plugins from a file"""
        plugins = self.loader.load_plugin_file(filepath)

        results = {}
        for plugin in plugins:
            results[plugin.metadata.name] = self.registry.register(plugin)

        return results

    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin"""
        success = self.registry.enable(plugin_name)
        if success:
            self._integrate_plugin(plugin_name)
        return success

    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin"""
        self._unintegrate_plugin(plugin_name)
        return self.registry.disable(plugin_name)

    def _integrate_plugin(self, plugin_name: str):
        """Integrate plugin with runtime systems"""
        plugin = self.registry.get_plugin(plugin_name)
        if not plugin or not plugin.is_enabled:
            return

        # Integrate function library plugins
        if plugin.metadata.plugin_type == PluginType.FUNCTION_LIBRARY:
            self._integrate_function_library(plugin)

        # Integrate runtime hook plugins
        elif plugin.metadata.plugin_type == PluginType.RUNTIME_HOOK:
            self._integrate_runtime_hooks(plugin)

        # Integrate mode handler plugins
        elif plugin.metadata.plugin_type == PluginType.MODE_HANDLER:
            self._integrate_mode_handler(plugin)

    def _unintegrate_plugin(self, plugin_name: str):
        """Remove plugin integration"""
        plugin = self.registry.get_plugin(plugin_name)
        if not plugin:
            return

        # Remove from integration context
        if plugin_name in self.integration_context:
            del self.integration_context[plugin_name]

    def _integrate_function_library(self, plugin: PluginInterface):
        """Integrate function library plugin"""
        if not hasattr(plugin, "get_functions"):
            return

        # Get runtime context
        if self.runtime:
            stdlib = self.runtime.context.stdlib

            # Add functions
            functions = plugin.get_functions()
            for name, func in functions.items():
                stdlib.register_function(name, func, overwrite=True)

            # Add constants
            if hasattr(plugin, "get_constants"):
                constants = plugin.get_constants()
                for name, value in constants.items():
                    stdlib.register_constant(name, value, overwrite=True)

    def _integrate_runtime_hooks(self, plugin: PluginInterface):
        """Integrate runtime hook plugin"""
        # Store hooks for runtime to call
        self.integration_context[plugin.metadata.name] = {
            "type": "runtime_hooks",
            "plugin": plugin,
        }

    def _integrate_mode_handler(self, plugin: PluginInterface):
        """Integrate mode handler plugin"""
        if hasattr(plugin, "get_mode_name"):
            mode_name = plugin.get_mode_name()
            self.integration_context[plugin.metadata.name] = {
                "type": "mode_handler",
                "mode_name": mode_name,
                "plugin": plugin,
            }

    def get_runtime_hooks(self) -> List[PluginInterface]:
        """Get all enabled runtime hook plugins"""
        hooks = []
        for context in self.integration_context.values():
            if context.get("type") == "runtime_hooks":
                hooks.append(context["plugin"])
        return hooks

    def get_mode_handlers(self) -> Dict[str, PluginInterface]:
        """Get all enabled mode handler plugins"""
        handlers = {}
        for context in self.integration_context.values():
            if context.get("type") == "mode_handler":
                handlers[context["mode_name"]] = context["plugin"]
        return handlers

    def call_runtime_hooks(self, hook_name: str, *args, **kwargs):
        """Call a runtime hook on all hook plugins"""
        for plugin in self.get_runtime_hooks():
            if hasattr(plugin, hook_name):
                try:
                    getattr(plugin, hook_name)(*args, **kwargs)
                except Exception as e:
                    print(
                        f"Error in plugin {plugin.metadata.name} hook {hook_name}: {e}"
                    )

    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all plugins"""
        return self.registry.list_plugins()

    def list_enabled_plugins(self) -> List[str]:
        """List enabled plugins"""
        return self.registry.list_enabled_plugins()

    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific plugin"""
        plugin = self.registry.get_plugin(plugin_name)
        return plugin.get_info() if plugin else None

    def enable_all_plugins(self) -> Dict[str, bool]:
        """Enable all possible plugins"""
        return self.registry.enable_all_possible()

    def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a plugin"""
        # Unintegrate first
        self._unintegrate_plugin(plugin_name)

        # Reload
        success = self.loader.reload_plugin(plugin_name)

        # Re-integrate if successful
        if success:
            self.enable_plugin(plugin_name)

        return success

    def create_plugin_template(
        self, filepath: str, plugin_type: PluginType = PluginType.FUNCTION_LIBRARY
    ):
        """Create a plugin template"""
        self.loader.create_plugin_template(filepath, plugin_type)

    def get_statistics(self) -> Dict[str, Any]:
        """Get plugin manager statistics"""
        registry_stats = self.registry.get_statistics()
        loader_stats = self.loader.get_statistics()

        return {
            "registry": registry_stats,
            "loader": loader_stats,
            "integration_contexts": len(self.integration_context),
            "runtime_hooks": len(self.get_runtime_hooks()),
            "mode_handlers": len(self.get_mode_handlers()),
        }

    def execute_with_hooks(self, program: Any) -> Any:
        """Execute program with plugin hooks"""
        if not self.runtime:
            return None

        # Call pre-execution hooks
        self.call_runtime_hooks("on_program_start", self.runtime.context.__dict__)

        try:
            result = self.runtime.execute(program)
            return result
        except Exception as e:
            # Call error hooks
            self.call_runtime_hooks("on_error", e, self.runtime.context.__dict__)
            raise
        finally:
            # Call post-execution hooks
            self.call_runtime_hooks("on_program_end", self.runtime.context.__dict__)

    def extend_stdlib_with_plugins(self, stdlib: StandardLibrary):
        """Extend standard library with plugin functions"""
        function_plugins = self.registry.get_enabled_plugins_by_type(
            PluginType.FUNCTION_LIBRARY
        )

        for plugin in function_plugins:
            if hasattr(plugin, "get_functions"):
                functions = plugin.get_functions()
                for name, func in functions.items():
                    stdlib.register_function(name, func, overwrite=True)

            if hasattr(plugin, "get_constants"):
                constants = plugin.get_constants()
                for name, value in constants.items():
                    stdlib.register_constant(name, value, overwrite=True)
