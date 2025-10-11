"""
Time_Warp IDE Enhanced Parser
Improved AST generation with better error handling
"""

from typing import List, Optional, Dict, Any, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from .lexer import Token, TokenType, EnhancedLexer
from ..errors.error_manager import (
    ErrorManager,
    TimeWarpError,
    TimeWarpSyntaxError,
    ErrorCode,
    ErrorSeverity,
    SourceLocation,
)


# AST Node Types
class ASTNodeType(Enum):
    """AST node types"""

    # Literals
    NUMBER = "number"
    STRING = "string"
    BOOLEAN = "boolean"
    IDENTIFIER = "identifier"

    # Expressions
    BINARY_OP = "binary_op"
    UNARY_OP = "unary_op"
    FUNCTION_CALL = "function_call"

    # Statements
    ASSIGNMENT = "assignment"
    IF_STATEMENT = "if_statement"
    WHILE_LOOP = "while_loop"
    FOR_LOOP = "for_loop"
    FUNCTION_DEF = "function_def"
    RETURN_STATEMENT = "return_statement"

    # Special
    PROGRAM = "program"
    BLOCK = "block"


class ASTNode(ABC):
    """Base AST node"""

    def __init__(
        self, node_type: ASTNodeType, location: Optional[SourceLocation] = None
    ):
        self.node_type = node_type
        self.location = location
        self.children: List["ASTNode"] = []

    @abstractmethod
    def accept(self, visitor):
        """Accept visitor pattern"""
        pass

    def add_child(self, child: "ASTNode"):
        """Add child node"""
        self.children.append(child)


@dataclass
class LiteralNode(ASTNode):
    """Literal value node"""

    value: Any

    def __init__(self, value: Any, location: Optional[SourceLocation] = None):
        if isinstance(value, (int, float)):
            super().__init__(ASTNodeType.NUMBER, location)
        elif isinstance(value, str):
            super().__init__(ASTNodeType.STRING, location)
        elif isinstance(value, bool):
            super().__init__(ASTNodeType.BOOLEAN, location)
        else:
            super().__init__(ASTNodeType.STRING, location)
        self.value = value

    def accept(self, visitor):
        return visitor.visit_literal(self)


@dataclass
class IdentifierNode(ASTNode):
    """Identifier node"""

    name: str

    def __init__(self, name: str, location: Optional[SourceLocation] = None):
        super().__init__(ASTNodeType.IDENTIFIER, location)
        self.name = name

    def accept(self, visitor):
        return visitor.visit_identifier(self)


@dataclass
class BinaryOpNode(ASTNode):
    """Binary operation node"""

    operator: str
    left: ASTNode
    right: ASTNode

    def __init__(
        self,
        operator: str,
        left: ASTNode,
        right: ASTNode,
        location: Optional[SourceLocation] = None,
    ):
        super().__init__(ASTNodeType.BINARY_OP, location)
        self.operator = operator
        self.left = left
        self.right = right
        self.add_child(left)
        self.add_child(right)

    def accept(self, visitor):
        return visitor.visit_binary_op(self)


@dataclass
class UnaryOpNode(ASTNode):
    """Unary operation node"""

    operator: str
    operand: ASTNode

    def __init__(
        self, operator: str, operand: ASTNode, location: Optional[SourceLocation] = None
    ):
        super().__init__(ASTNodeType.UNARY_OP, location)
        self.operator = operator
        self.operand = operand
        self.add_child(operand)

    def accept(self, visitor):
        return visitor.visit_unary_op(self)


@dataclass
class FunctionCallNode(ASTNode):
    """Function call node"""

    name: str
    arguments: List[ASTNode]

    def __init__(
        self,
        name: str,
        arguments: List[ASTNode],
        location: Optional[SourceLocation] = None,
    ):
        super().__init__(ASTNodeType.FUNCTION_CALL, location)
        self.name = name
        self.arguments = arguments
        for arg in arguments:
            self.add_child(arg)

    def accept(self, visitor):
        return visitor.visit_function_call(self)


@dataclass
class AssignmentNode(ASTNode):
    """Assignment statement node"""

    target: str
    value: ASTNode

    def __init__(
        self, target: str, value: ASTNode, location: Optional[SourceLocation] = None
    ):
        super().__init__(ASTNodeType.ASSIGNMENT, location)
        self.target = target
        self.value = value
        self.add_child(value)

    def accept(self, visitor):
        return visitor.visit_assignment(self)


@dataclass
class ProgramNode(ASTNode):
    """Program root node"""

    statements: List[ASTNode]

    def __init__(
        self, statements: List[ASTNode], location: Optional[SourceLocation] = None
    ):
        super().__init__(ASTNodeType.PROGRAM, location)
        self.statements = statements
        for stmt in statements:
            self.add_child(stmt)

    def accept(self, visitor):
        return visitor.visit_program(self)


class ParserState:
    """Parser state for better error recovery"""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
        self.error_manager = ErrorManager()

    def current_token(self) -> Optional[Token]:
        """Get current token"""
        return self.tokens[self.position] if self.position < len(self.tokens) else None

    def peek_token(self, offset: int = 1) -> Optional[Token]:
        """Peek at token with offset"""
        pos = self.position + offset
        return self.tokens[pos] if pos < len(self.tokens) else None

    def advance(self) -> Optional[Token]:
        """Advance to next token"""
        if self.position < len(self.tokens):
            token = self.tokens[self.position]
            self.position += 1
            return token
        return None

    def match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the given types"""
        current = self.current_token()
        return current is not None and current.type in token_types

    def consume(
        self, token_type: TokenType, error_message: str = ""
    ) -> Optional[Token]:
        """Consume expected token or report error"""
        current = self.current_token()
        if current and current.type == token_type:
            return self.advance()

        if not error_message:
            error_message = f"Expected {token_type.name}, got {current.type.name if current else 'EOF'}"

        location = current.location if current else SourceLocation(0, 0)
        self.error_manager.add_error(
            ErrorCode.UNEXPECTED_TOKEN,
            error_message,
            location,
            suggestions=[f"Add {token_type.name.lower()} token"],
        )
        return None


class EnhancedParser:
    """Enhanced parser with better error handling and recovery"""

    def __init__(self):
        self.state: Optional[ParserState] = None
        self.lexer = EnhancedLexer()

    def parse(self, text: str, filename: Optional[str] = None) -> Optional[ProgramNode]:
        """Parse source text into AST"""
        # Tokenize first
        tokens = self.lexer.tokenize(text, filename)

        # Check for lexical errors
        if self.lexer.has_errors():
            return None

        # Initialize parser state
        self.state = ParserState(tokens)

        try:
            return self._parse_program()
        except Exception as e:
            # Add error for unexpected parser failure
            self.state.error_manager.add_error(
                ErrorCode.INVALID_SYNTAX,
                f"Parser error: {e}",
                SourceLocation(0, 0, filename),
            )
            return None

    def _parse_program(self) -> ProgramNode:
        """Parse program (top level)"""
        if self.state is None:
            raise RuntimeError("Parser state not initialized")

        statements = []

        while not self.state.match(TokenType.EOF):
            # Skip newlines
            if self.state.match(TokenType.NEWLINE):
                self.state.advance()
                continue

            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
            else:
                # Error recovery - skip to next line
                self._skip_to_newline()

        return ProgramNode(statements)

    def _parse_statement(self) -> Optional[ASTNode]:
        """Parse a statement"""
        if self.state is None:
            return None

        current = self.state.current_token()
        if not current:
            return None

        # Assignment
        if (
            current.type == TokenType.IDENTIFIER
            and self.state.peek_token()
            and self.state.peek_token().type in [TokenType.ASSIGN, TokenType.EQUAL]
        ):
            return self._parse_assignment()

        # Expression statement (function calls, etc.)
        return self._parse_expression()

    def _parse_assignment(self) -> Optional[AssignmentNode]:
        """Parse assignment statement"""
        if self.state is None:
            return None

        identifier_token = self.state.consume(
            TokenType.IDENTIFIER, "Expected variable name"
        )
        if not identifier_token:
            return None

        # Handle both = and == (common mistake)
        assign_token = self.state.current_token()
        if assign_token and assign_token.type == TokenType.EQUAL:
            self.state.error_manager.add_warning(
                ErrorCode.UNEXPECTED_TOKEN,
                "Using '==' for assignment, did you mean '='?",
                assign_token.location,
                suggestions=["Use '=' for assignment", "Use '==' for comparison"],
            )

        self.state.consume(TokenType.ASSIGN, "Expected '=' for assignment")

        value = self._parse_expression()
        if not value:
            return None

        return AssignmentNode(identifier_token.value, value, identifier_token.location)

    def _parse_expression(self) -> Optional[ASTNode]:
        """Parse expression"""
        return self._parse_logical_or()

    def _parse_logical_or(self) -> Optional[ASTNode]:
        """Parse logical OR expression"""
        left = self._parse_logical_and()
        if not left:
            return None

        while self.state and self.state.match(TokenType.OR):
            operator_token = self.state.advance()
            right = self._parse_logical_and()
            if not right:
                return None
            left = BinaryOpNode(
                operator_token.value, left, right, operator_token.location
            )

        return left

    def _parse_logical_and(self) -> Optional[ASTNode]:
        """Parse logical AND expression"""
        left = self._parse_equality()
        if not left:
            return None

        while self.state and self.state.match(TokenType.AND):
            operator_token = self.state.advance()
            right = self._parse_equality()
            if not right:
                return None
            left = BinaryOpNode(
                operator_token.value, left, right, operator_token.location
            )

        return left

    def _parse_equality(self) -> Optional[ASTNode]:
        """Parse equality expression"""
        left = self._parse_comparison()
        if not left:
            return None

        while self.state and self.state.match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            operator_token = self.state.advance()
            right = self._parse_comparison()
            if not right:
                return None
            left = BinaryOpNode(
                operator_token.value, left, right, operator_token.location
            )

        return left

    def _parse_comparison(self) -> Optional[ASTNode]:
        """Parse comparison expression"""
        left = self._parse_addition()
        if not left:
            return None

        while self.state and self.state.match(
            TokenType.LESS_THAN,
            TokenType.GREATER_THAN,
            TokenType.LESS_EQUAL,
            TokenType.GREATER_EQUAL,
        ):
            operator_token = self.state.advance()
            right = self._parse_addition()
            if not right:
                return None
            left = BinaryOpNode(
                operator_token.value, left, right, operator_token.location
            )

        return left

    def _parse_addition(self) -> Optional[ASTNode]:
        """Parse addition/subtraction expression"""
        left = self._parse_multiplication()
        if not left:
            return None

        while self.state and self.state.match(TokenType.PLUS, TokenType.MINUS):
            operator_token = self.state.advance()
            right = self._parse_multiplication()
            if not right:
                return None
            left = BinaryOpNode(
                operator_token.value, left, right, operator_token.location
            )

        return left

    def _parse_multiplication(self) -> Optional[ASTNode]:
        """Parse multiplication/division expression"""
        left = self._parse_unary()
        if not left:
            return None

        while self.state and self.state.match(
            TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO
        ):
            operator_token = self.state.advance()
            right = self._parse_unary()
            if not right:
                return None
            left = BinaryOpNode(
                operator_token.value, left, right, operator_token.location
            )

        return left

    def _parse_unary(self) -> Optional[ASTNode]:
        """Parse unary expression"""
        if self.state and self.state.match(
            TokenType.NOT, TokenType.MINUS, TokenType.PLUS
        ):
            operator_token = self.state.advance()
            operand = self._parse_unary()
            if not operand:
                return None
            return UnaryOpNode(operator_token.value, operand, operator_token.location)

        return self._parse_power()

    def _parse_power(self) -> Optional[ASTNode]:
        """Parse power expression"""
        left = self._parse_primary()
        if not left:
            return None

        # Right associative
        if self.state and self.state.match(TokenType.POWER):
            operator_token = self.state.advance()
            right = self._parse_power()  # Right associative
            if not right:
                return None
            return BinaryOpNode(
                operator_token.value, left, right, operator_token.location
            )

        return left

    def _parse_primary(self) -> Optional[ASTNode]:
        """Parse primary expression"""
        if not self.state:
            return None

        current = self.state.current_token()
        if not current:
            return None

        # Numbers
        if current.type == TokenType.NUMBER:
            self.state.advance()
            try:
                if "." in current.value or "e" in current.value.lower():
                    value = float(current.value)
                else:
                    value = int(current.value)
                return LiteralNode(value, current.location)
            except ValueError:
                self.state.error_manager.add_error(
                    ErrorCode.INVALID_NUMBER,
                    f"Invalid number: {current.value}",
                    current.location,
                )
                return None

        # Strings
        if current.type == TokenType.STRING:
            self.state.advance()
            return LiteralNode(current.value, current.location)

        # Booleans
        if current.type == TokenType.BOOLEAN:
            self.state.advance()
            value = current.value.upper() == "TRUE"
            return LiteralNode(value, current.location)

        # Identifiers (variables or function calls)
        if current.type == TokenType.IDENTIFIER:
            self.state.advance()

            # Check for function call
            if self.state.match(TokenType.LEFT_PAREN):
                return self._parse_function_call(current.value, current.location)
            else:
                return IdentifierNode(current.value, current.location)

        # Parenthesized expressions
        if current.type == TokenType.LEFT_PAREN:
            self.state.advance()
            expr = self._parse_expression()
            if not expr:
                return None

            if not self.state.consume(
                TokenType.RIGHT_PAREN, "Expected ')' after expression"
            ):
                return None

            return expr

        # Unexpected token
        self.state.error_manager.add_error(
            ErrorCode.UNEXPECTED_TOKEN,
            f"Unexpected token: {current.value}",
            current.location,
            suggestions=["Check expression syntax"],
        )
        return None

    def _parse_function_call(
        self, name: str, location: SourceLocation
    ) -> Optional[FunctionCallNode]:
        """Parse function call"""
        if not self.state:
            return None

        # Already consumed identifier and checked for left paren
        self.state.consume(TokenType.LEFT_PAREN)

        arguments = []

        # Handle empty argument list
        if self.state.match(TokenType.RIGHT_PAREN):
            self.state.advance()
            return FunctionCallNode(name, arguments, location)

        # Parse arguments
        while True:
            arg = self._parse_expression()
            if not arg:
                return None
            arguments.append(arg)

            if self.state.match(TokenType.COMMA):
                self.state.advance()
            elif self.state.match(TokenType.RIGHT_PAREN):
                self.state.advance()
                break
            else:
                self.state.error_manager.add_error(
                    ErrorCode.UNEXPECTED_TOKEN,
                    "Expected ',' or ')' in function call",
                    (
                        self.state.current_token().location
                        if self.state.current_token()
                        else location
                    ),
                )
                return None

        return FunctionCallNode(name, arguments, location)

    def _skip_to_newline(self):
        """Skip tokens until newline for error recovery"""
        if not self.state:
            return

        while not self.state.match(TokenType.NEWLINE, TokenType.EOF):
            self.state.advance()

    def get_errors(self) -> List[TimeWarpError]:
        """Get parser errors"""
        errors = []

        # Add lexer errors
        if self.lexer:
            errors.extend(self.lexer.get_errors())

        # Add parser errors
        if self.state:
            errors.extend(self.state.error_manager.get_all_issues())

        return errors

    def has_errors(self) -> bool:
        """Check if there are parsing errors"""
        return len(self.get_errors()) > 0
