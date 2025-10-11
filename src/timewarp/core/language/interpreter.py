"""
Time_Warp IDE Runtime Engine
Executes Time_Warp IDE programs by interpreting the Abstract Syntax Tree
"""

import sys
import math
import random
import time
import os
from typing import Any, Dict, List, Optional, Callable, Union
from .parser import *
from .lexer import TimeWarpLexer, Token


class TimeWarpError(Exception):
    """Base exception for Time_Warp language errors"""

    pass


class TimeWarpTypeError(TimeWarpError):
    """Type error in Time_Warp code"""

    pass


class TimeWarpNameError(TimeWarpError):
    """Name error in Time_Warp code"""

    pass


class TimeWarpRuntimeError(TimeWarpError):
    """Runtime error in Time_Warp code"""

    pass


class TimeWarpReturnValue(Exception):
    """Used for function returns"""

    def __init__(self, value):
        self.value = value


class TimeWarpBreak(Exception):
    """Used for break statements"""

    pass


class TimeWarpContinue(Exception):
    """Used for continue statements"""

    pass


class Environment:
    """Variable environment with scoping"""

    def __init__(self, parent: Optional["Environment"] = None):
        self.parent = parent
        self.variables: Dict[str, Any] = {}

    def define(self, name: str, value: Any):
        """Define a variable in this environment"""
        self.variables[name] = value

    def get(self, name: str) -> Any:
        """Get a variable from this environment or parent"""
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get(name)
        raise TimeWarpNameError(f"Undefined variable '{name}'")

    def set(self, name: str, value: Any):
        """Set a variable in this environment or parent"""
        if name in self.variables:
            self.variables[name] = value
            return
        if self.parent:
            try:
                self.parent.set(name, value)
                return
            except TimeWarpNameError:
                pass
        # If not found anywhere, create in current scope
        self.variables[name] = value


class TimeWarpFunction:
    """Represents a user-defined function"""

    def __init__(self, declaration: FunctionDefNode, closure: Environment):
        self.declaration = declaration
        self.closure = closure

    def call(self, interpreter: "Time_WarpInterpreter", arguments: List[Any]) -> Any:
        """Call the function with given arguments"""
        if len(arguments) != len(self.declaration.parameters):
            raise TimeWarpRuntimeError(
                f"Expected {len(self.declaration.parameters)} arguments but got {len(arguments)}"
            )

        # Create new environment for function
        environment = Environment(self.closure)

        # Bind parameters
        for i, param in enumerate(self.declaration.parameters):
            environment.define(param, arguments[i])

        previous = interpreter.environment
        try:
            interpreter.environment = environment

            # Execute function body
            for stmt in self.declaration.statements:
                interpreter.execute(stmt)

        except TimeWarpReturnValue as return_val:
            return return_val.value
        finally:
            interpreter.environment = previous

        return None  # No explicit return


class Time_WarpInterpreter:
    """Main interpreter for Time_Warp IDE programs"""

    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        self.output_buffer = []
        self.input_callback: Optional[Callable[[str], str]] = None

        # Initialize built-in functions
        self._init_builtins()

        # Python integration globals
        self.python_globals = {"Time_Warp": self._create_timewarp_interface()}

    def _init_builtins(self):
        """Initialize built-in functions and constants"""
        # Math functions
        self.globals.define("SIN", lambda x: math.sin(x))
        self.globals.define("COS", lambda x: math.cos(x))
        self.globals.define("TAN", lambda x: math.tan(x))
        self.globals.define("SQRT", lambda x: math.sqrt(x))
        self.globals.define("ABS", lambda x: abs(x))
        self.globals.define("INT", lambda x: int(x))
        self.globals.define("RND", lambda: random.random())

        # String functions
        self.globals.define("LEN", lambda s: len(str(s)))
        self.globals.define("LEFT$", lambda s, n: str(s)[: int(n)])
        self.globals.define("RIGHT$", lambda s, n: str(s)[-int(n) :])
        self.globals.define(
            "MID$",
            lambda s, start, length=None: (
                str(s)[int(start) - 1 : int(start) - 1 + int(length)]
                if length
                else str(s)[int(start) - 1 :]
            ),
        )

        # Type conversion
        self.globals.define("STR$", lambda x: str(x))
        self.globals.define("VAL", lambda s: float(s) if "." in str(s) else int(s))

        # System functions
        self.globals.define("TIME$", lambda: time.strftime("%H:%M:%S"))
        self.globals.define("DATE$", lambda: time.strftime("%Y-%m-%d"))

        # Constants
        self.globals.define("PI", math.pi)
        self.globals.define("E", math.e)

    def _create_timewarp_interface(self):
        """Create Time_Warp interface for Python integration"""

        class TimeWarpInterface:
            def __init__(self, interpreter):
                self.interpreter = interpreter

            def GET(self, name: str) -> Any:
                """Get Time_Warp variable from Python"""
                return self.interpreter.environment.get(name)

            def SET(self, name: str, value: Any):
                """Set Time_Warp variable from Python"""
                self.interpreter.environment.set(name, value)

            def CALL(self, name: str, *args) -> Any:
                """Call Time_Warp function from Python"""
                func = self.interpreter.environment.get(name)
                if isinstance(func, TimeWarpFunction):
                    return func.call(self.interpreter, list(args))
                elif callable(func):
                    return func(*args)
                else:
                    raise TimeWarpRuntimeError(f"'{name}' is not callable")

        return TimeWarpInterface(self)

    def interpret(self, program: ProgramNode) -> List[str]:
        """Interpret a Time_Warp program"""
        self.output_buffer = []

        try:
            for statement in program.statements:
                if statement:
                    self.execute(statement)
        except TimeWarpError as e:
            self.output_buffer.append(f"Error: {e}")

        return self.output_buffer

    def execute(self, node: ASTNode) -> Any:
        """Execute an AST node"""
        method_name = f"execute_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_execute)
        return method(node)

    def generic_execute(self, node: ASTNode):
        """Generic execution for unknown node types"""
        raise TimeWarpRuntimeError(f"No execution method for {type(node).__name__}")

    def execute_NumberNode(self, node: NumberNode) -> Union[int, float]:
        """Execute number literal"""
        return node.value

    def execute_StringNode(self, node: StringNode) -> str:
        """Execute string literal"""
        return node.value

    def execute_IdentifierNode(self, node: IdentifierNode) -> Any:
        """Execute identifier (variable access)"""
        return self.environment.get(node.name)

    def execute_BinaryOpNode(self, node: BinaryOpNode) -> Any:
        """Execute binary operation"""
        left = self.execute(node.left)
        right = self.execute(node.right)

        if node.operator == "+":
            return left + right
        elif node.operator == "-":
            return left - right
        elif node.operator == "*":
            return left * right
        elif node.operator == "/":
            if right == 0:
                raise TimeWarpRuntimeError("Division by zero")
            return left / right
        elif node.operator == "^":
            return left**right
        elif node.operator == "=":
            return left == right
        elif node.operator == "<>":
            return left != right
        elif node.operator == "<":
            return left < right
        elif node.operator == ">":
            return left > right
        elif node.operator == "<=":
            return left <= right
        elif node.operator == ">=":
            return left >= right
        elif node.operator.upper() == "AND":
            return self._is_truthy(left) and self._is_truthy(right)
        elif node.operator.upper() == "OR":
            return self._is_truthy(left) or self._is_truthy(right)
        else:
            raise TimeWarpRuntimeError(f"Unknown binary operator: {node.operator}")

    def execute_UnaryOpNode(self, node: UnaryOpNode) -> Any:
        """Execute unary operation"""
        operand = self.execute(node.operand)

        if node.operator == "-":
            return -operand
        elif node.operator.upper() == "NOT":
            return not self._is_truthy(operand)
        else:
            raise TimeWarpRuntimeError(f"Unknown unary operator: {node.operator}")

    def execute_AssignmentNode(self, node: AssignmentNode):
        """Execute assignment"""
        value = self.execute(node.value)
        self.environment.set(node.variable, value)
        return value

    def execute_PrintNode(self, node: PrintNode):
        """Execute PRINT statement"""
        output = []
        for expr in node.expressions:
            value = self.execute(expr)
            output.append(str(value))

        result = " ".join(output) if output else ""
        self.output_buffer.append(result)
        return result

    def execute_InputNode(self, node: InputNode):
        """Execute INPUT statement"""
        if node.prompt:
            self.output_buffer.append(node.prompt)

        if self.input_callback:
            value = self.input_callback(node.prompt or "")
        else:
            value = input(node.prompt or "")

        # Try to convert to number if possible
        try:
            if "." in value:
                value = float(value)
            else:
                value = int(value)
        except ValueError:
            pass  # Keep as string

        self.environment.set(node.variable, value)
        return value

    def execute_IfNode(self, node: IfNode):
        """Execute IF statement"""
        condition = self.execute(node.condition)

        if self._is_truthy(condition):
            for stmt in node.then_statements:
                self.execute(stmt)
        else:
            # Check ELIF conditions
            for elif_condition, elif_statements in node.elif_conditions:
                if self._is_truthy(self.execute(elif_condition)):
                    for stmt in elif_statements:
                        self.execute(stmt)
                    return

            # Execute ELSE block if no ELIF matched
            if node.else_statements:
                for stmt in node.else_statements:
                    self.execute(stmt)

    def execute_ForNode(self, node: ForNode):
        """Execute FOR loop"""
        start = self.execute(node.start)
        end = self.execute(node.end)
        step = self.execute(node.step) if node.step else 1

        current = start
        while (step > 0 and current <= end) or (step < 0 and current >= end):
            self.environment.set(node.variable, current)

            try:
                for stmt in node.statements:
                    self.execute(stmt)
            except TimeWarpBreak:
                break
            except TimeWarpContinue:
                pass

            current += step

    def execute_WhileNode(self, node: WhileNode):
        """Execute WHILE loop"""
        while self._is_truthy(self.execute(node.condition)):
            try:
                for stmt in node.statements:
                    self.execute(stmt)
            except TimeWarpBreak:
                break
            except TimeWarpContinue:
                continue

    def execute_FunctionDefNode(self, node: FunctionDefNode):
        """Execute function definition"""
        function = TimeWarpFunction(node, self.environment)
        self.environment.define(node.name, function)
        return function

    def execute_FunctionCallNode(self, node: FunctionCallNode) -> Any:
        """Execute function call"""
        function = self.environment.get(node.name)
        arguments = [self.execute(arg) for arg in node.arguments]

        if isinstance(function, TimeWarpFunction):
            return function.call(self, arguments)
        elif callable(function):
            return function(*arguments)
        else:
            raise TimeWarpRuntimeError(f"'{node.name}' is not callable")

    def execute_ReturnNode(self, node: ReturnNode):
        """Execute RETURN statement"""
        value = None
        if node.value:
            value = self.execute(node.value)
        raise TimeWarpReturnValue(value)

    def execute_PythonBlockNode(self, node: PythonBlockNode):
        """Execute Python code block"""
        try:
            # Create execution environment
            local_vars = {}
            global_vars = dict(self.python_globals)

            # Execute Python code
            exec(node.code, global_vars, local_vars)

            return local_vars
        except Exception as e:
            raise TimeWarpRuntimeError(f"Python execution error: {e}")

    def execute_ModeNode(self, node: ModeNode):
        """Execute mode switching"""
        # For now, just execute the statements
        # Mode-specific behavior will be handled by specialized handlers
        for stmt in node.statements:
            self.execute(stmt)

    def execute_PilotCommandNode(self, node: PilotCommandNode):
        """Execute PILOT command (placeholder)"""
        # This will be implemented by the PILOT handler
        self.output_buffer.append(f"PILOT: {node.command} {node.argument}")

    def execute_LogoCommandNode(self, node: LogoCommandNode):
        """Execute Logo command (placeholder)"""
        # This will be implemented by the Logo handler
        args = [self.execute(arg) for arg in node.arguments]
        self.output_buffer.append(f"LOGO: {node.command} {args}")

    def execute_TryNode(self, node: TryNode):
        """Execute TRY/CATCH/FINALLY block"""
        try:
            for stmt in node.try_statements:
                self.execute(stmt)
        except Exception as e:
            # Handle CATCH clauses
            for exception_type, catch_statements in node.catch_clauses:
                if not exception_type or exception_type == type(e).__name__:
                    for stmt in catch_statements:
                        self.execute(stmt)
                    break
            else:
                # No matching catch clause, re-raise
                raise
        finally:
            if node.finally_statements:
                for stmt in node.finally_statements:
                    self.execute(stmt)

    def _is_truthy(self, value: Any) -> bool:
        """Determine if a value is truthy in Time_Warp"""
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return len(value) > 0
        return True

    def set_input_callback(self, callback: Callable[[str], str]):
        """Set callback for input operations"""
        self.input_callback = callback
