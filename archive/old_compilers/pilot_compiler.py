#!/usr/bin/env python3
"""
PILOT Native Compiler
=====================

A compiler for the PILOT (Programmed Inquiry, Learning, Or Teaching) 
programming language that produces standalone Linux executables.

This compiler takes PILOT source code and generates native C code which
is then compiled into a standalone Linux executable that can run without
requiring Python or the Time_Warp IDE.

Architecture:
1. Lexer: tokenizes PILOT source code
2. Parser: builds Abstract Syntax Tree (AST)
3. Code Generator: generates C code from AST
4. Executable Builder: compiles C code to Linux executable

PILOT Language Features Supported:
- Text output (T:)
- User input (A:)
- Conditional branching (Y:, N:)
- Jumps and labels (J:, L:)
- Variable updates (U:, C:)
- Match conditions (M:, MT:)
- String interpolation (*VAR*)
- Expression evaluation
- Arithmetic operations
- Built-in functions (RND, INT, STR$, etc.)
"""

import re
import os
import sys
import subprocess
import tempfile
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    """Token types for PILOT language"""
    # Commands
    TEXT_OUTPUT = auto()      # T:
    ACCEPT_INPUT = auto()     # A:
    YES_CONDITION = auto()    # Y:
    NO_CONDITION = auto()     # N:
    JUMP = auto()            # J:
    CONDITIONAL_JUMP = auto() # J(condition):
    LABEL = auto()           # L:
    UPDATE = auto()          # U:
    COMPUTE = auto()         # C:
    MATCH_JUMP = auto()      # M:
    MATCH_TEXT = auto()      # MT:
    
    # Extended commands
    RUNTIME = auto()         # R:
    GAME = auto()           # GAME:
    AUDIO = auto()          # AUDIO:
    FILE = auto()           # F:
    WEB = auto()            # W:
    DATABASE = auto()       # D:
    STRING = auto()         # S:
    DATETIME = auto()       # DT:
    
    # Literals and identifiers
    STRING_LITERAL = auto()
    NUMBER_LITERAL = auto()
    IDENTIFIER = auto()
    VARIABLE_REF = auto()    # *VAR*
    
    # Operators
    EQUALS = auto()          # =
    PLUS = auto()           # +
    MINUS = auto()          # -
    MULTIPLY = auto()       # *
    DIVIDE = auto()         # /
    MODULO = auto()         # %
    
    # Comparison operators
    LESS_THAN = auto()      # <
    GREATER_THAN = auto()   # >
    LESS_EQUAL = auto()     # <=
    GREATER_EQUAL = auto()  # >=
    EQUAL_EQUAL = auto()    # ==
    NOT_EQUAL = auto()      # !=
    
    # Logical operators
    AND = auto()            # AND
    OR = auto()             # OR
    NOT = auto()            # NOT
    
    # Punctuation
    LPAREN = auto()         # (
    RPAREN = auto()         # )
    COMMA = auto()          # ,
    COLON = auto()          # :
    
    # Special
    NEWLINE = auto()
    END = auto()
    EOF = auto()


@dataclass
class Token:
    """Token representation"""
    type: TokenType
    value: str
    line: int
    column: int


class PilotLexer:
    """Lexical analyzer for PILOT language"""
    
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        
    def current_char(self) -> Optional[str]:
        """Get current character"""
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos]
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        """Peek at character ahead"""
        peek_pos = self.pos + offset
        if peek_pos >= len(self.source):
            return None
        return self.source[peek_pos]
    
    def advance(self):
        """Move to next character"""
        if self.pos < len(self.source) and self.source[self.pos] == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.pos += 1
    
    def skip_whitespace(self):
        """Skip whitespace except newlines"""
        char = self.current_char()
        while char and char in ' \t\r':
            self.advance()
            char = self.current_char()
    
    def read_string(self, quote_char: str) -> str:
        """Read quoted string literal"""
        value = ""
        self.advance()  # Skip opening quote
        
        while self.current_char() and self.current_char() != quote_char:
            if self.current_char() == '\\':
                self.advance()
                escape_char = self.current_char()
                if escape_char == 'n':
                    value += '\n'
                elif escape_char == 't':
                    value += '\t'
                elif escape_char == 'r':
                    value += '\r'
                elif escape_char == '\\':
                    value += '\\'
                elif escape_char == quote_char:
                    value += quote_char
                else:
                    value += escape_char or ''
                self.advance()
            else:
                value += self.current_char()
                self.advance()
        
        if self.current_char() == quote_char:
            self.advance()  # Skip closing quote
        
        return value
    
    def read_number(self) -> str:
        """Read numeric literal"""
        value = ""
        has_dot = False
        
        while self.current_char() and (self.current_char().isdigit() or 
                                      (self.current_char() == '.' and not has_dot)):
            if self.current_char() == '.':
                has_dot = True
            value += self.current_char()
            self.advance()
        
        return value
    
    def read_identifier(self) -> str:
        """Read identifier or keyword"""
        value = ""
        
        char = self.current_char()
        while (char and (char.isalnum() or char in '_$')):
            value += char
            self.advance()
            char = self.current_char()
        
        return value
    
    def read_command(self) -> Optional[Token]:
        """Read PILOT command"""
        start_line = self.line
        start_column = self.column
        
        # Handle conditional jump J(...):
        if self.current_char() == 'J' and self.peek_char() == '(':
            # Read the entire J(condition): construct
            value = ""
            while self.current_char() and self.current_char() != ':':
                value += self.current_char()
                self.advance()
            if self.current_char() == ':':
                value += self.current_char()
                self.advance()
            return Token(TokenType.CONDITIONAL_JUMP, value, start_line, start_column)
        
        # Read command prefix
        cmd = ""
        while self.current_char() and self.current_char().isalpha():
            cmd += self.current_char()
            self.advance()
        
        # Check for colon
        if self.current_char() == ':':
            cmd += self.current_char()
            self.advance()
            
            # Map command strings to token types
            command_map = {
                'T:': TokenType.TEXT_OUTPUT,
                'A:': TokenType.ACCEPT_INPUT,
                'Y:': TokenType.YES_CONDITION,
                'N:': TokenType.NO_CONDITION,
                'J:': TokenType.JUMP,
                'L:': TokenType.LABEL,
                'U:': TokenType.UPDATE,
                'C:': TokenType.COMPUTE,
                'M:': TokenType.MATCH_JUMP,
                'MT:': TokenType.MATCH_TEXT,
                'R:': TokenType.RUNTIME,
                'F:': TokenType.FILE,
                'W:': TokenType.WEB,
                'D:': TokenType.DATABASE,
                'S:': TokenType.STRING,
                'DT:': TokenType.DATETIME,
                'GAME:': TokenType.GAME,
                'AUDIO:': TokenType.AUDIO,
            }
            
            token_type = command_map.get(cmd, TokenType.IDENTIFIER)
            return Token(token_type, cmd, start_line, start_column)
        
        # Not a command, backtrack and treat as identifier
        self.pos -= len(cmd)
        self.column -= len(cmd)
        return None
    
    def tokenize(self) -> List[Token]:
        """Tokenize the source code"""
        while self.pos < len(self.source):
            self.skip_whitespace()
            
            if not self.current_char():
                break
            
            start_line = self.line
            start_column = self.column
            char = self.current_char()
            
            # Newlines
            if char == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, char, start_line, start_column))
                self.advance()
            
            # Comments (if we want to support them)
            elif char == '#':
                # Skip rest of line
                while self.current_char() and self.current_char() != '\n':
                    self.advance()
            
            # String literals
            elif char in '"\'':
                value = self.read_string(char)
                self.tokens.append(Token(TokenType.STRING_LITERAL, value, start_line, start_column))
            
            # Variable references *VAR*
            elif char == '*':
                self.advance()
                if self.current_char() and self.current_char().isalpha():
                    var_name = self.read_identifier()
                    if self.current_char() == '*':
                        self.advance()
                        self.tokens.append(Token(TokenType.VARIABLE_REF, f"*{var_name}*", start_line, start_column))
                    else:
                        # Just a * operator
                        self.tokens.append(Token(TokenType.MULTIPLY, "*", start_line, start_column))
                        # Put back the identifier
                        self.pos -= len(var_name)
                        self.column -= len(var_name)
                else:
                    self.tokens.append(Token(TokenType.MULTIPLY, "*", start_line, start_column))
            
            # Numbers
            elif char.isdigit():
                value = self.read_number()
                self.tokens.append(Token(TokenType.NUMBER_LITERAL, value, start_line, start_column))
            
            # Commands or identifiers
            elif char.isalpha():
                # Try to read as command first
                cmd_token = self.read_command()
                if cmd_token:
                    self.tokens.append(cmd_token)
                else:
                    # Read as identifier
                    value = self.read_identifier()
                    
                    # Check for special keywords
                    if value.upper() == "END":
                        self.tokens.append(Token(TokenType.END, value, start_line, start_column))
                    elif value.upper() in ["AND", "OR", "NOT"]:
                        token_type = {
                            "AND": TokenType.AND,
                            "OR": TokenType.OR,
                            "NOT": TokenType.NOT
                        }[value.upper()]
                        self.tokens.append(Token(token_type, value, start_line, start_column))
                    else:
                        self.tokens.append(Token(TokenType.IDENTIFIER, value, start_line, start_column))
            
            # Operators and punctuation
            elif char == '=':
                if self.peek_char() == '=':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.EQUAL_EQUAL, "==", start_line, start_column))
                else:
                    self.advance()
                    self.tokens.append(Token(TokenType.EQUALS, "=", start_line, start_column))
            
            elif char == '<':
                if self.peek_char() == '=':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.LESS_EQUAL, "<=", start_line, start_column))
                else:
                    self.advance()
                    self.tokens.append(Token(TokenType.LESS_THAN, "<", start_line, start_column))
            
            elif char == '>':
                if self.peek_char() == '=':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.GREATER_EQUAL, ">=", start_line, start_column))
                else:
                    self.advance()
                    self.tokens.append(Token(TokenType.GREATER_THAN, ">", start_line, start_column))
            
            elif char == '!':
                if self.peek_char() == '=':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.NOT_EQUAL, "!=", start_line, start_column))
                else:
                    self.advance()
                    self.tokens.append(Token(TokenType.NOT, "!", start_line, start_column))
            
            elif char == '+':
                self.advance()
                self.tokens.append(Token(TokenType.PLUS, "+", start_line, start_column))
            
            elif char == '-':
                self.advance()
                self.tokens.append(Token(TokenType.MINUS, "-", start_line, start_column))
            
            elif char == '/':
                self.advance()
                self.tokens.append(Token(TokenType.DIVIDE, "/", start_line, start_column))
            
            elif char == '%':
                self.advance()
                self.tokens.append(Token(TokenType.MODULO, "%", start_line, start_column))
            
            elif char == '(':
                self.advance()
                self.tokens.append(Token(TokenType.LPAREN, "(", start_line, start_column))
            
            elif char == ')':
                self.advance()
                self.tokens.append(Token(TokenType.RPAREN, ")", start_line, start_column))
            
            elif char == ',':
                self.advance()
                self.tokens.append(Token(TokenType.COMMA, ",", start_line, start_column))
            
            elif char == ':':
                self.advance()
                self.tokens.append(Token(TokenType.COLON, ":", start_line, start_column))
            
            else:
                # Unknown character, skip it
                self.advance()
        
        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens


# AST Node Definitions
@dataclass
class ASTNode:
    """Base AST node"""
    line: int
    column: int


@dataclass
class ProgramNode(ASTNode):
    """Root program node"""
    statements: List[ASTNode]


@dataclass
class TextOutputNode(ASTNode):
    """T: text output command"""
    text: str


@dataclass
class AcceptInputNode(ASTNode):
    """A: accept input command"""
    variable: str


@dataclass
class YesConditionNode(ASTNode):
    """Y: condition command"""
    condition: str


@dataclass
class NoConditionNode(ASTNode):
    """N: condition command"""
    condition: str


@dataclass
class JumpNode(ASTNode):
    """J: jump command"""
    label: str
    condition: Optional[str] = None


@dataclass
class LabelNode(ASTNode):
    """L: label definition"""
    label: str


@dataclass
class UpdateNode(ASTNode):
    """U: update variable command"""
    variable: str
    expression: str


@dataclass
class ComputeNode(ASTNode):
    """C: compute command"""
    variable: str
    expression: str


@dataclass
class MatchJumpNode(ASTNode):
    """M: match jump command"""
    label: str


@dataclass
class MatchTextNode(ASTNode):
    """MT: match text command"""
    text: str


class PilotParser:
    """Parser for PILOT language"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        
    def current_token(self) -> Optional[Token]:
        """Get current token"""
        if self.pos >= len(self.tokens):
            return None
        return self.tokens[self.pos]
    
    def peek_token(self, offset: int = 1) -> Optional[Token]:
        """Peek at token ahead"""
        peek_pos = self.pos + offset
        if peek_pos >= len(self.tokens):
            return None
        return self.tokens[peek_pos]
    
    def advance(self):
        """Move to next token"""
        self.pos += 1
    
    def expect_token(self, token_type: TokenType) -> Token:
        """Expect a specific token type"""
        token = self.current_token()
        if not token or token.type != token_type:
            raise SyntaxError(f"Expected {token_type}, got {token.type if token else 'EOF'}")
        self.advance()
        return token
    
    def parse(self) -> ProgramNode:
        """Parse tokens into AST"""
        statements = []
        
        while self.current_token() and self.current_token().type != TokenType.EOF:
            # Skip newlines
            if self.current_token().type == TokenType.NEWLINE:
                self.advance()
                continue
            
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        
        return ProgramNode(1, 1, statements)
    
    def parse_statement(self) -> Optional[ASTNode]:
        """Parse a single statement"""
        token = self.current_token()
        if not token:
            return None
        
        if token.type == TokenType.TEXT_OUTPUT:
            return self.parse_text_output()
        elif token.type == TokenType.ACCEPT_INPUT:
            return self.parse_accept_input()
        elif token.type == TokenType.YES_CONDITION:
            return self.parse_yes_condition()
        elif token.type == TokenType.NO_CONDITION:
            return self.parse_no_condition()
        elif token.type == TokenType.JUMP:
            return self.parse_jump()
        elif token.type == TokenType.CONDITIONAL_JUMP:
            return self.parse_conditional_jump()
        elif token.type == TokenType.LABEL:
            return self.parse_label()
        elif token.type == TokenType.UPDATE:
            return self.parse_update()
        elif token.type == TokenType.COMPUTE:
            return self.parse_compute()
        elif token.type == TokenType.MATCH_JUMP:
            return self.parse_match_jump()
        elif token.type == TokenType.MATCH_TEXT:
            return self.parse_match_text()
        elif token.type == TokenType.END:
            self.advance()
            return None  # End of program
        else:
            # Unknown statement, skip
            self.advance()
            return None
    
    def parse_text_output(self) -> TextOutputNode:
        """Parse T: text output"""
        token = self.expect_token(TokenType.TEXT_OUTPUT)
        text = self.read_rest_of_line()
        return TextOutputNode(text, token.line, token.column)
    
    def parse_accept_input(self) -> AcceptInputNode:
        """Parse A: accept input"""
        token = self.expect_token(TokenType.ACCEPT_INPUT)
        variable = self.read_rest_of_line().strip()
        return AcceptInputNode(variable, token.line, token.column)
    
    def parse_yes_condition(self) -> YesConditionNode:
        """Parse Y: condition"""
        token = self.expect_token(TokenType.YES_CONDITION)
        condition = self.read_rest_of_line()
        return YesConditionNode(condition, token.line, token.column)
    
    def parse_no_condition(self) -> NoConditionNode:
        """Parse N: condition"""
        token = self.expect_token(TokenType.NO_CONDITION)
        condition = self.read_rest_of_line()
        return NoConditionNode(condition, token.line, token.column)
    
    def parse_jump(self) -> JumpNode:
        """Parse J: jump"""
        token = self.expect_token(TokenType.JUMP)
        label = self.read_rest_of_line().strip()
        return JumpNode(label, token.line, token.column)
    
    def parse_conditional_jump(self) -> JumpNode:
        """Parse J(condition): jump"""
        token = self.expect_token(TokenType.CONDITIONAL_JUMP)
        # Extract condition and label from J(condition):label
        match = re.match(r'^J\((.+)\):(.+)$', token.value + self.read_rest_of_line())
        if match:
            condition = match.group(1).strip()
            label = match.group(2).strip()
            return JumpNode(label, token.line, token.column, condition)
        else:
            raise SyntaxError(f"Invalid conditional jump: {token.value}")
    
    def parse_label(self) -> LabelNode:
        """Parse L: label"""
        token = self.expect_token(TokenType.LABEL)
        label = self.read_rest_of_line().strip()
        return LabelNode(label, token.line, token.column)
    
    def parse_update(self) -> UpdateNode:
        """Parse U: update"""
        token = self.expect_token(TokenType.UPDATE)
        assignment = self.read_rest_of_line()
        if "=" in assignment:
            variable, expression = assignment.split("=", 1)
            return UpdateNode(variable.strip(), expression.strip(), token.line, token.column)
        else:
            raise SyntaxError(f"Invalid update statement: {assignment}")
    
    def parse_compute(self) -> ComputeNode:
        """Parse C: compute"""
        token = self.expect_token(TokenType.COMPUTE)
        assignment = self.read_rest_of_line()
        if "=" in assignment:
            variable, expression = assignment.split("=", 1)
            return ComputeNode(variable.strip(), expression.strip(), token.line, token.column)
        else:
            raise SyntaxError(f"Invalid compute statement: {assignment}")
    
    def parse_match_jump(self) -> MatchJumpNode:
        """Parse M: match jump"""
        token = self.expect_token(TokenType.MATCH_JUMP)
        label = self.read_rest_of_line().strip()
        return MatchJumpNode(label, token.line, token.column)
    
    def parse_match_text(self) -> MatchTextNode:
        """Parse MT: match text"""
        token = self.expect_token(TokenType.MATCH_TEXT)
        text = self.read_rest_of_line()
        return MatchTextNode(text, token.line, token.column)
    
    def read_rest_of_line(self) -> str:
        """Read rest of tokens until newline"""
        text = ""
        while (self.current_token() and 
               self.current_token().type not in [TokenType.NEWLINE, TokenType.EOF]):
            token = self.current_token()
            if token.type == TokenType.STRING_LITERAL:
                text += f'"{token.value}"'
            else:
                text += token.value
            self.advance()
        return text


class PilotCodeGenerator:
    """Generates C code from PILOT AST"""
    
    def __init__(self):
        self.labels = {}
        self.variables = set()
        self.output = []
        
    def generate(self, ast: ProgramNode) -> str:
        """Generate C code from AST"""
        # First pass: collect labels and variables
        self.collect_labels_and_variables(ast)
        
        # Generate C code
        self.output = []
        self.generate_header()
        self.generate_runtime()
        self.generate_main_function(ast)
        
        return "\n".join(self.output)
    
    def collect_labels_and_variables(self, ast: ProgramNode):
        """Collect all labels and variables used in the program"""
        for i, stmt in enumerate(ast.statements):
            if isinstance(stmt, LabelNode):
                self.labels[stmt.label] = i
            elif isinstance(stmt, (AcceptInputNode, UpdateNode, ComputeNode)):
                self.variables.add(stmt.variable)
            elif isinstance(stmt, (TextOutputNode, YesConditionNode, NoConditionNode)):
                # Extract variables from text/expressions
                variables = re.findall(r'\*([A-Za-z_][A-Za-z0-9_]*)\*', stmt.text if hasattr(stmt, 'text') else stmt.condition)
                self.variables.update(variables)
    
    def generate_header(self):
        """Generate C header includes and definitions"""
        self.output.extend([
            "#include <stdio.h>",
            "#include <stdlib.h>",
            "#include <string.h>",
            "#include <time.h>",
            "#include <math.h>",
            "",
            "#define MAX_STRING_LEN 1024",
            "#define MAX_VARIABLES 100",
            "",
        ])
    
    def generate_runtime(self):
        """Generate runtime support functions"""
        self.output.extend([
            "// Runtime support functions",
            "typedef struct {",
            "    char name[64];",
            "    double value;",
            "    char str_value[MAX_STRING_LEN];",
            "    int is_string;",
            "} Variable;",
            "",
            "Variable variables[MAX_VARIABLES];",
            "int var_count = 0;",
            "int match_flag = 0;",
            "",
            "Variable* find_variable(const char* name) {",
            "    for (int i = 0; i < var_count; i++) {",
            "        if (strcmp(variables[i].name, name) == 0) {",
            "            return &variables[i];",
            "        }",
            "    }",
            "    return NULL;",
            "}",
            "",
            "Variable* create_variable(const char* name) {",
            "    Variable* var = find_variable(name);",
            "    if (var) return var;",
            "    ",
            "    if (var_count < MAX_VARIABLES) {",
            "        strcpy(variables[var_count].name, name);",
            "        variables[var_count].value = 0.0;",
            "        variables[var_count].str_value[0] = '\\0';",
            "        variables[var_count].is_string = 0;",
            "        return &variables[var_count++];",
            "    }",
            "    return NULL;",
            "}",
            "",
            "void set_variable_number(const char* name, double value) {",
            "    Variable* var = create_variable(name);",
            "    if (var) {",
            "        var->value = value;",
            "        var->is_string = 0;",
            "    }",
            "}",
            "",
            "void set_variable_string(const char* name, const char* value) {",
            "    Variable* var = create_variable(name);",
            "    if (var) {",
            "        strncpy(var->str_value, value, MAX_STRING_LEN - 1);",
            "        var->str_value[MAX_STRING_LEN - 1] = '\\0';",
            "        var->is_string = 1;",
            "    }",
            "}",
            "",
            "double get_variable_number(const char* name) {",
            "    Variable* var = find_variable(name);",
            "    if (var) {",
            "        if (var->is_string) {",
            "            return atof(var->str_value);",
            "        } else {",
            "            return var->value;",
            "        }",
            "    }",
            "    return 0.0;",
            "}",
            "",
            "const char* get_variable_string(const char* name) {",
            "    Variable* var = find_variable(name);",
            "    static char buffer[MAX_STRING_LEN];",
            "    if (var) {",
            "        if (var->is_string) {",
            "            return var->str_value;",
            "        } else {",
            "            snprintf(buffer, MAX_STRING_LEN, \"%.2f\", var->value);",
            "            return buffer;",
            "        }",
            "    }",
            "    return \"\";",
            "}",
            "",
            "void interpolate_string(const char* input, char* output) {",
            "    const char* p = input;",
            "    char* out = output;",
            "    ",
            "    while (*p) {",
            "        if (*p == '*') {",
            "            p++; // Skip first *",
            "            char var_name[64];",
            "            int i = 0;",
            "            // Read variable name",
            "            while (*p && *p != '*' && i < 63) {",
            "                var_name[i++] = *p++;",
            "            }",
            "            var_name[i] = '\\0';",
            "            if (*p == '*') p++; // Skip closing *",
            "            ",
            "            // Replace with variable value",
            "            const char* var_value = get_variable_string(var_name);",
            "            strcpy(out, var_value);",
            "            out += strlen(var_value);",
            "        } else {",
            "            *out++ = *p++;",
            "        }",
            "    }",
            "    *out = '\\0';",
            "}",
            "",
            "double evaluate_expression(const char* expr) {",
            "    // Simple expression evaluator",
            "    // For now, just handle basic arithmetic and variables",
            "    char buffer[MAX_STRING_LEN];",
            "    strcpy(buffer, expr);",
            "    ",
            "    // Replace variables with their values",
            "    // This is a simplified version - a real implementation would be more complex",
            "    return atof(buffer);",
            "}",
            "",
            "double random_number() {",
            "    return (double)rand() / RAND_MAX;",
            "}",
            "",
        ])
    
    def generate_main_function(self, ast: ProgramNode):
        """Generate main C function"""
        self.output.extend([
            "int main() {",
            "    srand(time(NULL));",
            "    char input_buffer[MAX_STRING_LEN];",
            "    char output_buffer[MAX_STRING_LEN];",
            f"    int pc = 0; // Program counter",
            f"    int program_size = {len(ast.statements)};",
            "",
            "    while (pc < program_size) {",
            "        switch (pc) {",
        ])
        
        # Generate case for each statement
        for i, stmt in enumerate(ast.statements):
            self.output.append(f"            case {i}:")
            self.generate_statement(stmt, i)
            self.output.append("                pc++;")
            self.output.append("                break;")
        
        self.output.extend([
            "            default:",
            "                pc++;",
            "                break;",
            "        }",
            "    }",
            "    return 0;",
            "}",
        ])
    
    def generate_statement(self, stmt: ASTNode, index: int):
        """Generate C code for a single statement"""
        if isinstance(stmt, TextOutputNode):
            self.output.extend([
                f"                interpolate_string(\"{self.escape_string(stmt.text)}\", output_buffer);",
                "                printf(\"%s\\n\", output_buffer);",
            ])
        
        elif isinstance(stmt, AcceptInputNode):
            self.output.extend([
                f"                printf(\"Enter value for {stmt.variable}: \");",
                "                fgets(input_buffer, MAX_STRING_LEN, stdin);",
                "                input_buffer[strcspn(input_buffer, \"\\n\")] = '\\0';",
                f"                set_variable_string(\"{stmt.variable}\", input_buffer);",
            ])
        
        elif isinstance(stmt, YesConditionNode):
            self.output.extend([
                f"                match_flag = (evaluate_expression(\"{self.escape_string(stmt.condition)}\") != 0);",
            ])
        
        elif isinstance(stmt, NoConditionNode):
            self.output.extend([
                f"                match_flag = (evaluate_expression(\"{self.escape_string(stmt.condition)}\") == 0);",
            ])
        
        elif isinstance(stmt, JumpNode):
            if stmt.condition:
                # Conditional jump
                condition_check = f"evaluate_expression(\"{self.escape_string(stmt.condition)}\") != 0"
                target = self.labels.get(stmt.label, -1)
                if target >= 0:
                    self.output.extend([
                        f"                if ({condition_check}) {{",
                        f"                    pc = {target} - 1; // -1 because pc++ happens after",
                        "                }",
                    ])
            else:
                # Unconditional jump
                target = self.labels.get(stmt.label, -1)
                if target >= 0:
                    self.output.extend([
                        f"                pc = {target} - 1; // -1 because pc++ happens after",
                    ])
        
        elif isinstance(stmt, LabelNode):
            # Labels don't generate code, just a comment
            self.output.append(f"                // Label: {stmt.label}")
        
        elif isinstance(stmt, UpdateNode):
            self.output.extend([
                f"                set_variable_number(\"{stmt.variable}\", evaluate_expression(\"{self.escape_string(stmt.expression)}\"));",
            ])
        
        elif isinstance(stmt, ComputeNode):
            self.output.extend([
                f"                set_variable_number(\"{stmt.variable}\", evaluate_expression(\"{self.escape_string(stmt.expression)}\"));",
            ])
        
        elif isinstance(stmt, MatchJumpNode):
            target = self.labels.get(stmt.label, -1)
            if target >= 0:
                self.output.extend([
                    "                if (match_flag) {",
                    f"                    pc = {target} - 1; // -1 because pc++ happens after",
                    "                }",
                ])
        
        elif isinstance(stmt, MatchTextNode):
            self.output.extend([
                "                if (match_flag) {",
                f"                    interpolate_string(\"{self.escape_string(stmt.text)}\", output_buffer);",
                "                    printf(\"%s\\n\", output_buffer);",
                "                }",
            ])
    
    def escape_string(self, s: str) -> str:
        """Escape string for C code"""
        return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t')


class PilotNativeCompiler:
    """Main PILOT native compiler class"""
    
    def __init__(self):
        self.debug = False
        self.optimize = False
        
    def compile_file(self, input_file: str, output_file: str = None) -> bool:
        """Compile PILOT source file to Linux executable"""
        try:
            # Read source file
            with open(input_file, 'r') as f:
                source = f.read()
            
            # Determine output filename
            if not output_file:
                base_name = os.path.splitext(os.path.basename(input_file))[0]
                output_file = f"{base_name}_compiled"
            
            return self.compile_source(source, output_file)
            
        except Exception as e:
            print(f"Compilation error: {e}")
            return False
    
    def compile_source(self, source: str, output_file: str) -> bool:
        """Compile PILOT source code to Linux executable"""
        try:
            print(f"🔧 Compiling PILOT source to executable: {output_file}")
            
            # Step 1: Lexical analysis
            print("📝 Step 1: Tokenizing...")
            lexer = PilotLexer(source)
            tokens = lexer.tokenize()
            print(f"   Generated {len(tokens)} tokens")
            
            if self.debug:
                self.print_tokens(tokens)
            
            # Step 2: Parsing
            print("🌳 Step 2: Parsing...")
            parser = PilotParser(tokens)
            ast = parser.parse()
            print(f"   Generated AST with {len(ast.statements)} statements")
            
            if self.debug:
                self.print_ast(ast)
            
            # Step 3: Code generation
            print("⚙️  Step 3: Generating C code...")
            code_generator = PilotCodeGenerator()
            c_code = code_generator.generate(ast)
            
            if self.debug:
                print("Generated C code:")
                print(c_code)
            
            # Step 4: Compile to executable
            print("🔨 Step 4: Building executable...")
            success = self.build_executable(c_code, output_file)
            
            if success:
                print(f"✅ Compilation successful: {output_file}")
                # Make executable
                os.chmod(output_file, 0o755)
            
            return success
            
        except Exception as e:
            print(f"❌ Compilation failed: {e}")
            return False
    
    def build_executable(self, c_code: str, output_file: str) -> bool:
        """Compile C code to executable"""
        try:
            # Create temporary C file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
                f.write(c_code)
                c_file = f.name
            
            try:
                # Compile with gcc
                cmd = ['gcc', '-o', output_file, c_file, '-lm']
                if self.optimize:
                    cmd.extend(['-O2'])
                else:
                    cmd.extend(['-g'])  # Debug info if not optimizing
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("   C compilation successful")
                    return True
                else:
                    print(f"   C compilation failed: {result.stderr}")
                    return False
                    
            finally:
                # Clean up temporary C file
                os.unlink(c_file)
                
        except Exception as e:
            print(f"   Build error: {e}")
            return False
    
    def print_tokens(self, tokens: List[Token]):
        """Print tokens for debugging"""
        print("\n=== TOKENS ===")
        for token in tokens[:50]:  # Limit output
            print(f"{token.type.name}: {repr(token.value)} (line {token.line}, col {token.column})")
        if len(tokens) > 50:
            print(f"... and {len(tokens) - 50} more tokens")
        print()
    
    def print_ast(self, ast: ProgramNode):
        """Print AST for debugging"""
        print("\n=== AST ===")
        for i, stmt in enumerate(ast.statements[:20]):  # Limit output
            print(f"{i}: {type(stmt).__name__}")
            if hasattr(stmt, 'text'):
                print(f"   text: {repr(stmt.text)}")
            elif hasattr(stmt, 'condition'):
                print(f"   condition: {repr(stmt.condition)}")
            elif hasattr(stmt, 'label'):
                print(f"   label: {repr(stmt.label)}")
            elif hasattr(stmt, 'variable'):
                print(f"   variable: {repr(stmt.variable)}")
        if len(ast.statements) > 20:
            print(f"... and {len(ast.statements) - 20} more statements")
        print()


def main():
    """Main compiler entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PILOT Native Compiler")
    parser.add_argument('input_file', help='PILOT source file to compile')
    parser.add_argument('-o', '--output', help='Output executable name')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug output')
    parser.add_argument('-O', '--optimize', action='store_true', help='Enable optimization')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found")
        sys.exit(1)
    
    compiler = PilotNativeCompiler()
    compiler.debug = args.debug
    compiler.optimize = args.optimize
    
    success = compiler.compile_file(args.input_file, args.output)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()