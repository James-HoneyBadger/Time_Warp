"""
Time_Warp IDE Code Optimizer
AST optimization for better performance
"""

from typing import List, Dict, Any, Optional
from .parser import ASTNode, ASTNodeType, LiteralNode, BinaryOpNode, UnaryOpNode


class CodeOptimizer:
    """Optimizes AST for better performance"""

    def __init__(self):
        self.optimizations_applied = 0

    def optimize(self, ast: ASTNode) -> ASTNode:
        """Apply optimizations to AST"""
        self.optimizations_applied = 0
        return self._optimize_node(ast)

    def _optimize_node(self, node: ASTNode) -> ASTNode:
        """Optimize a single node"""
        if node is None:
            return node

        # First optimize children
        for i, child in enumerate(node.children):
            node.children[i] = self._optimize_node(child)

        # Apply node-specific optimizations
        if node.node_type == ASTNodeType.BINARY_OP:
            return self._optimize_binary_op(node)
        elif node.node_type == ASTNodeType.UNARY_OP:
            return self._optimize_unary_op(node)

        return node

    def _optimize_binary_op(self, node: ASTNode) -> ASTNode:
        """Optimize binary operations"""
        if not isinstance(node, BinaryOpNode):
            return node

        left = node.left
        right = node.right

        # Constant folding
        if (
            isinstance(left, LiteralNode)
            and isinstance(right, LiteralNode)
            and isinstance(left.value, (int, float))
            and isinstance(right.value, (int, float))
        ):

            try:
                if node.operator == "+":
                    result = left.value + right.value
                elif node.operator == "-":
                    result = left.value - right.value
                elif node.operator == "*":
                    result = left.value * right.value
                elif node.operator == "/":
                    if right.value != 0:
                        result = left.value / right.value
                    else:
                        return node  # Don't optimize division by zero
                elif node.operator == "%":
                    if right.value != 0:
                        result = left.value % right.value
                    else:
                        return node
                elif node.operator == "^" or node.operator == "**":
                    result = left.value**right.value
                else:
                    return node

                self.optimizations_applied += 1
                return LiteralNode(result, node.location)

            except (ZeroDivisionError, OverflowError, ValueError):
                # Keep original if calculation fails
                return node

        # Algebraic optimizations
        if isinstance(right, LiteralNode):
            # x + 0 = x, x - 0 = x
            if node.operator in ["+", "-"] and right.value == 0:
                self.optimizations_applied += 1
                return left

            # x * 1 = x, x / 1 = x
            if node.operator in ["*", "/"] and right.value == 1:
                self.optimizations_applied += 1
                return left

            # x * 0 = 0
            if node.operator == "*" and right.value == 0:
                self.optimizations_applied += 1
                return LiteralNode(0, node.location)

        if isinstance(left, LiteralNode):
            # 0 + x = x
            if node.operator == "+" and left.value == 0:
                self.optimizations_applied += 1
                return right

            # 1 * x = x
            if node.operator == "*" and left.value == 1:
                self.optimizations_applied += 1
                return right

            # 0 * x = 0
            if node.operator == "*" and left.value == 0:
                self.optimizations_applied += 1
                return LiteralNode(0, node.location)

        return node

    def _optimize_unary_op(self, node: ASTNode) -> ASTNode:
        """Optimize unary operations"""
        if not isinstance(node, UnaryOpNode):
            return node

        operand = node.operand

        # Constant folding
        if isinstance(operand, LiteralNode):
            try:
                if node.operator == "-":
                    if isinstance(operand.value, (int, float)):
                        result = -operand.value
                        self.optimizations_applied += 1
                        return LiteralNode(result, node.location)
                elif node.operator == "+":
                    if isinstance(operand.value, (int, float)):
                        self.optimizations_applied += 1
                        return operand  # +x = x
                elif node.operator.upper() == "NOT":
                    if isinstance(operand.value, bool):
                        result = not operand.value
                        self.optimizations_applied += 1
                        return LiteralNode(result, node.location)
            except (ValueError, TypeError):
                pass

        return node

    def get_stats(self) -> Dict[str, Any]:
        """Get optimization statistics"""
        return {"optimizations_applied": self.optimizations_applied}
