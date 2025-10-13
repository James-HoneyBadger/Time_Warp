"""
TW Forth Language Executor
==========================

Implements TW Forth, an educational variant of the Forth stack-based programming
language for the Time_Warp IDE, emphasizing postfix notation and stack manipulation.

Language Features:
- Stack manipulation: DUP, DROP, SWAP, ROT, OVER, NIP, TUCK
- Arithmetic: +, -, *, /, MOD, /MOD, MIN, MAX, ABS, NEGATE
- Comparison: =, <, >, <=, >=, 0=, 0<, 0>
- Bitwise operations: AND, OR, XOR, INVERT
- Control structures: IF/THEN/ELSE, BEGIN/UNTIL, BEGIN/WHILE/REPEAT, DO/LOOP
- Word definition: : (colon) to define new words, ; (semicolon) to end
- Variables: VARIABLE to create named storage locations
- Constants: CONSTANT to define named values
- Comments: ( for line comments, \\ for end-of-line comments
- I/O: . (dot) to print, .S to show stack, CR for newline, EMIT for characters
- Strings: S" for string literals
- Math functions: SIN, COS, TAN, SQRT, LOG, EXP

The executor provides a stack-based programming environment where operations
work on data items pushed onto and popped from a parameter stack.
"""

import re
import math


class TwForthExecutor:
    """Handles TW Forth language command execution"""

    def __init__(self, interpreter):
        """Initialize with reference to main interpreter"""
        self.interpreter = interpreter
        self.data_stack = []  # Main data stack
        self.return_stack = []  # Return stack for control structures
        self.dictionary = {}  # User-defined words
        self.variables = {}  # Variables
        self.constants = {}  # Constants
        self.compiling = False  # Are we in compile mode?
        self.current_word = None  # Word being defined
        self.word_definition = []  # Words being compiled
        self.if_depth = 0  # Nested IF depth
        self.loop_depth = 0  # Nested loop depth

        # Initialize built-in words
        self._init_builtin_words()

    def _init_builtin_words(self):
        """Initialize built-in Forth words"""
        self.dictionary.update(
            {
                # Stack manipulation
                "DUP": lambda: self._dup(),
                "DROP": lambda: self._drop(),
                "SWAP": lambda: self._swap(),
                "OVER": lambda: self._over(),
                "ROT": lambda: self._rot(),
                "NIP": lambda: self._nip(),
                "TUCK": lambda: self._tuck(),
                # Arithmetic
                "+": lambda: self._add(),
                "-": lambda: self._sub(),
                "*": lambda: self._mul(),
                "/": lambda: self._div(),
                "MOD": lambda: self._mod(),
                "NEGATE": lambda: self._negate(),
                "ABS": lambda: self._abs(),
                "MIN": lambda: self._min(),
                "MAX": lambda: self._max(),
                # Comparison
                "=": lambda: self._equal(),
                "<": lambda: self._less(),
                ">": lambda: self._greater(),
                "<=": lambda: self._less_equal(),
                ">=": lambda: self._greater_equal(),
                "<>": lambda: self._not_equal(),
                # Logic
                "AND": lambda: self._and(),
                "OR": lambda: self._or(),
                "XOR": lambda: self._xor(),
                "INVERT": lambda: self._invert(),
                # I/O
                ".": lambda: self._dot(),
                ".S": lambda: self._dot_s(),
                '."': lambda: self._dot_quote(),
                "CR": lambda: self._cr(),
                "EMIT": lambda: self._emit(),
                "SPACES": lambda: self._spaces(),
                # Math functions
                "SIN": lambda: self._sin(),
                "COS": lambda: self._cos(),
                "TAN": lambda: self._tan(),
                "SQRT": lambda: self._sqrt(),
                "LOG": lambda: self._log(),
                "EXP": lambda: self._exp(),
                # Stack queries
                "DEPTH": lambda: self._depth(),
                "PICK": lambda: self._pick(),
                "ROLL": lambda: self._roll(),
                # Constants
                "TRUE": lambda: self.data_stack.append(-1),
                "FALSE": lambda: self.data_stack.append(0),
                "PI": lambda: self.data_stack.append(math.pi),
                "E": lambda: self.data_stack.append(math.e),
            }
        )

    def execute_command(self, command):
        """Execute a Forth command and return the result"""
        try:
            command = command.strip()
            if not command:
                return "continue"

            # Split command into words
            words = self._tokenize(command)

            for word in words:
                if not self._execute_word(word):
                    return "continue"

            return "continue"

        except Exception as e:
            self.interpreter.debug_output(f"Forth command error: {e}")
            return "continue"

    def _tokenize(self, command):
        """Tokenize Forth command into words"""
        # Handle comments first
        command = re.sub(r"\(.*?\)", "", command)  # Remove ( comments )

        # Handle .\" strings specially
        command = re.sub(r"\.\"([^\"]*?)\"", r'."\1"', command)

        # Split on whitespace, keeping quoted strings together
        tokens = []
        current_token = ""
        in_string = False

        for char in command:
            if char == '"' and not in_string:
                in_string = True
                current_token += char
            elif char == '"' and in_string:
                in_string = False
                current_token += char
                tokens.append(current_token)
                current_token = ""
            elif char.isspace() and not in_string:
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
            else:
                current_token += char

        if current_token:
            tokens.append(current_token)

        return tokens

    def _execute_word(self, word):
        """Execute a single Forth word"""
        try:
            # Handle numbers
            if self._is_number(word):
                if self.compiling:
                    self.word_definition.append(word)
                else:
                    self.data_stack.append(self._parse_number(word))
                return True

            # Handle strings
            if word.startswith('"') and word.endswith('"'):
                if self.compiling:
                    self.word_definition.append(word)
                else:
                    self.data_stack.append(word[1:-1])  # Remove quotes
                return True

            # Handle word definition start
            if word == ":":
                self.compiling = True
                self.word_definition = []
                self.current_word = None
                return True

            # If compiling and we don't have a word name yet, this is the word name
            if self.compiling and self.current_word is None:
                self.current_word = word
                return True

            # Handle word definition end
            if word == ";":
                self._end_word_definition()
                return True

            # Handle control structures
            if word == "IF":
                return self._handle_if()
            elif word == "THEN":
                return self._handle_then()
            elif word == "ELSE":
                return self._handle_else()
            elif word == "BEGIN":
                return self._handle_begin()
            elif word == "UNTIL":
                return self._handle_until()
            elif word == "WHILE":
                return self._handle_while()
            elif word == "REPEAT":
                return self._handle_repeat()
            elif word == "RECURSE":
                return self._recurse()

            # Handle variable operations
            if word == "VARIABLE":
                return self._handle_variable()
            elif word == "CONSTANT":
                return self._handle_constant()
            elif word == "!":
                return self._store()
            elif word == "@":
                return self._fetch()

            # Execute built-in or user-defined word
            if word in self.dictionary:
                if self.compiling:
                    self.word_definition.append(word)
                else:
                    result = self.dictionary[word]()
                    if result is False:  # Word execution failed
                        return False
                return True

            # Unknown word
            self.interpreter.log_output(f"Unknown word: {word}")
            return False

        except Exception as e:
            self.interpreter.debug_output(f"Word execution error: {e}")
            return False

    def _is_number(self, word):
        """Check if word is a number"""
        try:
            self._parse_number(word)
            return True
        except ValueError:
            return False

    def _parse_number(self, word):
        """Parse a number from string"""
        if "." in word:
            return float(word)
        else:
            return int(word)

    def _end_word_definition(self):
        """End word definition and store it"""
        if self.compiling and self.current_word:
            self.dictionary[self.current_word] = self._create_word_function(
                self.word_definition
            )
            self.interpreter.log_output(f"Defined word: {self.current_word}")
            self.compiling = False
            self.current_word = None
            self.word_definition = []
        else:
            self.interpreter.log_output("Error: Not in word definition")

    def _create_word_function(self, definition):
        """Create a function from word definition"""

        def word_func():
            for word in definition:
                if not self._execute_word(word):
                    return False
            return True

        return word_func

    # Stack manipulation words
    def _dup(self):
        """Duplicate top of stack"""
        if len(self.data_stack) < 1:
            self.interpreter.log_output("Stack underflow in DUP")
            return False
        self.data_stack.append(self.data_stack[-1])
        return True

    def _drop(self):
        """Drop top of stack"""
        if len(self.data_stack) < 1:
            self.interpreter.log_output("Stack underflow in DROP")
            return False
        self.data_stack.pop()
        return True

    def _swap(self):
        """Swap top two stack items"""
        if len(self.data_stack) < 2:
            self.interpreter.log_output("Stack underflow in SWAP")
            return False
        self.data_stack[-1], self.data_stack[-2] = (
            self.data_stack[-2],
            self.data_stack[-1],
        )
        return True

    def _over(self):
        """Copy second item to top"""
        if len(self.data_stack) < 2:
            self.interpreter.log_output("Stack underflow in OVER")
            return False
        self.data_stack.append(self.data_stack[-2])
        return True

    def _rot(self):
        """Rotate top three items"""
        if len(self.data_stack) < 3:
            self.interpreter.log_output("Stack underflow in ROT")
            return False
        a, b, c = self.data_stack[-3], self.data_stack[-2], self.data_stack[-1]
        self.data_stack[-3], self.data_stack[-2], self.data_stack[-1] = b, c, a
        return True

    def _nip(self):
        """Remove second item"""
        if len(self.data_stack) < 2:
            self.interpreter.log_output("Stack underflow in NIP")
            return False
        self.data_stack[-2] = self.data_stack[-1]
        self.data_stack.pop()
        return True

    def _tuck(self):
        """Copy top item under second item"""
        if len(self.data_stack) < 2:
            self.interpreter.log_output("Stack underflow in TUCK")
            return False
        top = self.data_stack[-1]
        self.data_stack.insert(-1, top)
        return True

    # Arithmetic operations
    def _add(self):
        if len(self.data_stack) < 2:
            self.interpreter.log_output("Stack underflow in +")
            return False
        b, a = self.data_stack.pop(), self.data_stack.pop()
        self.data_stack.append(a + b)
        return True

    def _sub(self):
        if len(self.data_stack) < 2:
            self.interpreter.log_output("Stack underflow in -")
            return False
        b, a = self.data_stack.pop(), self.data_stack.pop()
        self.data_stack.append(a - b)
        return True

    def _mul(self):
        if len(self.data_stack) < 2:
            self.interpreter.log_output("Stack underflow in *")
            return False
        b, a = self.data_stack.pop(), self.data_stack.pop()
        self.data_stack.append(a * b)
        return True

    def _div(self):
        if len(self.data_stack) < 2:
            self.interpreter.log_output("Stack underflow in /")
            return False
        b, a = self.data_stack.pop(), self.data_stack.pop()
        if b == 0:
            self.interpreter.log_output("Division by zero")
            return False
        self.data_stack.append(a / b)
        return True

    def _mod(self):
        if len(self.data_stack) < 2:
            self.interpreter.log_output("Stack underflow in MOD")
            return False
        b, a = self.data_stack.pop(), self.data_stack.pop()
        self.data_stack.append(a % b)
        return True

    def _negate(self):
        if len(self.data_stack) < 1:
            self.interpreter.log_output("Stack underflow in NEGATE")
            return False
        self.data_stack[-1] = -self.data_stack[-1]
        return True

    def _abs(self):
        if len(self.data_stack) < 1:
            self.interpreter.log_output("Stack underflow in ABS")
            return False
        self.data_stack[-1] = abs(self.data_stack[-1])
        return True

    def _min(self):
        if len(self.data_stack) < 2:
            self.interpreter.log_output("Stack underflow in MIN")
            return False
        b, a = self.data_stack.pop(), self.data_stack.pop()
        self.data_stack.append(min(a, b))
        return True

    def _max(self):
        if len(self.data_stack) < 2:
            self.interpreter.log_output("Stack underflow in MAX")
            return False
        b, a = self.data_stack.pop(), self.data_stack.pop()
        self.data_stack.append(max(a, b))
        return True

    # Comparison operations
    def _equal(self):
        if len(self.data_stack) < 2:
            self.interpreter.log_output("Stack underflow in =")
            return False
        b, a = self.data_stack.pop(), self.data_stack.pop()
        self.data_stack.append(-1 if a == b else 0)
        return True

    def _less(self):
        if len(self.data_stack) < 2:
            self.interpreter.log_output("Stack underflow in <")
            return False
        b, a = self.data_stack.pop(), self.data_stack.pop()
        self.data_stack.append(-1 if a < b else 0)
        return True

    def _greater(self):
        if len(self.data_stack) < 2:
            self.interpreter.log_output("Stack underflow in >")
            return False
        b, a = self.data_stack.pop(), self.data_stack.pop()
        self.data_stack.append(-1 if a > b else 0)
        return True

    def _less_equal(self):
        if len(self.data_stack) < 2:
            self.interpreter.log_output("Stack underflow in <=")
            return False
        b, a = self.data_stack.pop(), self.data_stack.pop()
        self.data_stack.append(-1 if a <= b else 0)
        return True

    def _greater_equal(self):
        if len(self.data_stack) < 2:
            self.interpreter.log_output("Stack underflow in >=")
            return False
        b, a = self.data_stack.pop(), self.data_stack.pop()
        self.data_stack.append(-1 if a >= b else 0)
        return True

    def _not_equal(self):
        if len(self.data_stack) < 2:
            self.interpreter.log_output("Stack underflow in <>")
            return False
        b, a = self.data_stack.pop(), self.data_stack.pop()
        self.data_stack.append(-1 if a != b else 0)
        return True

    # Logic operations
    def _and(self):
        if len(self.data_stack) < 2:
            self.interpreter.log_output("Stack underflow in AND")
            return False
        b, a = self.data_stack.pop(), self.data_stack.pop()
        self.data_stack.append(a & b)
        return True

    def _or(self):
        if len(self.data_stack) < 2:
            self.interpreter.log_output("Stack underflow in OR")
            return False
        b, a = self.data_stack.pop(), self.data_stack.pop()
        self.data_stack.append(a | b)
        return True

    def _xor(self):
        if len(self.data_stack) < 2:
            self.interpreter.log_output("Stack underflow in XOR")
            return False
        b, a = self.data_stack.pop(), self.data_stack.pop()
        self.data_stack.append(a ^ b)
        return True

    def _invert(self):
        if len(self.data_stack) < 1:
            self.interpreter.log_output("Stack underflow in INVERT")
            return False
        self.data_stack[-1] = ~self.data_stack[-1]
        return True

    # I/O operations
    def _dot(self):
        """Print top of stack"""
        if len(self.data_stack) < 1:
            self.interpreter.log_output("Stack underflow in .")
            return False
        value = self.data_stack.pop()
        self.interpreter.log_output(str(value))
        return True

    def _dot_s(self):
        """Show stack contents"""
        if self.data_stack:
            stack_str = " ".join(str(x) for x in self.data_stack)
            self.interpreter.log_output(f"<{len(self.data_stack)}> {stack_str}")
        else:
            self.interpreter.log_output("<0>")
        return True

    def _cr(self):
        """Carriage return"""
        self.interpreter.log_output("")
        return True

    def _emit(self):
        """Emit character"""
        if len(self.data_stack) < 1:
            self.interpreter.log_output("Stack underflow in EMIT")
            return False
        char_code = self.data_stack.pop()
        self.interpreter.log_output(chr(char_code))
        return True

    def _dot_quote(self):
        """Print string literal (.")"""
        # This is handled during tokenization - strings are already processed
        self.interpreter.log_output("." + " not implemented in this context")
        return True

    def _spaces(self):
        """Print n spaces"""
        if len(self.data_stack) < 1:
            self.interpreter.log_output("Stack underflow in SPACES")
            return False
        n = self.data_stack.pop()
        self.interpreter.log_output(" " * n)
        return True

    # Math functions
    def _sin(self):
        if len(self.data_stack) < 1:
            self.interpreter.log_output("Stack underflow in SIN")
            return False
        angle = math.radians(self.data_stack.pop())
        self.data_stack.append(math.sin(angle))
        return True

    def _cos(self):
        if len(self.data_stack) < 1:
            self.interpreter.log_output("Stack underflow in COS")
            return False
        angle = math.radians(self.data_stack.pop())
        self.data_stack.append(math.cos(angle))
        return True

    def _tan(self):
        if len(self.data_stack) < 1:
            self.interpreter.log_output("Stack underflow in TAN")
            return False
        angle = math.radians(self.data_stack.pop())
        self.data_stack.append(math.tan(angle))
        return True

    def _sqrt(self):
        if len(self.data_stack) < 1:
            self.interpreter.log_output("Stack underflow in SQRT")
            return False
        value = self.data_stack.pop()
        if value < 0:
            self.interpreter.log_output("Cannot take square root of negative number")
            return False
        self.data_stack.append(math.sqrt(value))
        return True

    def _log(self):
        if len(self.data_stack) < 1:
            self.interpreter.log_output("Stack underflow in LOG")
            return False
        value = self.data_stack.pop()
        if value <= 0:
            self.interpreter.log_output("Cannot take log of non-positive number")
            return False
        self.data_stack.append(math.log(value))
        return True

    def _exp(self):
        if len(self.data_stack) < 1:
            self.interpreter.log_output("Stack underflow in EXP")
            return False
        self.data_stack.append(math.exp(self.data_stack.pop()))
        return True

    # Stack queries
    def _depth(self):
        """Push stack depth"""
        self.data_stack.append(len(self.data_stack))
        return True

    def _pick(self):
        """Pick nth item from stack"""
        if len(self.data_stack) < 1:
            self.interpreter.log_output("Stack underflow in PICK")
            return False
        n = self.data_stack.pop()
        if n < 0 or n >= len(self.data_stack):
            self.interpreter.log_output("Invalid PICK index")
            return False
        self.data_stack.append(self.data_stack[-n - 1])
        return True

    def _roll(self):
        """Roll nth item to top"""
        if len(self.data_stack) < 1:
            self.interpreter.log_output("Stack underflow in ROLL")
            return False
        n = self.data_stack.pop()
        if n < 0 or n >= len(self.data_stack):
            self.interpreter.log_output("Invalid ROLL index")
            return False
        item = self.data_stack[-n - 1]
        del self.data_stack[-n - 1]
        self.data_stack.append(item)
        return True

    # Control structures
    def _handle_if(self):
        """Handle IF"""
        if len(self.data_stack) < 1:
            self.interpreter.log_output("Stack underflow in IF")
            return False

        condition = self.data_stack.pop()
        if condition == 0:  # False
            # Skip to ELSE or THEN
            self.return_stack.append("IF_SKIP")
        else:
            self.return_stack.append("IF_EXEC")
        return True

    def _handle_then(self):
        """Handle THEN"""
        if self.return_stack and self.return_stack[-1].startswith("IF"):
            self.return_stack.pop()
        return True

    def _handle_else(self):
        """Handle ELSE"""
        if self.return_stack and self.return_stack[-1] == "IF_EXEC":
            self.return_stack[-1] = "IF_SKIP"
        elif self.return_stack and self.return_stack[-1] == "IF_SKIP":
            self.return_stack[-1] = "IF_EXEC"
        return True

    def _handle_begin(self):
        """Handle BEGIN"""
        self.return_stack.append("BEGIN")
        return True

    def _handle_until(self):
        """Handle UNTIL"""
        if len(self.data_stack) < 1:
            self.interpreter.log_output("Stack underflow in UNTIL")
            return False

        condition = self.data_stack.pop()
        if condition == 0:  # False, continue loop
            # Would need to jump back to BEGIN - simplified for now
            pass
        else:  # True, exit loop
            if self.return_stack and self.return_stack[-1] == "BEGIN":
                self.return_stack.pop()
        return True

    def _handle_while(self):
        """Handle WHILE"""
        if len(self.data_stack) < 1:
            self.interpreter.log_output("Stack underflow in WHILE")
            return False

        condition = self.data_stack.pop()
        if condition == 0:  # False
            # Skip to REPEAT
            self.return_stack.append("WHILE_SKIP")
        else:
            self.return_stack.append("WHILE_EXEC")
        return True

    def _handle_repeat(self):
        """Handle REPEAT"""
        if self.return_stack and self.return_stack[-1].startswith("WHILE"):
            self.return_stack.pop()
        return True

    def _recurse(self):
        """Handle RECURSE - call the current word being defined"""
        if (
            self.compiling
            and self.current_word
            and self.current_word in self.dictionary
        ):
            # Call the current word recursively
            return self.dictionary[self.current_word]()
        else:
            self.interpreter.log_output(
                "RECURSE can only be used inside word definitions"
            )
            return False

    # Variables and constants
    def _handle_variable(self):
        """Handle VARIABLE declaration"""
        # In a real Forth, this would allocate memory
        # For simplicity, we'll just create a named storage location
        self.interpreter.log_output("VARIABLE not fully implemented")
        return True

    def _handle_constant(self):
        """Handle CONSTANT declaration"""
        if len(self.data_stack) < 1:
            self.interpreter.log_output("Stack underflow in CONSTANT")
            return False
        # Would need to get constant name - simplified
        self.interpreter.log_output("CONSTANT not fully implemented")
        return True

    def _store(self):
        """Store value (!)"""
        self.interpreter.log_output("! (store) not implemented")
        return True

    def _fetch(self):
        """Fetch value (@)"""
        self.interpreter.log_output("@ (fetch) not implemented")
        return True
