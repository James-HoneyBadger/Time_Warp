"""
Time_Warp IDE Runtime Engine
Core execution environment and context management
"""

from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum
import threading
import time

from ..errors.error_manager import (
    ErrorManager,
    TimeWarpError,
    TimeWarpRuntimeError,
    ErrorCode,
    ErrorSeverity,
    SourceLocation,
)
from ..stdlib.core import StandardLibrary


class ExecutionMode(Enum):
    """Execution modes for Time_Warp IDE"""

    BASIC = "basic"
    PILOT = "pilot"
    LOGO = "logo"
    PYTHON = "python"
    HYBRID = "hybrid"


@dataclass
class Variable:
    """Runtime variable representation"""

    name: str
    value: Any
    type_hint: Optional[str] = None
    is_constant: bool = False
    scope: str = "global"
    line_defined: Optional[int] = None

    def __post_init__(self):
        if self.type_hint is None:
            self.type_hint = type(self.value).__name__


class VariableManager:
    """Manages variables and scoping"""

    def __init__(self):
        self.scopes: Dict[str, Dict[str, Variable]] = {"global": {}}
        self.scope_stack: List[str] = ["global"]
        self.current_scope = "global"

    def enter_scope(self, scope_name: str):
        """Enter a new scope"""
        if scope_name not in self.scopes:
            self.scopes[scope_name] = {}
        self.scope_stack.append(scope_name)
        self.current_scope = scope_name

    def exit_scope(self):
        """Exit current scope"""
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()
            self.current_scope = self.scope_stack[-1]

    def set_variable(
        self,
        name: str,
        value: Any,
        type_hint: Optional[str] = None,
        is_constant: bool = False,
        line_defined: Optional[int] = None,
    ):
        """Set a variable in current scope"""
        # Check if trying to modify a constant
        existing = self.get_variable_info(name)
        if existing and existing.is_constant:
            raise TimeWarpRuntimeError(
                TimeWarpError(
                    code=ErrorCode.UNDEFINED_VARIABLE,
                    severity=ErrorSeverity.ERROR,
                    message=f"Cannot modify constant '{name}'",
                    location=(
                        SourceLocation(line_defined or 0, 0) if line_defined else None
                    ),
                )
            )

        var = Variable(
            name=name,
            value=value,
            type_hint=type_hint,
            is_constant=is_constant,
            scope=self.current_scope,
            line_defined=line_defined,
        )
        self.scopes[self.current_scope][name] = var

    def get_variable(self, name: str) -> Any:
        """Get variable value with scope resolution"""
        var_info = self.get_variable_info(name)
        if var_info is None:
            raise TimeWarpRuntimeError(
                TimeWarpError(
                    code=ErrorCode.UNDEFINED_VARIABLE,
                    severity=ErrorSeverity.ERROR,
                    message=f"Undefined variable '{name}'",
                    suggestions=[
                        f"Define the variable before using it",
                        f"Check for typos in the variable name",
                    ],
                )
            )
        return var_info.value

    def get_variable_info(self, name: str) -> Optional[Variable]:
        """Get variable info with scope resolution"""
        # Search from current scope up to global
        for scope in reversed(self.scope_stack):
            if name in self.scopes[scope]:
                return self.scopes[scope][name]
        return None

    def has_variable(self, name: str) -> bool:
        """Check if variable exists in any accessible scope"""
        return self.get_variable_info(name) is not None

    def list_variables(self, scope: Optional[str] = None) -> Dict[str, Variable]:
        """List variables in specified scope or current scope"""
        target_scope = scope or self.current_scope
        return self.scopes.get(target_scope, {}).copy()

    def clear_scope(self, scope: str):
        """Clear all variables in a scope"""
        if scope in self.scopes:
            self.scopes[scope].clear()


@dataclass
class ExecutionContext:
    """Runtime execution context"""

    mode: ExecutionMode = ExecutionMode.BASIC
    variables: VariableManager = field(default_factory=VariableManager)
    stdlib: StandardLibrary = field(default_factory=StandardLibrary)
    error_manager: ErrorManager = field(default_factory=ErrorManager)

    # Execution state
    program_counter: int = 0
    call_stack: List[Dict[str, Any]] = field(default_factory=list)
    is_running: bool = False
    should_stop: bool = False

    # Performance tracking
    start_time: Optional[float] = None
    instructions_executed: int = 0
    max_instructions: int = 1000000  # Prevent infinite loops

    # Mode-specific state
    turtle_position: tuple = (0, 0)  # For LOGO mode
    turtle_angle: float = 0
    pilot_patterns: Dict[str, Any] = field(default_factory=dict)  # For PILOT mode
    python_globals: Dict[str, Any] = field(default_factory=dict)  # For Python mode

    def reset(self):
        """Reset execution state"""
        self.program_counter = 0
        self.call_stack.clear()
        self.is_running = False
        self.should_stop = False
        self.start_time = None
        self.instructions_executed = 0
        self.error_manager.clear()

    def check_execution_limits(self):
        """Check if execution should be stopped"""
        if self.should_stop:
            return False

        if self.instructions_executed >= self.max_instructions:
            self.error_manager.add_error(
                ErrorCode.OUT_OF_MEMORY,
                "Maximum instruction limit reached - possible infinite loop",
            )
            return False

        return True


class ModeHandler:
    """Handles mode-specific execution logic"""

    def __init__(self, context: ExecutionContext):
        self.context = context

    def switch_mode(self, new_mode: ExecutionMode):
        """Switch execution mode"""
        old_mode = self.context.mode
        self.context.mode = new_mode

        # Mode-specific setup
        if new_mode == ExecutionMode.LOGO:
            self._setup_logo_mode()
        elif new_mode == ExecutionMode.PILOT:
            self._setup_pilot_mode()
        elif new_mode == ExecutionMode.PYTHON:
            self._setup_python_mode()

    def _setup_logo_mode(self):
        """Setup LOGO graphics mode"""
        self.context.turtle_position = (0, 0)
        self.context.turtle_angle = 0
        # Register LOGO-specific functions
        self.context.stdlib.register_function("FORWARD", self._logo_forward)
        self.context.stdlib.register_function("BACK", self._logo_back)
        self.context.stdlib.register_function("LEFT", self._logo_left)
        self.context.stdlib.register_function("RIGHT", self._logo_right)
        self.context.stdlib.register_function("PENUP", self._logo_penup)
        self.context.stdlib.register_function("PENDOWN", self._logo_pendown)

    def _setup_pilot_mode(self):
        """Setup PILOT pattern matching mode"""
        self.context.pilot_patterns.clear()
        # Register PILOT-specific functions
        self.context.stdlib.register_function("MATCH", self._pilot_match)
        self.context.stdlib.register_function("ACCEPT", self._pilot_accept)
        self.context.stdlib.register_function("JUMP", self._pilot_jump)

    def _setup_python_mode(self):
        """Setup Python execution mode"""
        import builtins

        self.context.python_globals = {"__builtins__": builtins, "__name__": "__main__"}

    # LOGO mode functions
    def _logo_forward(self, distance: float):
        """Move turtle forward"""
        import math

        distance = float(distance)
        angle_rad = math.radians(self.context.turtle_angle)
        dx = distance * math.cos(angle_rad)
        dy = distance * math.sin(angle_rad)

        x, y = self.context.turtle_position
        self.context.turtle_position = (x + dx, y + dy)
        return self.context.turtle_position

    def _logo_back(self, distance: float):
        """Move turtle backward"""
        return self._logo_forward(-float(distance))

    def _logo_left(self, angle: float):
        """Turn turtle left"""
        self.context.turtle_angle = (self.context.turtle_angle - float(angle)) % 360
        return self.context.turtle_angle

    def _logo_right(self, angle: float):
        """Turn turtle right"""
        self.context.turtle_angle = (self.context.turtle_angle + float(angle)) % 360
        return self.context.turtle_angle

    def _logo_penup(self):
        """Pen up - move without drawing"""
        # This would integrate with graphics system
        return "PEN_UP"

    def _logo_pendown(self):
        """Pen down - draw while moving"""
        # This would integrate with graphics system
        return "PEN_DOWN"

    # PILOT mode functions
    def _pilot_match(self, pattern: str, text: str):
        """Pattern matching function"""
        # Simplified pattern matching - would be more sophisticated
        import re

        try:
            return bool(re.search(str(pattern), str(text)))
        except re.error as e:
            raise TimeWarpRuntimeError(
                TimeWarpError(
                    code=ErrorCode.PILOT_PATTERN_ERROR,
                    severity=ErrorSeverity.ERROR,
                    message=f"Invalid pattern: {e}",
                )
            )

    def _pilot_accept(self):
        """Accept current match"""
        return True

    def _pilot_jump(self, label: str):
        """Jump to label"""
        # This would integrate with control flow
        return f"JUMP_TO_{label}"


class RuntimeEngine:
    """Main runtime execution engine"""

    def __init__(self):
        self.context = ExecutionContext()
        self.mode_handler = ModeHandler(self.context)
        self._lock = threading.Lock()

    def execute(self, program: Any) -> Any:
        """Execute a program"""
        with self._lock:
            try:
                self.context.reset()
                self.context.is_running = True
                self.context.start_time = time.time()

                result = self._execute_program(program)

                return result

            except Exception as e:
                if not isinstance(e, (TimeWarpRuntimeError,)):
                    # Wrap unexpected errors
                    error = TimeWarpError(
                        code=ErrorCode.PYTHON_EXECUTION_ERROR,
                        severity=ErrorSeverity.ERROR,
                        message=f"Unexpected error: {e}",
                    )
                    raise TimeWarpRuntimeError(error) from e
                raise
            finally:
                self.context.is_running = False

    def _execute_program(self, program: Any) -> Any:
        """Execute the actual program logic"""
        # This would contain the main execution loop
        # For now, just a placeholder that works with the AST
        if hasattr(program, "accept"):
            # AST node with visitor pattern
            return program.accept(self)
        elif callable(program):
            # Callable program
            return program(self.context)
        else:
            # Simple value
            return program

    def stop_execution(self):
        """Stop program execution"""
        self.context.should_stop = True

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        elapsed = 0
        if self.context.start_time:
            elapsed = time.time() - self.context.start_time

        return {
            "instructions_executed": self.context.instructions_executed,
            "elapsed_time": elapsed,
            "mode": self.context.mode.value,
            "variables_count": sum(
                len(scope) for scope in self.context.variables.scopes.values()
            ),
            "errors_count": len(self.context.error_manager.errors),
            "warnings_count": len(self.context.error_manager.warnings),
        }

    def set_mode(self, mode: Union[ExecutionMode, str]):
        """Set execution mode"""
        if isinstance(mode, str):
            mode = ExecutionMode(mode.lower())
        self.mode_handler.switch_mode(mode)

    def get_variable(self, name: str) -> Any:
        """Get variable value"""
        return self.context.variables.get_variable(name)

    def set_variable(self, name: str, value: Any, **kwargs):
        """Set variable value"""
        self.context.variables.set_variable(name, value, **kwargs)

    def call_function(self, name: str, *args, **kwargs) -> Any:
        """Call a built-in function"""
        func = self.context.stdlib.get_function(name)
        if func is None:
            raise TimeWarpRuntimeError(
                TimeWarpError(
                    code=ErrorCode.FUNCTION_NOT_FOUND,
                    severity=ErrorSeverity.ERROR,
                    message=f"Unknown function '{name}'",
                    suggestions=[
                        "Check the function name spelling",
                        "Import the required library",
                        f"Available functions: {', '.join(list(self.context.stdlib.functions.keys())[:10])}",
                    ],
                )
            )

        try:
            return func(*args, **kwargs)
        except Exception as e:
            if isinstance(e, TimeWarpRuntimeError):
                raise

            error = TimeWarpError(
                code=ErrorCode.FUNCTION_NOT_FOUND,
                severity=ErrorSeverity.ERROR,
                message=f"Error calling function '{name}': {e}",
            )
            raise TimeWarpRuntimeError(error) from e
