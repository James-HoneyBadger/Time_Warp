"""
Time_Warp IDE Code Generator
Generates executable code from AST
"""

from typing import List, Dict, Any, Optional, Callable
from .parser import (
    ASTNode,
    ASTNodeType,
    LiteralNode,
    IdentifierNode,
    BinaryOpNode,
    UnaryOpNode,
    FunctionCallNode,
    AssignmentNode,
    ProgramNode,
)
from ..runtime.engine import RuntimeEngine, ExecutionContext
from ..errors.error_manager import (
    TimeWarpError,
    TimeWarpRuntimeError,
    ErrorCode,
    ErrorSeverity,
)


class CodeGenerator:
    """Generates executable code from AST"""

    def __init__(self, runtime: Optional[RuntimeEngine] = None):
        self.runtime = runtime or RuntimeEngine()
        self.generated_code = []

    def generate(self, ast: ASTNode) -> Callable[[ExecutionContext], Any]:
        """Generate executable code from AST"""
        self.generated_code = []

        # Generate code that can be executed by the runtime
        def execute_ast(context: ExecutionContext) -> Any:
            return self._execute_node(ast, context)

        return execute_ast

    def _execute_node(self, node: ASTNode, context: ExecutionContext) -> Any:
        """Execute an AST node"""
        if node is None:
            return None

        if node.node_type == ASTNodeType.PROGRAM:
            return self._execute_program(node, context)
        elif node.node_type == ASTNodeType.NUMBER:
            return self._execute_literal(node, context)
        elif node.node_type == ASTNodeType.STRING:
            return self._execute_literal(node, context)
        elif node.node_type == ASTNodeType.BOOLEAN:
            return self._execute_literal(node, context)
        elif node.node_type == ASTNodeType.IDENTIFIER:
            return self._execute_identifier(node, context)
        elif node.node_type == ASTNodeType.BINARY_OP:
            return self._execute_binary_op(node, context)
        elif node.node_type == ASTNodeType.UNARY_OP:
            return self._execute_unary_op(node, context)
        elif node.node_type == ASTNodeType.FUNCTION_CALL:
            return self._execute_function_call(node, context)
        elif node.node_type == ASTNodeType.ASSIGNMENT:
            return self._execute_assignment(node, context)
        else:
            raise TimeWarpRuntimeError(
                TimeWarpError(
                    code=ErrorCode.PYTHON_EXECUTION_ERROR,
                    severity=ErrorSeverity.ERROR,
                    message=f"Unknown AST node type: {node.node_type}",
                    location=node.location,
                )
            )

    def _execute_program(self, node: ASTNode, context: ExecutionContext) -> Any:
        """Execute program node"""
        if not isinstance(node, ProgramNode):
            return None

        result = None
        for stmt in node.statements:
            result = self._execute_node(stmt, context)
            context.instructions_executed += 1

            # Check execution limits
            if not context.check_execution_limits():
                break

        return result

    def _execute_literal(self, node: ASTNode, context: ExecutionContext) -> Any:
        """Execute literal node"""
        if isinstance(node, LiteralNode):
            return node.value
        return None

    def _execute_identifier(self, node: ASTNode, context: ExecutionContext) -> Any:
        """Execute identifier node"""
        if isinstance(node, IdentifierNode):
            # Check constants first
            try:
                return context.stdlib.get_constant(node.name)
            except:
                pass

            # Then check variables
            try:
                return context.variables.get_variable(node.name)
            except TimeWarpRuntimeError:
                # Variable not found
                raise TimeWarpRuntimeError(
                    TimeWarpError(
                        code=ErrorCode.UNDEFINED_VARIABLE,
                        severity=ErrorSeverity.ERROR,
                        message=f"Undefined variable or constant: '{node.name}'",
                        location=node.location,
                        suggestions=[
                            "Define the variable before using it",
                            "Check for typos in the name",
                            f"Available constants: {', '.join(list(context.stdlib.constants.keys())[:5])}",
                        ],
                    )
                )
        return None

    def _execute_binary_op(self, node: ASTNode, context: ExecutionContext) -> Any:
        """Execute binary operation node"""
        if not isinstance(node, BinaryOpNode):
            return None

        left_val = self._execute_node(node.left, context)
        right_val = self._execute_node(node.right, context)

        try:
            if node.operator == "+":
                return left_val + right_val
            elif node.operator == "-":
                return left_val - right_val
            elif node.operator == "*":
                return left_val * right_val
            elif node.operator == "/":
                if right_val == 0:
                    raise TimeWarpRuntimeError(
                        TimeWarpError(
                            code=ErrorCode.DIVISION_BY_ZERO,
                            severity=ErrorSeverity.ERROR,
                            message="Division by zero",
                            location=node.location,
                        )
                    )
                return left_val / right_val
            elif node.operator == "%":
                if right_val == 0:
                    raise TimeWarpRuntimeError(
                        TimeWarpError(
                            code=ErrorCode.DIVISION_BY_ZERO,
                            severity=ErrorSeverity.ERROR,
                            message="Modulo by zero",
                            location=node.location,
                        )
                    )
                return left_val % right_val
            elif node.operator in ["^", "**"]:
                return left_val**right_val
            elif node.operator in ["==", "="]:
                return left_val == right_val
            elif node.operator in ["!=", "<>"]:
                return left_val != right_val
            elif node.operator == "<":
                return left_val < right_val
            elif node.operator == ">":
                return left_val > right_val
            elif node.operator == "<=":
                return left_val <= right_val
            elif node.operator == ">=":
                return left_val >= right_val
            elif node.operator.upper() == "AND":
                return bool(left_val) and bool(right_val)
            elif node.operator.upper() == "OR":
                return bool(left_val) or bool(right_val)
            else:
                raise TimeWarpRuntimeError(
                    TimeWarpError(
                        code=ErrorCode.PYTHON_EXECUTION_ERROR,
                        severity=ErrorSeverity.ERROR,
                        message=f"Unknown binary operator: {node.operator}",
                        location=node.location,
                    )
                )
        except (TypeError, ValueError) as e:
            raise TimeWarpRuntimeError(
                TimeWarpError(
                    code=ErrorCode.TYPE_MISMATCH,
                    severity=ErrorSeverity.ERROR,
                    message=f"Type error in binary operation: {e}",
                    location=node.location,
                    suggestions=[
                        "Check operand types",
                        "Ensure numeric operations use numbers",
                        "Use appropriate type conversion functions",
                    ],
                )
            )

    def _execute_unary_op(self, node: ASTNode, context: ExecutionContext) -> Any:
        """Execute unary operation node"""
        if not isinstance(node, UnaryOpNode):
            return None

        operand_val = self._execute_node(node.operand, context)

        try:
            if node.operator == "-":
                return -operand_val
            elif node.operator == "+":
                return +operand_val
            elif node.operator.upper() == "NOT":
                return not bool(operand_val)
            else:
                raise TimeWarpRuntimeError(
                    TimeWarpError(
                        code=ErrorCode.PYTHON_EXECUTION_ERROR,
                        severity=ErrorSeverity.ERROR,
                        message=f"Unknown unary operator: {node.operator}",
                        location=node.location,
                    )
                )
        except (TypeError, ValueError) as e:
            raise TimeWarpRuntimeError(
                TimeWarpError(
                    code=ErrorCode.TYPE_MISMATCH,
                    severity=ErrorSeverity.ERROR,
                    message=f"Type error in unary operation: {e}",
                    location=node.location,
                )
            )

    def _execute_function_call(self, node: ASTNode, context: ExecutionContext) -> Any:
        """Execute function call node"""
        if not isinstance(node, FunctionCallNode):
            return None

        # Evaluate arguments
        args = []
        for arg_node in node.arguments:
            arg_val = self._execute_node(arg_node, context)
            args.append(arg_val)

        # Get function
        func = context.stdlib.get_function(node.name)
        if func is None:
            raise TimeWarpRuntimeError(
                TimeWarpError(
                    code=ErrorCode.FUNCTION_NOT_FOUND,
                    severity=ErrorSeverity.ERROR,
                    message=f"Unknown function: '{node.name}'",
                    location=node.location,
                    suggestions=[
                        "Check function name spelling",
                        "Import required library",
                        f"Available functions: {', '.join(list(context.stdlib.functions.keys())[:10])}",
                    ],
                )
            )

        # Call function
        try:
            return func(*args)
        except Exception as e:
            if isinstance(e, TimeWarpRuntimeError):
                raise

            raise TimeWarpRuntimeError(
                TimeWarpError(
                    code=ErrorCode.FUNCTION_NOT_FOUND,
                    severity=ErrorSeverity.ERROR,
                    message=f"Error calling function '{node.name}': {e}",
                    location=node.location,
                )
            )

    def _execute_assignment(self, node: ASTNode, context: ExecutionContext) -> Any:
        """Execute assignment node"""
        if not isinstance(node, AssignmentNode):
            return None

        value = self._execute_node(node.value, context)
        context.variables.set_variable(
            node.target,
            value,
            line_defined=node.location.line if node.location else None,
        )
        return value

    def compile_to_bytecode(self, ast: ASTNode) -> List[Dict[str, Any]]:
        """Compile AST to bytecode-like instructions (for future optimization)"""
        instructions = []
        self._compile_node(ast, instructions)
        return instructions

    def _compile_node(self, node: ASTNode, instructions: List[Dict[str, Any]]):
        """Compile node to instructions"""
        if node is None:
            return

        if node.node_type == ASTNodeType.NUMBER:
            if isinstance(node, LiteralNode):
                instructions.append(
                    {"op": "LOAD_CONST", "value": node.value, "location": node.location}
                )
        elif node.node_type == ASTNodeType.STRING:
            if isinstance(node, LiteralNode):
                instructions.append(
                    {"op": "LOAD_CONST", "value": node.value, "location": node.location}
                )
        elif node.node_type == ASTNodeType.IDENTIFIER:
            if isinstance(node, IdentifierNode):
                instructions.append(
                    {"op": "LOAD_VAR", "name": node.name, "location": node.location}
                )
        elif node.node_type == ASTNodeType.BINARY_OP:
            if isinstance(node, BinaryOpNode):
                self._compile_node(node.left, instructions)
                self._compile_node(node.right, instructions)
                instructions.append(
                    {
                        "op": "BINARY_OP",
                        "operator": node.operator,
                        "location": node.location,
                    }
                )
        elif node.node_type == ASTNodeType.ASSIGNMENT:
            if isinstance(node, AssignmentNode):
                self._compile_node(node.value, instructions)
                instructions.append(
                    {"op": "STORE_VAR", "name": node.target, "location": node.location}
                )
        # Add more node types as needed
