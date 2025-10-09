"""
JAMES III Compiler/Interpreter
Main interface for compiling and executing JAMES III programs
"""

import os
import sys
from typing import List, Optional, Dict, Any, Callable, Union
from .lexer import JAMESLexer, Token
from .parser import JAMESParser, ProgramNode
from .interpreter import JAMESInterpreter
from .handlers.pilot_handler import PilotHandler
from .handlers.logo_handler import LogoHandler
from .handlers.python_handler import PythonHandler, BasicHandler

class JAMESCompiler:
    """Main JAMES III compiler/interpreter"""
    
    def __init__(self):
        self.lexer = JAMESLexer()
        self.parser = JAMESParser()
        self.interpreter = JAMESInterpreter()
        
        # Initialize handlers
        self.pilot_handler = PilotHandler(self.interpreter)
        self.logo_handler = LogoHandler(self.interpreter)
        self.python_handler = PythonHandler(self.interpreter)
        self.basic_handler = BasicHandler(self.interpreter)
        
        # Replace interpreter's command handlers with specialized ones
        self._setup_handlers()
        
        # Compilation options
        self.debug_mode = False
        self.optimize = False
        
    def _setup_handlers(self):
        """Setup specialized command handlers in the interpreter"""
        # Override PILOT command execution
        original_pilot_execute = self.interpreter.execute_PilotCommandNode
        def enhanced_pilot_execute(node):
            return self.pilot_handler.execute_command(node)
        self.interpreter.execute_PilotCommandNode = enhanced_pilot_execute
        
        # Override Logo command execution
        original_logo_execute = self.interpreter.execute_LogoCommandNode
        def enhanced_logo_execute(node):
            return self.logo_handler.execute_command(node)
        self.interpreter.execute_LogoCommandNode = enhanced_logo_execute
        
        # Override Python block execution
        original_python_execute = self.interpreter.execute_PythonBlockNode
        def enhanced_python_execute(node):
            return self.python_handler.execute_python_block(node)
        self.interpreter.execute_PythonBlockNode = enhanced_python_execute
    
    def compile_file(self, filename: str) -> ProgramNode:
        """Compile a JAMES file to AST"""
        if not filename.endswith('.james'):
            raise ValueError("JAMES files must have .james extension")
        
        if not os.path.exists(filename):
            raise FileNotFoundError(f"File not found: {filename}")
        
        with open(filename, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        return self.compile_string(source_code)
    
    def compile_string(self, source_code: str) -> ProgramNode:
        """Compile JAMES source code to AST"""
        try:
            # Lexical analysis
            tokens = self.lexer.tokenize(source_code)
            
            if self.debug_mode:
                self._print_tokens(tokens)
            
            # Parsing
            ast = self.parser.parse(tokens)
            
            if self.debug_mode:
                self._print_ast(ast)
            
            # Optimization (if enabled)
            if self.optimize:
                ast = self._optimize_ast(ast)
            
            return ast
            
        except Exception as e:
            raise RuntimeError(f"Compilation error: {e}")
    
    def execute_file(self, filename: str, input_callback: Optional[Callable[[str], str]] = None) -> List[str]:
        """Execute a JAMES file"""
        ast = self.compile_file(filename)
        return self.execute_ast(ast, input_callback)
    
    def execute_string(self, source_code: str, input_callback: Optional[Callable[[str], str]] = None) -> List[str]:
        """Execute JAMES source code"""
        ast = self.compile_string(source_code)
        return self.execute_ast(ast, input_callback)
    
    def execute_ast(self, ast: ProgramNode, input_callback: Optional[Callable[[str], str]] = None) -> List[str]:
        """Execute a compiled AST"""
        try:
            # Set input callback
            if input_callback:
                self.interpreter.set_input_callback(input_callback)
                self.pilot_handler.set_callbacks(
                    lambda text: self.interpreter.output_buffer.append(text),
                    input_callback
                )
            
            # Execute the program
            output = self.interpreter.interpret(ast)
            
            return output
            
        except Exception as e:
            return [f"Runtime error: {e}"]
    
    def interactive_mode(self):
        """Start interactive JAMES interpreter"""
        print("JAMES III Interactive Interpreter")
        print("Type 'EXIT' to quit, 'HELP' for help")
        print()
        
        while True:
            try:
                line = input("JAMES> ").strip()
                
                if line.upper() == 'EXIT':
                    break
                elif line.upper() == 'HELP':
                    self._print_help()
                    continue
                elif line.upper() == 'VARS':
                    self._print_variables()
                    continue
                elif line.upper() == 'CLEAR':
                    self._clear_environment()
                    continue
                elif not line:
                    continue
                
                # Execute the line
                output = self.execute_string(line)
                for line_output in output:
                    print(line_output)
                    
            except KeyboardInterrupt:
                print("\\nUse EXIT to quit")
            except Exception as e:
                print(f"Error: {e}")
    
    def set_debug_mode(self, debug: bool):
        """Enable/disable debug mode"""
        self.debug_mode = debug
    
    def set_optimization(self, optimize: bool):
        """Enable/disable optimization"""
        self.optimize = optimize
    
    def reset(self):
        """Reset all handlers and interpreter state"""
        self.interpreter = JAMESInterpreter()
        self.pilot_handler.reset()
        self.logo_handler.reset()
        self.python_handler.reset()
        self.basic_handler.reset()
        self._setup_handlers()
    
    def _print_tokens(self, tokens: List[Token]):
        """Print tokens for debugging"""
        print("=== TOKENS ===")
        for token in tokens:
            print(f"{token.type.name}: {repr(token.value)} (line {token.line}, col {token.column})")
        print()
    
    def _print_ast(self, ast: ProgramNode):
        """Print AST for debugging"""
        print("=== AST ===")
        self._print_ast_node(ast, 0)
        print()
    
    def _print_ast_node(self, node, indent):
        """Recursively print AST node"""
        spaces = "  " * indent
        print(f"{spaces}{type(node).__name__}")
        
        for attr_name in dir(node):
            if not attr_name.startswith('_') and attr_name not in ['line', 'column']:
                attr_value = getattr(node, attr_name)
                if hasattr(attr_value, '__iter__') and not isinstance(attr_value, str):
                    if attr_value:  # Not empty
                        print(f"{spaces}  {attr_name}:")
                        for item in attr_value:
                            if hasattr(item, 'line'):  # It's an AST node
                                self._print_ast_node(item, indent + 2)
                            else:
                                print(f"{spaces}    {repr(item)}")
                elif hasattr(attr_value, 'line'):  # It's an AST node
                    print(f"{spaces}  {attr_name}:")
                    self._print_ast_node(attr_value, indent + 2)
                elif attr_value is not None:
                    print(f"{spaces}  {attr_name}: {repr(attr_value)}")
    
    def _optimize_ast(self, ast: ProgramNode) -> ProgramNode:
        """Optimize AST (placeholder)"""
        # TODO: Implement optimizations like:
        # - Constant folding
        # - Dead code elimination
        # - Loop optimization
        return ast
    
    def _print_help(self):
        """Print help for interactive mode"""
        print("""
JAMES III Interactive Help:
- EXIT: Quit the interpreter
- HELP: Show this help
- VARS: Show all variables
- CLEAR: Clear all variables and reset state

JAMES III supports:
- BASIC: LET X = 10, PRINT X, IF...THEN...ELSE, FOR...NEXT, WHILE...WEND
- PILOT: T: Type text, A: Accept input, M: Match patterns
- Logo: FORWARD 100, RIGHT 90, PENUP, PENDOWN, HOME
- Python: PYTHON: ... END_PYTHON blocks

Examples:
  PRINT "Hello, World!"
  LET X = 10 * 5
  FOR I = 1 TO 10: PRINT I: NEXT I
  T: Hello from PILOT
  FORWARD 100: RIGHT 90
        """)
    
    def _print_variables(self):
        """Print all variables"""
        print("=== VARIABLES ===")
        if self.interpreter.environment.variables:
            for name, value in self.interpreter.environment.variables.items():
                print(f"{name} = {repr(value)}")
        else:
            print("No variables defined")
        print()
    
    def _clear_environment(self):
        """Clear environment"""
        self.reset()
        print("Environment cleared")

def main():
    """Main entry point for JAMES III"""
    import argparse
    
    parser = argparse.ArgumentParser(description="JAMES III Programming Language")
    parser.add_argument('file', nargs='?', help='JAMES file to execute')
    parser.add_argument('-i', '--interactive', action='store_true', help='Start interactive mode')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('-O', '--optimize', action='store_true', help='Enable optimization')
    
    args = parser.parse_args()
    
    compiler = JAMESCompiler()
    
    if args.debug:
        compiler.set_debug_mode(True)
    
    if args.optimize:
        compiler.set_optimization(True)
    
    if args.file:
        try:
            output = compiler.execute_file(args.file)
            for line in output:
                print(line)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.interactive:
        compiler.interactive_mode()
    else:
        compiler.interactive_mode()

if __name__ == '__main__':
    main()