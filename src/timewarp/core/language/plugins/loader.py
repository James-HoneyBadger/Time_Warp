"""
Time_Warp IDE Plugin Loader
Dynamic plugin loading from files and directories
"""

import os
import sys
import importlib
import importlib.util
from types import ModuleType
from typing import List, Dict, Any, Optional, Type
import traceback

from .base import PluginInterface, PluginMetadata, PluginType
from .registry import PluginRegistry
from ..errors.error_manager import TimeWarpError, ErrorCode, ErrorSeverity


class PluginLoader:
    """Loads plugins from files and directories"""

    def __init__(self, registry: PluginRegistry):
        self.registry = registry
        self.loaded_modules: Dict[str, ModuleType] = {}
        self.plugin_paths: List[str] = []

    def add_plugin_path(self, path: str):
        """Add a path to search for plugins"""
        if os.path.exists(path) and path not in self.plugin_paths:
            self.plugin_paths.append(path)
            if path not in sys.path:
                sys.path.insert(0, path)

    def load_plugin_file(self, filepath: str) -> List[PluginInterface]:
        """Load plugins from a single file"""
        plugins = []

        try:
            # Get module name from filepath
            module_name = os.path.splitext(os.path.basename(filepath))[0]

            # Load module
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            if spec is None or spec.loader is None:
                return plugins

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            self.loaded_modules[filepath] = module

            # Find plugin classes in module
            plugins.extend(self._extract_plugins_from_module(module))

        except Exception as e:
            print(f"Error loading plugin from {filepath}: {e}")
            traceback.print_exc()

        return plugins

    def load_plugin_directory(self, directory: str) -> List[PluginInterface]:
        """Load all plugins from a directory"""
        plugins = []

        if not os.path.isdir(directory):
            return plugins

        for filename in os.listdir(directory):
            if filename.endswith(".py") and not filename.startswith("_"):
                filepath = os.path.join(directory, filename)
                plugins.extend(self.load_plugin_file(filepath))

        return plugins

    def load_plugins_from_paths(self) -> List[PluginInterface]:
        """Load plugins from all configured paths"""
        plugins = []

        for path in self.plugin_paths:
            if os.path.isfile(path):
                plugins.extend(self.load_plugin_file(path))
            elif os.path.isdir(path):
                plugins.extend(self.load_plugin_directory(path))

        return plugins

    def load_and_register_all(self) -> Dict[str, bool]:
        """Load and register all plugins from paths"""
        results = {}
        plugins = self.load_plugins_from_paths()

        for plugin in plugins:
            success = self.registry.register(plugin)
            results[plugin.metadata.name] = success

        return results

    def _extract_plugins_from_module(self, module: ModuleType) -> List[PluginInterface]:
        """Extract plugin instances from a module"""
        plugins = []

        # Look for plugin classes
        for attr_name in dir(module):
            attr = getattr(module, attr_name)

            # Check if it's a plugin class (not the base classes)
            if (
                isinstance(attr, type)
                and issubclass(attr, PluginInterface)
                and attr is not PluginInterface
                and not attr.__name__.endswith("Plugin")
            ):

                try:
                    # Try to instantiate the plugin
                    plugin_instance = attr()
                    plugins.append(plugin_instance)
                except Exception as e:
                    print(f"Error instantiating plugin {attr_name}: {e}")

        # Also look for module-level plugin metadata and functions
        if hasattr(module, "PLUGIN_METADATA"):
            metadata = module.PLUGIN_METADATA
            if isinstance(metadata, dict):
                plugin = self._create_function_plugin(module, metadata)
                if plugin:
                    plugins.append(plugin)

        return plugins

    def _create_function_plugin(
        self, module: ModuleType, metadata_dict: Dict[str, Any]
    ) -> Optional[PluginInterface]:
        """Create a plugin from module-level functions"""
        try:
            # Create metadata
            metadata = PluginMetadata(
                name=metadata_dict.get("name", "Unknown Plugin"),
                version=metadata_dict.get("version", "1.0.0"),
                description=metadata_dict.get("description", "No description"),
                author=metadata_dict.get("author", "Unknown"),
                plugin_type=PluginType(metadata_dict.get("type", "function_library")),
            )

            # Create dynamic plugin class
            class DynamicPlugin(PluginInterface):
                def __init__(self, mod: ModuleType):
                    super().__init__(metadata)
                    self.module = mod

                def initialize(self, context: Dict[str, Any]) -> bool:
                    self.context = context
                    self.is_loaded = True
                    self.is_enabled = True
                    return True

                def cleanup(self) -> bool:
                    self.is_enabled = False
                    self.is_loaded = False
                    return True

                def get_functions(self) -> Dict[str, Any]:
                    """Extract functions marked with plugin decorators"""
                    functions = {}
                    for attr_name in dir(self.module):
                        attr = getattr(self.module, attr_name)
                        if callable(attr) and hasattr(attr, "_plugin_name"):
                            functions[attr._plugin_name] = attr
                    return functions

                def get_constants(self) -> Dict[str, Any]:
                    """Extract constants from module"""
                    constants = {}
                    for attr_name in dir(self.module):
                        attr = getattr(self.module, attr_name)
                        if hasattr(attr, "_plugin_constant_name"):
                            constants[attr._plugin_constant_name] = (
                                attr._plugin_constant_value
                            )
                    return constants

            return DynamicPlugin(module)

        except Exception as e:
            print(f"Error creating function plugin: {e}")
            return None

    def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a plugin"""
        # Find the plugin
        plugin = self.registry.get_plugin(plugin_name)
        if not plugin:
            return False

        # Find the module file
        module_file = None
        for filepath, module in self.loaded_modules.items():
            if hasattr(module, plugin.__class__.__name__):
                module_file = filepath
                break

        if not module_file:
            return False

        try:
            # Unregister old plugin
            self.registry.unregister(plugin_name)

            # Reload module
            spec = importlib.util.spec_from_file_location(
                os.path.splitext(os.path.basename(module_file))[0], module_file
            )
            if spec is None or spec.loader is None:
                return False

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            self.loaded_modules[module_file] = module

            # Load new plugins
            plugins = self._extract_plugins_from_module(module)
            for new_plugin in plugins:
                if new_plugin.metadata.name == plugin_name:
                    return self.registry.register(new_plugin)

            return False

        except Exception as e:
            print(f"Error reloading plugin {plugin_name}: {e}")
            return False

    def create_plugin_template(
        self, filepath: str, plugin_type: PluginType = PluginType.FUNCTION_LIBRARY
    ):
        """Create a plugin template file"""
        template = f'''"""
Example Time_Warp IDE Plugin
Generated plugin template
"""

from typing import Dict, Any, Callable
from james.core.language.plugins.base import (
    PluginInterface, PluginMetadata, PluginType, 
    FunctionLibraryPlugin, plugin_function
)

class ExamplePlugin(FunctionLibraryPlugin):
    """Example plugin implementation"""
    
    def __init__(self):
        metadata = PluginMetadata(
            name="Example Plugin",
            version="1.0.0",
            description="An example plugin for Time_Warp IDE",
            author="Your Name",
            plugin_type=PluginType.{plugin_type.name}
        )
        super().__init__(metadata)
    
    def initialize(self, context: Dict[str, Any]) -> bool:
        """Initialize the plugin"""
        self.context = context
        self.is_loaded = True
        self.is_enabled = True
        return True
    
    def cleanup(self) -> bool:
        """Cleanup plugin resources"""
        self.is_enabled = False
        self.is_loaded = False
        return True
    
    def get_functions(self) -> Dict[str, Callable]:
        """Return plugin functions"""
        
        @plugin_function("HELLO", "Print hello message")
        def hello(name: str = "World") -> str:
            return f"Hello, {{name}}!"
        
        @plugin_function("ADD", "Add two numbers")
        def add(a: float, b: float) -> float:
            return a + b
        
        return {{
            'HELLO': hello,
            'ADD': add
        }}
    
    def get_constants(self) -> Dict[str, Any]:
        """Return plugin constants"""
        return {{
            'PLUGIN_VERSION': '1.0.0',
            'AUTHOR': 'Your Name'
        }}

# Alternative: Module-level plugin definition
# PLUGIN_METADATA = {{
#     'name': 'Simple Plugin',
#     'version': '1.0.0',
#     'description': 'A simple module-based plugin',
#     'author': 'Your Name',
#     'type': 'function_library'
# }}
# 
# @plugin_function("GREET", "Greet someone")
# def greet(name: str) -> str:
#     return f"Greetings, {{name}}!"
'''

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            f.write(template)

    def get_statistics(self) -> Dict[str, Any]:
        """Get loader statistics"""
        return {
            "plugin_paths": len(self.plugin_paths),
            "loaded_modules": len(self.loaded_modules),
            "search_paths": self.plugin_paths,
        }
