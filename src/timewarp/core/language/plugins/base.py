"""
Time_Warp IDE Plugin Base Classes
Foundation for the plugin system
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum
import inspect


class PluginType(Enum):
    """Types of plugins"""

    LANGUAGE_EXTENSION = "language_extension"  # New language features
    FUNCTION_LIBRARY = "function_library"  # New built-in functions
    MODE_HANDLER = "mode_handler"  # New execution modes
    COMPILER_PASS = "compiler_pass"  # Compilation optimization
    RUNTIME_HOOK = "runtime_hook"  # Runtime event handlers
    UI_EXTENSION = "ui_extension"  # User interface extensions
    INTEGRATION = "integration"  # External tool integrations


@dataclass
class PluginMetadata:
    """Plugin metadata"""

    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    dependencies: Optional[List[str]] = None
    james_version_min: str = "3.0.0"
    james_version_max: str = "4.0.0"

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class PluginInterface(ABC):
    """Base interface for all plugins"""

    def __init__(self, metadata: PluginMetadata):
        self.metadata = metadata
        self.is_enabled = False
        self.is_loaded = False
        self.context: Optional[Dict[str, Any]] = None

    @abstractmethod
    def initialize(self, context: Dict[str, Any]) -> bool:
        """Initialize the plugin with runtime context"""
        pass

    @abstractmethod
    def cleanup(self) -> bool:
        """Clean up plugin resources"""
        pass

    def get_info(self) -> Dict[str, Any]:
        """Get plugin information"""
        return {
            "name": self.metadata.name,
            "version": self.metadata.version,
            "description": self.metadata.description,
            "author": self.metadata.author,
            "type": self.metadata.plugin_type.value,
            "dependencies": self.metadata.dependencies,
            "enabled": self.is_enabled,
            "loaded": self.is_loaded,
        }


class LanguageExtensionPlugin(PluginInterface):
    """Plugin for adding new language features"""

    @abstractmethod
    def get_new_keywords(self) -> Dict[str, str]:
        """Return new keywords to add to the lexer"""
        return {}

    @abstractmethod
    def get_syntax_rules(self) -> Dict[str, Callable]:
        """Return new syntax parsing rules"""
        return {}

    def get_ast_nodes(self) -> Dict[str, type]:
        """Return new AST node types"""
        return {}


class FunctionLibraryPlugin(PluginInterface):
    """Plugin for adding new built-in functions"""

    @abstractmethod
    def get_functions(self) -> Dict[str, Callable]:
        """Return functions to add to standard library"""
        return {}

    def get_constants(self) -> Dict[str, Any]:
        """Return constants to add to standard library"""
        return {}


class ModeHandlerPlugin(PluginInterface):
    """Plugin for adding new execution modes"""

    @abstractmethod
    def get_mode_name(self) -> str:
        """Return the name of the execution mode"""
        pass

    @abstractmethod
    def setup_mode(self, context: Dict[str, Any]) -> bool:
        """Setup the execution mode"""
        pass

    @abstractmethod
    def handle_statement(self, statement: Any, context: Dict[str, Any]) -> Any:
        """Handle a statement in this mode"""
        pass


class CompilerPassPlugin(PluginInterface):
    """Plugin for adding compiler optimization passes"""

    @abstractmethod
    def get_pass_name(self) -> str:
        """Return the name of the compiler pass"""
        pass

    @abstractmethod
    def should_run(self, ast: Any, context: Dict[str, Any]) -> bool:
        """Determine if this pass should run"""
        pass

    @abstractmethod
    def transform_ast(self, ast: Any, context: Dict[str, Any]) -> Any:
        """Transform the AST"""
        pass


class RuntimeHookPlugin(PluginInterface):
    """Plugin for runtime event handling"""

    def on_program_start(self, context: Dict[str, Any]):
        """Called when program starts"""
        pass

    def on_program_end(self, context: Dict[str, Any]):
        """Called when program ends"""
        pass

    def on_variable_set(self, name: str, value: Any, context: Dict[str, Any]):
        """Called when a variable is set"""
        pass

    def on_function_call(self, name: str, args: List[Any], context: Dict[str, Any]):
        """Called when a function is called"""
        pass

    def on_error(self, error: Exception, context: Dict[str, Any]):
        """Called when an error occurs"""
        pass


class UIExtensionPlugin(PluginInterface):
    """Plugin for user interface extensions"""

    @abstractmethod
    def get_ui_components(self) -> Dict[str, Any]:
        """Return UI components to add"""
        return {}

    def get_menu_items(self) -> List[Dict[str, Any]]:
        """Return menu items to add"""
        return []

    def get_toolbar_items(self) -> List[Dict[str, Any]]:
        """Return toolbar items to add"""
        return []


class IntegrationPlugin(PluginInterface):
    """Plugin for external tool integrations"""

    @abstractmethod
    def get_integration_name(self) -> str:
        """Return the name of the integration"""
        pass

    @abstractmethod
    def connect(self, config: Dict[str, Any]) -> bool:
        """Connect to external tool"""
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """Disconnect from external tool"""
        pass

    def get_capabilities(self) -> List[str]:
        """Return list of capabilities this integration provides"""
        return []


# Convenience base class
class Plugin(PluginInterface):
    """Simple plugin base class with default implementations"""

    def initialize(self, context: Dict[str, Any]) -> bool:
        """Default initialization"""
        self.context = context
        self.is_loaded = True
        self.is_enabled = True
        return True

    def cleanup(self) -> bool:
        """Default cleanup"""
        self.is_enabled = False
        self.is_loaded = False
        self.context = None
        return True


# Plugin decorators for easier plugin creation
def plugin_function(name: str, description: str = ""):
    """Decorator to mark a function as a plugin function"""

    def decorator(func: Callable) -> Callable:
        # Add metadata to function
        func._plugin_name = name
        func._plugin_description = description
        func._plugin_signature = inspect.signature(func)
        return func

    return decorator


def plugin_constant(name: str, value: Any, description: str = ""):
    """Decorator to mark a value as a plugin constant"""

    def decorator(func: Callable) -> Callable:
        func._plugin_constant_name = name
        func._plugin_constant_value = value
        func._plugin_constant_description = description
        return func

    return decorator


# Example plugin implementations
class MathLibraryPlugin(FunctionLibraryPlugin):
    """Example math library plugin"""

    def __init__(self):
        metadata = PluginMetadata(
            name="Advanced Math Library",
            version="1.0.0",
            description="Additional mathematical functions",
            author="Time_Warp Team",
            plugin_type=PluginType.FUNCTION_LIBRARY,
        )
        super().__init__(metadata)

    def initialize(self, context: Dict[str, Any]) -> bool:
        self.context = context
        self.is_loaded = True
        self.is_enabled = True
        return True

    def cleanup(self) -> bool:
        self.is_enabled = False
        self.is_loaded = False
        return True

    def get_functions(self) -> Dict[str, Callable]:
        """Return advanced math functions"""
        import math

        @plugin_function("FACTORIAL", "Calculate factorial of n")
        def factorial(n: int) -> int:
            if n < 0:
                raise ValueError("Factorial not defined for negative numbers")
            if n <= 1:
                return 1
            result = 1
            for i in range(2, n + 1):
                result *= i
            return result

        @plugin_function("GCD", "Greatest common divisor of two numbers")
        def gcd(a: int, b: int) -> int:
            while b:
                a, b = b, a % b
            return abs(a)

        @plugin_function("LCM", "Least common multiple of two numbers")
        def lcm(a: int, b: int) -> int:
            return abs(a * b) // gcd(a, b)

        @plugin_function("ISPRIME", "Check if number is prime")
        def is_prime(n: int) -> bool:
            if n < 2:
                return False
            if n == 2:
                return True
            if n % 2 == 0:
                return False
            for i in range(3, int(math.sqrt(n)) + 1, 2):
                if n % i == 0:
                    return False
            return True

        return {"FACTORIAL": factorial, "GCD": gcd, "LCM": lcm, "ISPRIME": is_prime}

    def get_constants(self) -> Dict[str, Any]:
        """Return mathematical constants"""
        import math

        return {
            "PHI": (1 + math.sqrt(5)) / 2,  # Golden ratio
            "EULER_GAMMA": 0.5772156649015329,  # Euler-Mascheroni constant
        }


class LoggingPlugin(RuntimeHookPlugin):
    """Example logging plugin"""

    def __init__(self):
        metadata = PluginMetadata(
            name="Runtime Logger",
            version="1.0.0",
            description="Logs runtime events for debugging",
            author="Time_Warp Team",
            plugin_type=PluginType.RUNTIME_HOOK,
        )
        super().__init__(metadata)
        self.log_file = None

    def initialize(self, context: Dict[str, Any]) -> bool:
        self.context = context
        try:
            self.log_file = open("james_runtime.log", "w")
            self.is_loaded = True
            self.is_enabled = True
            return True
        except Exception:
            return False

    def cleanup(self) -> bool:
        if self.log_file:
            self.log_file.close()
            self.log_file = None
        self.is_enabled = False
        self.is_loaded = False
        return True

    def on_program_start(self, context: Dict[str, Any]):
        if self.log_file:
            self.log_file.write("Program started\n")
            self.log_file.flush()

    def on_program_end(self, context: Dict[str, Any]):
        if self.log_file:
            self.log_file.write("Program ended\n")
            self.log_file.flush()

    def on_variable_set(self, name: str, value: Any, context: Dict[str, Any]):
        if self.log_file:
            self.log_file.write(f"Variable set: {name} = {value}\n")
            self.log_file.flush()

    def on_function_call(self, name: str, args: List[Any], context: Dict[str, Any]):
        if self.log_file:
            self.log_file.write(
                f"Function called: {name}({', '.join(map(str, args))})\n"
            )
            self.log_file.flush()

    def on_error(self, error: Exception, context: Dict[str, Any]):
        if self.log_file:
            self.log_file.write(f"Error occurred: {error}\n")
            self.log_file.flush()
