"""
Time_Warp IDE Language Parser
Parses tokenized Time_Warp IDE source code into an Abstract Syntax Tree (AST)
"""

from typing import List, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum
from .lexer import Token, TokenType, TimeWarpLexer


# AST Node Types
@dataclass
class ASTNode:
    """Base class for all AST nodes"""

    line: int
    column: int


@dataclass
class ProgramNode(ASTNode):
    """Root node of the program"""

    statements: List[ASTNode]

    def __init__(self, statements: List[ASTNode], line: int, column: int):
        super().__init__(line, column)
        self.statements = statements


@dataclass
class NumberNode(ASTNode):
    """Numeric literal"""

    value: Union[int, float]

    def __init__(self, value: Union[int, float], line: int, column: int):
        super().__init__(line, column)
        self.value = value


@dataclass
class StringNode(ASTNode):
    """String literal"""

    value: str

    def __init__(self, value: str, line: int, column: int):
        super().__init__(line, column)
        self.value = value


@dataclass
class IdentifierNode(ASTNode):
    """Variable or function identifier"""

    name: str

    def __init__(self, name: str, line: int, column: int):
        super().__init__(line, column)
        self.name = name


@dataclass
class BinaryOpNode(ASTNode):
    """Binary operation (e.g., +, -, *, /)"""

    left: ASTNode
    operator: str
    right: ASTNode

    def __init__(
        self, left: ASTNode, operator: str, right: ASTNode, line: int, column: int
    ):
        super().__init__(line, column)
        self.left = left
        self.operator = operator
        self.right = right


@dataclass
class UnaryOpNode(ASTNode):
    """Unary operation (e.g., -, NOT)"""

    operator: str
    operand: ASTNode

    def __init__(self, operator: str, operand: ASTNode, line: int, column: int):
        super().__init__(line, column)
        self.operator = operator
        self.operand = operand


@dataclass
class AssignmentNode(ASTNode):
    """Variable assignment"""

    variable: str
    value: ASTNode

    def __init__(self, variable: str, value: ASTNode, line: int, column: int):
        super().__init__(line, column)
        self.variable = variable
        self.value = value


@dataclass
class PrintNode(ASTNode):
    """PRINT statement"""

    expressions: List[ASTNode]

    def __init__(self, expressions: List[ASTNode], line: int, column: int):
        super().__init__(line, column)
        self.expressions = expressions


@dataclass
class InputNode(ASTNode):
    """INPUT statement"""

    variable: str
    prompt: Optional[str] = None

    def __init__(self, variable: str, prompt: Optional[str], line: int, column: int):
        super().__init__(line, column)
        self.variable = variable
        self.prompt = prompt


@dataclass
class IfNode(ASTNode):
    """IF/THEN/ELSE statement"""

    condition: ASTNode
    then_statements: List[ASTNode]
    elif_conditions: List[tuple]  # [(condition, statements), ...]
    else_statements: Optional[List[ASTNode]] = None

    def __init__(
        self,
        condition: ASTNode,
        then_statements: List[ASTNode],
        elif_conditions: List[tuple],
        else_statements: Optional[List[ASTNode]],
        line: int,
        column: int,
    ):
        super().__init__(line, column)
        self.condition = condition
        self.then_statements = then_statements
        self.elif_conditions = elif_conditions
        self.else_statements = else_statements


@dataclass
class ForNode(ASTNode):
    """FOR loop"""

    variable: str
    start: ASTNode
    end: ASTNode
    step: Optional[ASTNode]
    statements: List[ASTNode]

    def __init__(
        self,
        variable: str,
        start: ASTNode,
        end: ASTNode,
        step: Optional[ASTNode],
        statements: List[ASTNode],
        line: int,
        column: int,
    ):
        super().__init__(line, column)
        self.variable = variable
        self.start = start
        self.end = end
        self.step = step
        self.statements = statements


@dataclass
class WhileNode(ASTNode):
    """WHILE loop"""

    condition: ASTNode
    statements: List[ASTNode]

    def __init__(
        self, condition: ASTNode, statements: List[ASTNode], line: int, column: int
    ):
        super().__init__(line, column)
        self.condition = condition
        self.statements = statements


@dataclass
class FunctionDefNode(ASTNode):
    """Function definition"""

    name: str
    parameters: List[str]
    statements: List[ASTNode]

    def __init__(
        self,
        name: str,
        parameters: List[str],
        statements: List[ASTNode],
        line: int,
        column: int,
    ):
        super().__init__(line, column)
        self.name = name
        self.parameters = parameters
        self.statements = statements


@dataclass
class FunctionCallNode(ASTNode):
    """Function call"""

    name: str
    arguments: List[ASTNode]

    def __init__(self, name: str, arguments: List[ASTNode], line: int, column: int):
        super().__init__(line, column)
        self.name = name
        self.arguments = arguments


@dataclass
class ReturnNode(ASTNode):
    """RETURN statement"""

    value: Optional[ASTNode] = None

    def __init__(self, value: Optional[ASTNode], line: int, column: int):
        super().__init__(line, column)
        self.value = value


@dataclass
class ModeNode(ASTNode):
    """Mode switching statement"""

    mode: str
    statements: List[ASTNode]

    def __init__(self, mode: str, statements: List[ASTNode], line: int, column: int):
        super().__init__(line, column)
        self.mode = mode
        self.statements = statements


@dataclass
class PilotCommandNode(ASTNode):
    """PILOT command"""

    command: str
    argument: str

    def __init__(self, command: str, argument: str, line: int, column: int):
        super().__init__(line, column)
        self.command = command
        self.argument = argument


@dataclass
class LogoCommandNode(ASTNode):
    """Logo turtle command"""

    command: str
    arguments: List[ASTNode]

    def __init__(self, command: str, arguments: List[ASTNode], line: int, column: int):
        super().__init__(line, column)
        self.command = command
        self.arguments = arguments


@dataclass
class PythonBlockNode(ASTNode):
    """Python code block"""

    code: str

    def __init__(self, code: str, line: int, column: int):
        super().__init__(line, column)
        self.code = code


@dataclass
class TryNode(ASTNode):
    """Try/catch/finally block"""

    try_statements: List[ASTNode]
    catch_clauses: List[tuple]  # [(exception_type, statements), ...]
    finally_statements: Optional[List[ASTNode]] = None

    def __init__(
        self,
        try_statements: List[ASTNode],
        catch_clauses: List[tuple],
        finally_statements: Optional[List[ASTNode]],
        line: int,
        column: int,
    ):
        super().__init__(line, column)
        self.try_statements = try_statements
        self.catch_clauses = catch_clauses
        self.finally_statements = finally_statements


class ParseError(Exception):
    """Parser error"""

    pass


class TimeWarpParser:
    """Parser for Time_Warp IDE language"""

    def __init__(self):
        self.tokens = []
        self.current = 0

    def parse(self, tokens: List[Token]) -> ProgramNode:
        """Parse tokens into AST"""
        self.tokens = tokens
        self.current = 0

        statements = []
        while not self._is_at_end():
            if self._check(TokenType.NEWLINE):
                self._advance()
                continue

            stmt = self._statement()
            if stmt:
                statements.append(stmt)

        return ProgramNode(statements, 1, 1)

    def _statement(self) -> Optional[ASTNode]:
        """Parse a statement"""
        try:
            # Line numbers (ignore for now)
            if self._check(TokenType.LINE_NUMBER):
                self._advance()

            # Comments (ignore)
            if self._check(TokenType.COMMENT):
                self._advance()
                return None

            # Assignment (LET is optional)
            if self._check(TokenType.LET):
                return self._assignment_statement()

            # Print statement
            if self._check(TokenType.PRINT):
                return self._print_statement()

            # Input statement
            if self._check(TokenType.INPUT):
                return self._input_statement()

            # Control flow
            if self._check(TokenType.IF):
                return self._if_statement()

            if self._check(TokenType.FOR):
                return self._for_statement()

            if self._check(TokenType.WHILE):
                return self._while_statement()

            # Function definition
            if self._check(TokenType.DEF):
                return self._function_definition()

            # Return statement
            if self._check(TokenType.RETURN):
                return self._return_statement()

            # Mode switching
            if self._check(TokenType.MODE):
                return self._mode_statement()

            # PILOT commands
            if self._check_pilot_command():
                return self._pilot_command()

            # Logo commands
            if self._check_logo_command():
                return self._logo_command()

            # Python block
            if self._check(TokenType.PYTHON):
                return self._python_block()

            # Try/catch
            if self._check(TokenType.TRY):
                return self._try_statement()

            # Expression statement (assignment without LET)
            if self._check(TokenType.IDENTIFIER):
                return self._expression_statement()

            # Skip unknown tokens
            self._advance()
            return None

        except ParseError as e:
            print(f"Parse error: {e}")
            self._synchronize()
            return None

    def _assignment_statement(self) -> AssignmentNode:
        """Parse assignment statement"""
        line, col = self._peek().line, self._peek().column

        if self._check(TokenType.LET):
            self._advance()

        if not self._check(TokenType.IDENTIFIER):
            raise ParseError("Expected variable name")

        var_name = self._advance().value

        if not self._check(TokenType.EQUALS):
            raise ParseError("Expected '=' in assignment")

        self._advance()
        value = self._expression()

        return AssignmentNode(var_name, value, line, col)

    def _print_statement(self) -> PrintNode:
        """Parse PRINT statement"""
        line, col = self._peek().line, self._peek().column
        self._advance()  # consume PRINT

        expressions = []
        if not self._check(TokenType.NEWLINE) and not self._is_at_end():
            expressions.append(self._expression())

            while self._check(TokenType.COMMA) or self._check(TokenType.SEMICOLON):
                self._advance()
                if not self._check(TokenType.NEWLINE) and not self._is_at_end():
                    expressions.append(self._expression())

        return PrintNode(expressions, line, col)

    def _input_statement(self) -> InputNode:
        """Parse INPUT statement"""
        line, col = self._peek().line, self._peek().column
        self._advance()  # consume INPUT

        prompt = None
        if self._check(TokenType.STRING):
            prompt = self._advance().value[1:-1]  # Remove quotes
            if self._check(TokenType.SEMICOLON):
                self._advance()

        if not self._check(TokenType.IDENTIFIER):
            raise ParseError("Expected variable name in INPUT")

        var_name = self._advance().value

        return InputNode(var_name, prompt, line, col)

    def _if_statement(self) -> IfNode:
        """Parse IF statement"""
        line, col = self._peek().line, self._peek().column
        self._advance()  # consume IF

        condition = self._expression()

        if not self._check(TokenType.THEN):
            raise ParseError("Expected THEN after IF condition")
        self._advance()

        then_statements = []
        elif_conditions = []
        else_statements = None

        # Parse THEN block
        while (
            not self._check(TokenType.ELIF)
            and not self._check(TokenType.ELSE)
            and not self._check(TokenType.ENDIF)
            and not self._is_at_end()
        ):
            if self._check(TokenType.NEWLINE):
                self._advance()
                continue
            stmt = self._statement()
            if stmt:
                then_statements.append(stmt)

        # Parse ELIF blocks
        while self._check(TokenType.ELIF):
            self._advance()
            elif_condition = self._expression()
            if not self._check(TokenType.THEN):
                raise ParseError("Expected THEN after ELIF condition")
            self._advance()

            elif_statements = []
            while (
                not self._check(TokenType.ELIF)
                and not self._check(TokenType.ELSE)
                and not self._check(TokenType.ENDIF)
                and not self._is_at_end()
            ):
                if self._check(TokenType.NEWLINE):
                    self._advance()
                    continue
                stmt = self._statement()
                if stmt:
                    elif_statements.append(stmt)

            elif_conditions.append((elif_condition, elif_statements))

        # Parse ELSE block
        if self._check(TokenType.ELSE):
            self._advance()
            else_statements = []
            while not self._check(TokenType.ENDIF) and not self._is_at_end():
                if self._check(TokenType.NEWLINE):
                    self._advance()
                    continue
                stmt = self._statement()
                if stmt:
                    else_statements.append(stmt)

        if not self._check(TokenType.ENDIF):
            raise ParseError("Expected ENDIF")
        self._advance()

        return IfNode(
            condition, then_statements, elif_conditions, else_statements, line, col
        )

    def _for_statement(self) -> ForNode:
        """Parse FOR loop"""
        line, col = self._peek().line, self._peek().column
        self._advance()  # consume FOR

        if not self._check(TokenType.IDENTIFIER):
            raise ParseError("Expected variable name in FOR loop")

        var_name = self._advance().value

        if not self._check(TokenType.EQUALS):
            raise ParseError("Expected '=' in FOR loop")
        self._advance()

        start = self._expression()

        if not self._check(TokenType.TO):
            raise ParseError("Expected TO in FOR loop")
        self._advance()

        end = self._expression()

        step = None
        if self._check(TokenType.STEP):
            self._advance()
            step = self._expression()

        statements = []
        while not self._check(TokenType.NEXT) and not self._is_at_end():
            if self._check(TokenType.NEWLINE):
                self._advance()
                continue
            stmt = self._statement()
            if stmt:
                statements.append(stmt)

        if not self._check(TokenType.NEXT):
            raise ParseError("Expected NEXT")
        self._advance()

        # Optional variable name after NEXT
        if self._check(TokenType.IDENTIFIER):
            self._advance()

        return ForNode(var_name, start, end, step, statements, line, col)

    def _while_statement(self) -> WhileNode:
        """Parse WHILE loop"""
        line, col = self._peek().line, self._peek().column
        self._advance()  # consume WHILE

        condition = self._expression()

        statements = []
        while not self._check(TokenType.WEND) and not self._is_at_end():
            if self._check(TokenType.NEWLINE):
                self._advance()
                continue
            stmt = self._statement()
            if stmt:
                statements.append(stmt)

        if not self._check(TokenType.WEND):
            raise ParseError("Expected WEND")
        self._advance()

        return WhileNode(condition, statements, line, col)

    def _function_definition(self) -> FunctionDefNode:
        """Parse function definition"""
        line, col = self._peek().line, self._peek().column
        self._advance()  # consume DEF

        if not self._check(TokenType.IDENTIFIER):
            raise ParseError("Expected function name")

        func_name = self._advance().value

        if not self._check(TokenType.LPAREN):
            raise ParseError("Expected '(' after function name")
        self._advance()

        parameters = []
        if not self._check(TokenType.RPAREN):
            parameters.append(self._advance().value)
            while self._check(TokenType.COMMA):
                self._advance()
                if not self._check(TokenType.IDENTIFIER):
                    raise ParseError("Expected parameter name")
                parameters.append(self._advance().value)

        if not self._check(TokenType.RPAREN):
            raise ParseError("Expected ')'")
        self._advance()

        statements = []
        while not self._check(TokenType.END_DEF) and not self._is_at_end():
            if self._check(TokenType.NEWLINE):
                self._advance()
                continue
            stmt = self._statement()
            if stmt:
                statements.append(stmt)

        if not self._check(TokenType.END_DEF):
            raise ParseError("Expected END_DEF")
        self._advance()

        return FunctionDefNode(func_name, parameters, statements, line, col)

    def _return_statement(self) -> ReturnNode:
        """Parse RETURN statement"""
        line, col = self._peek().line, self._peek().column
        self._advance()  # consume RETURN

        value = None
        if not self._check(TokenType.NEWLINE) and not self._is_at_end():
            value = self._expression()

        return ReturnNode(value, line, col)

    def _mode_statement(self) -> ModeNode:
        """Parse MODE statement"""
        line, col = self._peek().line, self._peek().column
        self._advance()  # consume MODE

        if not self._check(TokenType.IDENTIFIER):
            raise ParseError("Expected mode name")

        mode = self._advance().value

        statements = []
        # Mode statements continue until another MODE or end of block
        while not self._check(TokenType.MODE) and not self._is_at_end():
            if self._check(TokenType.NEWLINE):
                self._advance()
                continue
            stmt = self._statement()
            if stmt:
                statements.append(stmt)

        return ModeNode(mode, statements, line, col)

    def _pilot_command(self) -> PilotCommandNode:
        """Parse PILOT command"""
        line, col = self._peek().line, self._peek().column
        command_token = self._advance()

        # Get the rest of the line as argument
        argument = ""
        while not self._check(TokenType.NEWLINE) and not self._is_at_end():
            token = self._advance()
            argument += token.value + " "

        return PilotCommandNode(command_token.value, argument.strip(), line, col)

    def _logo_command(self) -> LogoCommandNode:
        """Parse Logo command"""
        line, col = self._peek().line, self._peek().column
        command = self._advance().value

        arguments = []
        while not self._check(TokenType.NEWLINE) and not self._is_at_end():
            if self._check(TokenType.COMMA):
                self._advance()
                continue
            arguments.append(self._expression())

        return LogoCommandNode(command, arguments, line, col)

    def _python_block(self) -> PythonBlockNode:
        """Parse Python code block"""
        line, col = self._peek().line, self._peek().column
        self._advance()  # consume PYTHON

        code_lines = []
        while not self._check(TokenType.END_PYTHON) and not self._is_at_end():
            if self._check(TokenType.NEWLINE):
                code_lines.append("")
                self._advance()
                continue

            # Collect all tokens on this line
            line_tokens = []
            while (
                not self._check(TokenType.NEWLINE)
                and not self._check(TokenType.END_PYTHON)
                and not self._is_at_end()
            ):
                line_tokens.append(self._advance().value)

            code_lines.append(" ".join(line_tokens))

        if not self._check(TokenType.END_PYTHON):
            raise ParseError("Expected END_PYTHON")
        self._advance()

        return PythonBlockNode("\\n".join(code_lines), line, col)

    def _try_statement(self) -> TryNode:
        """Parse TRY statement"""
        line, col = self._peek().line, self._peek().column
        self._advance()  # consume TRY

        try_statements = []
        catch_clauses = []
        finally_statements = None

        # Parse TRY block
        while (
            not self._check(TokenType.CATCH)
            and not self._check(TokenType.FINALLY)
            and not self._check(TokenType.END_TRY)
            and not self._is_at_end()
        ):
            if self._check(TokenType.NEWLINE):
                self._advance()
                continue
            stmt = self._statement()
            if stmt:
                try_statements.append(stmt)

        # Parse CATCH blocks
        while self._check(TokenType.CATCH):
            self._advance()
            exception_type = None
            if self._check(TokenType.IDENTIFIER):
                exception_type = self._advance().value

            catch_statements = []
            while (
                not self._check(TokenType.CATCH)
                and not self._check(TokenType.FINALLY)
                and not self._check(TokenType.END_TRY)
                and not self._is_at_end()
            ):
                if self._check(TokenType.NEWLINE):
                    self._advance()
                    continue
                stmt = self._statement()
                if stmt:
                    catch_statements.append(stmt)

            catch_clauses.append((exception_type, catch_statements))

        # Parse FINALLY block
        if self._check(TokenType.FINALLY):
            self._advance()
            finally_statements = []
            while not self._check(TokenType.END_TRY) and not self._is_at_end():
                if self._check(TokenType.NEWLINE):
                    self._advance()
                    continue
                stmt = self._statement()
                if stmt:
                    finally_statements.append(stmt)

        if not self._check(TokenType.END_TRY):
            raise ParseError("Expected END_TRY")
        self._advance()

        return TryNode(try_statements, catch_clauses, finally_statements, line, col)

    def _expression_statement(self) -> Optional[ASTNode]:
        """Parse expression statement (assignment without LET)"""
        # Look ahead to see if this is an assignment
        if (
            self.current + 1 < len(self.tokens)
            and self.tokens[self.current + 1].type == TokenType.EQUALS
        ):
            return self._assignment_statement()

        # Otherwise, it's just an expression (function call, etc.)
        expr = self._expression()
        return expr

    def _expression(self) -> ASTNode:
        """Parse expression"""
        return self._or_expression()

    def _or_expression(self) -> ASTNode:
        """Parse OR expression"""
        expr = self._and_expression()

        while self._check(TokenType.OR):
            operator = self._advance().value
            right = self._and_expression()
            expr = BinaryOpNode(expr, operator, right, expr.line, expr.column)

        return expr

    def _and_expression(self) -> ASTNode:
        """Parse AND expression"""
        expr = self._equality()

        while self._check(TokenType.AND):
            operator = self._advance().value
            right = self._equality()
            expr = BinaryOpNode(expr, operator, right, expr.line, expr.column)

        return expr

    def _equality(self) -> ASTNode:
        """Parse equality expression"""
        expr = self._comparison()

        while self._check(TokenType.EQUALS) or self._check(TokenType.NOT_EQUALS):
            operator = self._advance().value
            right = self._comparison()
            expr = BinaryOpNode(expr, operator, right, expr.line, expr.column)

        return expr

    def _comparison(self) -> ASTNode:
        """Parse comparison expression"""
        expr = self._addition()

        while (
            self._check(TokenType.GREATER_THAN)
            or self._check(TokenType.GREATER_EQUAL)
            or self._check(TokenType.LESS_THAN)
            or self._check(TokenType.LESS_EQUAL)
        ):
            operator = self._advance().value
            right = self._addition()
            expr = BinaryOpNode(expr, operator, right, expr.line, expr.column)

        return expr

    def _addition(self) -> ASTNode:
        """Parse addition/subtraction"""
        expr = self._multiplication()

        while self._check(TokenType.PLUS) or self._check(TokenType.MINUS):
            operator = self._advance().value
            right = self._multiplication()
            expr = BinaryOpNode(expr, operator, right, expr.line, expr.column)

        return expr

    def _multiplication(self) -> ASTNode:
        """Parse multiplication/division"""
        expr = self._power()

        while self._check(TokenType.MULTIPLY) or self._check(TokenType.DIVIDE):
            operator = self._advance().value
            right = self._power()
            expr = BinaryOpNode(expr, operator, right, expr.line, expr.column)

        return expr

    def _power(self) -> ASTNode:
        """Parse power expression"""
        expr = self._unary()

        if self._check(TokenType.POWER):
            operator = self._advance().value
            right = self._power()  # Right associative
            expr = BinaryOpNode(expr, operator, right, expr.line, expr.column)

        return expr

    def _unary(self) -> ASTNode:
        """Parse unary expression"""
        if self._check(TokenType.NOT) or self._check(TokenType.MINUS):
            operator = self._advance().value
            expr = self._unary()
            return UnaryOpNode(operator, expr, expr.line, expr.column)

        return self._primary()

    def _primary(self) -> ASTNode:
        """Parse primary expression"""
        line, col = self._peek().line, self._peek().column

        if self._check(TokenType.NUMBER):
            value = self._advance().value
            if "." in value:
                return NumberNode(float(value), line, col)
            else:
                return NumberNode(int(value), line, col)

        if self._check(TokenType.STRING):
            value = self._advance().value[1:-1]  # Remove quotes
            return StringNode(value, line, col)

        if self._check(TokenType.IDENTIFIER):
            name = self._advance().value

            # Function call
            if self._check(TokenType.LPAREN):
                self._advance()
                arguments = []

                if not self._check(TokenType.RPAREN):
                    arguments.append(self._expression())
                    while self._check(TokenType.COMMA):
                        self._advance()
                        arguments.append(self._expression())

                if not self._check(TokenType.RPAREN):
                    raise ParseError("Expected ')'")
                self._advance()

                return FunctionCallNode(name, arguments, line, col)

            return IdentifierNode(name, line, col)

        if self._check(TokenType.LPAREN):
            self._advance()
            expr = self._expression()
            if not self._check(TokenType.RPAREN):
                raise ParseError("Expected ')'")
            self._advance()
            return expr

        raise ParseError(f"Unexpected token: {self._peek().value}")

    # Helper methods
    def _check(self, token_type: TokenType) -> bool:
        """Check if current token is of given type"""
        if self._is_at_end():
            return False
        return self._peek().type == token_type

    def _check_pilot_command(self) -> bool:
        """Check if current token is a PILOT command"""
        return (
            self._check(TokenType.T_COLON)
            or self._check(TokenType.A_COLON)
            or self._check(TokenType.M_COLON)
            or self._check(TokenType.J_COLON)
            or self._check(TokenType.C_COLON)
            or self._check(TokenType.U_COLON)
            or self._check(TokenType.R_COLON)
            or self._check(TokenType.E_COLON)
        )

    def _check_logo_command(self) -> bool:
        """Check if current token is a Logo command"""
        logo_commands = [
            TokenType.FORWARD,
            TokenType.FD,
            TokenType.BACK,
            TokenType.BK,
            TokenType.LEFT,
            TokenType.LT,
            TokenType.RIGHT,
            TokenType.RT,
            TokenType.PENUP,
            TokenType.PU,
            TokenType.PENDOWN,
            TokenType.PD,
            TokenType.SETCOLOR,
            TokenType.REPEAT,
            TokenType.HOME,
            TokenType.CLEARSCREEN,
            TokenType.CS,
        ]
        return any(self._check(cmd) for cmd in logo_commands)

    def _advance(self) -> Token:
        """Consume current token and return it"""
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _is_at_end(self) -> bool:
        """Check if we've reached the end"""
        return self._peek().type == TokenType.EOF

    def _peek(self) -> Token:
        """Return current token without advancing"""
        return self.tokens[self.current]

    def _previous(self) -> Token:
        """Return previous token"""
        return self.tokens[self.current - 1]

    def _synchronize(self):
        """Synchronize parser after error"""
        self._advance()

        while not self._is_at_end():
            if self._previous().type == TokenType.NEWLINE:
                return

            sync_tokens = [
                TokenType.PRINT,
                TokenType.LET,
                TokenType.IF,
                TokenType.FOR,
                TokenType.WHILE,
                TokenType.DEF,
                TokenType.RETURN,
            ]
            if self._peek().type in sync_tokens:
                return

            self._advance()
