"""
TW BASIC Language Executor
==========================

Implements TW BASIC (Time_Warp Beginner's All-purpose Symbolic Instruction Code),
an educational variant of the classic BASIC programming language for the Time_Warp IDE.

Language Features:
- Variable assignment with LET or direct assignment
- Text output with PRINT
- User input with INPUT
- Control structures: IF/THEN/ELSE, FOR/NEXT loops, GOTO, GOSUB/RETURN
- Mathematical functions: SIN, COS, TAN, SQRT, ABS, INT, RND
- String operations: LEN, MID, LEFT, RIGHT, INSTR, STR$, VAL
- Array operations: DIM, SORT, FIND, SUM, AVG, MIN, MAX
- File I/O: OPEN, CLOSE, READ, WRITE, EOF
- Graphics commands: LINE, BOX, TRIANGLE, ELLIPSE, FILL (with pygame)
- Sound commands: BEEP, PLAY, SOUND, NOTE
- Comments with REM

The executor supports both traditional line-numbered BASIC programs and
modern structured BASIC code. It integrates with pygame for graphics when available,
falling back to text-based output otherwise.
"""

import re
import time
import math
import random


class TwBasicExecutor:
    """
    Executor for TW BASIC programming language commands.

    Handles parsing and execution of BASIC statements including variable assignment,
    control flow, mathematical operations, and graphics commands. Supports both
    traditional line-numbered syntax and modern structured programming.

    The executor can optionally use pygame for graphics rendering when available,
    providing visual output for drawing commands.
    """

    def __init__(self, interpreter):
        """
        Initialize the BASIC executor.

        Args:
            interpreter: Reference to the main Time_WarpInterpreter instance
        """
        self.interpreter = interpreter
        self.pygame_screen = None
        self.pygame_clock = None
        self.current_color = (255, 255, 255)  # White default

    def _init_pygame_graphics(self, width, height, title):
        """
        Initialize pygame graphics for standalone mode.

        Attempts to create a pygame window for graphics output. If pygame is not
        available or display is not accessible, falls back to text-based operation.

        Args:
            width (int): Window width in pixels
            height (int): Window height in pixels
            title (str): Window title

        Returns:
            bool: True if pygame initialized successfully, False otherwise
        """
        try:
            import pygame
            import os

            # Check if display is available
            display = os.environ.get("DISPLAY")
            self.interpreter.log_output(f"🖥️  Display environment: {display}")

            pygame.init()

            # Check available drivers
            drivers = pygame.display.get_driver()
            self.interpreter.log_output(f"🎮 Pygame video driver: {drivers}")

            self.pygame_screen = pygame.display.set_mode((width, height))
            pygame.display.set_caption(title)
            self.pygame_clock = pygame.time.Clock()
            self.pygame_screen.fill((0, 0, 0))  # Black background
            pygame.display.flip()

            self.interpreter.log_output(
                f"✅ Pygame window created: {width}x{height} '{title}'"
            )
            return True
        except ImportError:
            self.interpreter.log_output("❌ Error: pygame not available for graphics")
            return False
        except Exception as e:
            self.interpreter.log_output(f"❌ Error initializing pygame: {e}")
            return False

    def execute_command(self, command):
        """
        Execute a BASIC command and return the execution result.

        Parses the command and routes it to the appropriate handler method
        based on the command keyword.

        Args:
            command (str): The BASIC command to execute

        Returns:
            str: Execution result ("continue", "end", or jump target)
        """
        try:
            parts = command.split()
            if not parts:
                return "continue"

            cmd = parts[0].upper()

            if cmd == "LET":
                return self._handle_let(command)
            elif cmd == "IF":
                return self._handle_if(command)
            elif cmd == "FOR":
                return self._handle_for(command)
            elif cmd == "PRINT":
                return self._handle_print(command)
            elif cmd == "REM":
                return self._handle_rem(command)
            elif cmd == "END":
                return "end"
            elif cmd == "INPUT":
                return self._handle_input(command, parts)
            elif cmd == "GOTO":
                return self._handle_goto(command, parts)
            elif cmd == "GOSUB":
                return self._handle_gosub(command, parts)
            elif cmd == "RETURN":
                return self._handle_return()
            elif cmd == "NEXT":
                return self._handle_next(command)
            elif cmd == "DIM":
                return self._handle_dim(command, parts)
            # Math Functions
            elif cmd in ["SIN", "COS", "TAN", "SQRT", "ABS", "INT", "RND"]:
                return self._handle_math_functions(cmd, parts)
            # String Functions
            elif cmd in ["LEN", "MID", "LEFT", "RIGHT", "INSTR", "STR", "VAL"]:
                return self._handle_string_functions(cmd, parts)
            # File I/O Commands
            elif cmd in ["OPEN", "CLOSE", "READ", "WRITE", "EOF"]:
                return self._handle_file_commands(cmd, parts)
            # Enhanced Graphics Commands
            elif cmd in ["LINE", "BOX", "TRIANGLE", "ELLIPSE", "FILL"]:
                return self._handle_enhanced_graphics(cmd, parts)
            # Sound Commands
            elif cmd in ["BEEP", "PLAY", "SOUND", "NOTE"]:
                return self._handle_sound_commands(cmd, parts)
            # Array Operations
            elif cmd in ["SORT", "FIND", "SUM", "AVG", "MIN", "MAX"]:
                return self._handle_array_operations(cmd, parts)
            # Game and Graphics Commands
            # Game Development Commands (BASIC style)
            elif cmd.startswith("GAME"):
                return self._handle_game_commands(command, cmd, parts)
            # Multiplayer (BASIC style)
            elif cmd.startswith("MP") or cmd.startswith("NET"):
                return self._handle_multiplayer_commands(command, cmd, parts)
            # Audio System Commands (BASIC style)
            elif (
                cmd.startswith("SOUND")
                or cmd.startswith("MUSIC")
                or cmd == "MASTERVOLUME"
            ):
                return self._handle_audio_commands(command, cmd, parts)

        except Exception as e:
            self.interpreter.debug_output(f"BASIC command error: {e}")
            return "continue"

        return "continue"

    def _handle_let(self, command):
        """Handle LET variable assignment"""
        if "=" in command:
            _, assignment = command.split(" ", 1)
            if "=" in assignment:
                var_name, expr = assignment.split("=", 1)
                var_name = var_name.strip()
                expr = expr.strip()
                try:
                    value = self.interpreter.evaluate_expression(expr)

                    # Handle array assignment
                    if "(" in var_name and ")" in var_name:
                        # Extract array name and indices
                        array_name = var_name[: var_name.index("(")]
                        indices_str = var_name[
                            var_name.index("(") + 1 : var_name.rindex(")")
                        ]
                        indices = [
                            int(self.interpreter.evaluate_expression(idx.strip()))
                            for idx in indices_str.split(",")
                        ]

                        # Get or create array
                        if array_name not in self.interpreter.variables:
                            self.interpreter.variables[array_name] = {}

                        # Set array element
                        current = self.interpreter.variables[array_name]
                        for idx in indices[:-1]:
                            if idx not in current:
                                current[idx] = {}
                            current = current[idx]
                        current[indices[-1]] = value
                    else:
                        # Simple variable assignment
                        self.interpreter.variables[var_name] = value
                except Exception as e:
                    self.interpreter.debug_output(f"Error in LET {assignment}: {e}")
        return "continue"

    def _handle_if(self, command):
        """Handle IF/THEN conditional statement"""
        try:
            m = re.match(r"IF\s+(.+?)\s+THEN\s+(.+)", command, re.IGNORECASE)
            if m:
                cond_expr = m.group(1).strip()
                then_cmd = m.group(2).strip()
                try:
                    cond_val = self.interpreter.evaluate_expression(cond_expr)
                except Exception:
                    cond_val = False
                if cond_val:
                    # Execute the THEN command using the general line executor so
                    # it can be a BASIC, PILOT or LOGO command fragment.
                    return self.interpreter.execute_line(then_cmd)
        except Exception as e:
            self.interpreter.debug_output(f"IF statement error: {e}")
        return "continue"

    def _handle_for(self, command):
        """Handle FOR loop initialization"""
        try:
            m = re.match(
                r"FOR\s+([A-Za-z_]\w*)\s*=\s*(.+?)\s+TO\s+(.+?)(?:\s+STEP\s+(.+))?$",
                command,
                re.IGNORECASE,
            )
            if m:
                var_name = m.group(1)
                start_expr = m.group(2).strip()
                end_expr = m.group(3).strip()
                step_expr = m.group(4).strip() if m.group(4) else None

                start_val = self.interpreter.evaluate_expression(start_expr)
                end_val = self.interpreter.evaluate_expression(end_expr)
                step_val = (
                    self.interpreter.evaluate_expression(step_expr)
                    if step_expr is not None
                    else 1
                )

                # Integer-only loops: coerce start/end/step to int
                try:
                    start_val = int(start_val)
                except Exception:
                    start_val = 0
                try:
                    end_val = int(end_val)
                except Exception:
                    end_val = 0
                try:
                    step_val = int(step_val)
                except Exception:
                    step_val = 1

                # Store the loop variable and position
                self.interpreter.variables[var_name] = start_val
                self.interpreter.for_stack.append(
                    {
                        "var": var_name,
                        "end": end_val,
                        "step": step_val,
                        "for_line": self.interpreter.current_line,
                    }
                )
        except Exception as e:
            self.interpreter.debug_output(f"FOR statement error: {e}")
        return "continue"

    def _handle_print(self, command):
        """Handle PRINT output statement"""
        text = command[5:].strip()
        if not text:
            self.interpreter.log_output("")
            return "continue"

        # Split by commas for PRINT statements (BASIC standard)
        # Semicolons suppress newlines, commas add spaces
        parts = []
        current_part = ""
        in_quotes = False
        i = 0
        while i < len(text):
            char = text[i]
            if char == '"' and (i == 0 or text[i - 1] != "\\"):
                in_quotes = not in_quotes
                current_part += char
            elif char in [",", ";"] and not in_quotes:
                if current_part.strip():
                    parts.append(current_part.strip())
                    current_part = ""
                # Skip multiple separators
                while i + 1 < len(text) and text[i + 1] in [",", ";"]:
                    i += 1
            else:
                current_part += char
            i += 1

        if current_part.strip():
            parts.append(current_part.strip())

        # Evaluate each part and concatenate
        result_parts = []
        for part in parts:
            if part.startswith('"') and part.endswith('"'):
                # String literal
                result_parts.append(part[1:-1])
            else:
                # Expression or variable
                try:
                    evaluated = self.interpreter.evaluate_expression(part)
                    # Handle string variables properly
                    if isinstance(evaluated, str) and not part.startswith('"'):
                        # This was a string variable, use its value
                        result_parts.append(evaluated)
                    else:
                        result_parts.append(str(evaluated))
                except Exception as e:
                    self.interpreter.debug_output(f"Expression error: {e}")
                    # For variables that failed evaluation, check if they exist directly
                    var_name = part.strip().upper()
                    if var_name in self.interpreter.variables:
                        result_parts.append(str(self.interpreter.variables[var_name]))
                    else:
                        result_parts.append(str(part))

        # Join parts without extra spaces for cleaner output
        result = "".join(result_parts) if parts else ""
        self.interpreter.log_output(result)
        return "continue"

    def _handle_rem(self, command):
        """Handle REM comment statement"""
        # Comment - ignore rest of the line
        return "continue"

    def _handle_input(self, command, parts):
        """Handle INPUT statement"""
        var_name = parts[1] if len(parts) > 1 else "INPUT"
        prompt = f"Enter value for {var_name}: " if len(parts) == 2 else "Enter value: "
        value = self.interpreter.get_user_input(prompt)
        try:
            if "." in value:
                self.interpreter.variables[var_name] = float(value)
            else:
                self.interpreter.variables[var_name] = int(value)
        except:
            self.interpreter.variables[var_name] = value
        return "continue"

    def _handle_goto(self, command, parts):
        """Handle GOTO statement"""
        if len(parts) > 1:
            line_num = int(parts[1])
            for i, (num, _) in enumerate(self.interpreter.program_lines):
                if num == line_num:
                    return f"jump:{i}"
        return "continue"

    def _handle_gosub(self, command, parts):
        """Handle GOSUB statement"""
        if len(parts) > 1:
            line_num = int(parts[1])
            # push next-line index
            self.interpreter.stack.append(self.interpreter.current_line + 1)
            for i, (num, _) in enumerate(self.interpreter.program_lines):
                if num == line_num:
                    return f"jump:{i}"
        return "continue"

    def _handle_return(self):
        """Handle RETURN statement"""
        if self.interpreter.stack:
            return f"jump:{self.interpreter.stack.pop()}"
        return "continue"

    def _handle_next(self, command):
        """Handle NEXT statement"""
        try:
            parts = command.split()
            var_spec = parts[1] if len(parts) > 1 else None

            # Find matching FOR on the stack
            if not self.interpreter.for_stack:
                # Log (not just debug) so tests can assert message
                self.interpreter.log_output("NEXT without FOR")
                return "continue"

            # If var specified, search from top for match, else take top
            if var_spec:
                # strip possible commas
                var_spec = var_spec.strip()
                found_idx = None
                for i in range(len(self.interpreter.for_stack) - 1, -1, -1):
                    if self.interpreter.for_stack[i]["var"].upper() == var_spec.upper():
                        found_idx = i
                        break
                if found_idx is None:
                    self.interpreter.debug_output(
                        f"NEXT for unknown variable {var_spec}"
                    )
                    return "continue"
                ctx = self.interpreter.for_stack[found_idx]
                # remove any inner loops above this one? keep nested intact
                # Only pop if loop finishes
            else:
                ctx = self.interpreter.for_stack[-1]
                found_idx = len(self.interpreter.for_stack) - 1

            var_name = ctx["var"]
            step = int(ctx["step"])
            end_val = int(ctx["end"])

            # Ensure variable exists (treat as integer)
            current_val = self.interpreter.variables.get(var_name, 0)
            try:
                current_val = int(current_val)
            except Exception:
                current_val = 0

            next_val = current_val + step
            self.interpreter.variables[var_name] = int(next_val)

            # Decide whether to loop
            loop_again = False
            try:
                if step >= 0:
                    loop_again = next_val <= int(end_val)
                else:
                    loop_again = next_val >= int(end_val)
            except Exception:
                loop_again = False

            if loop_again:
                # jump to line after FOR statement
                for_line = ctx["for_line"]
                return f"jump:{for_line+1}"
            else:
                # pop this FOR from stack
                try:
                    self.interpreter.for_stack.pop(found_idx)
                except Exception:
                    pass
        except Exception as e:
            self.interpreter.debug_output(f"NEXT statement error: {e}")
        return "continue"

    def _handle_dim(self, command, parts):
        """Handle DIM array declaration"""
        try:
            # DIM ARRAY_NAME(size1, size2, ...)
            if len(parts) >= 2:
                dim_spec = command[3:].strip()  # Remove "DIM"
                if "(" in dim_spec and ")" in dim_spec:
                    array_name = dim_spec.split("(")[0].strip()
                    dimensions_str = dim_spec.split("(")[1].split(")")[0]
                    dimensions = [int(d.strip()) for d in dimensions_str.split(",")]

                    # Create multi-dimensional array initialized with zeros
                    if len(dimensions) == 1:
                        array = [0] * (
                            dimensions[0] + 1
                        )  # +1 for BASIC 0-based indexing
                    elif len(dimensions) == 2:
                        array = [
                            [0 for _ in range(dimensions[1] + 1)]
                            for _ in range(dimensions[0] + 1)
                        ]
                    else:
                        # For higher dimensions, create nested lists
                        def create_array(dims):
                            if len(dims) == 1:
                                return [0] * (dims[0] + 1)
                            else:
                                return [
                                    create_array(dims[1:]) for _ in range(dims[0] + 1)
                                ]

                        array = create_array(dimensions)

                    # Store the array
                    self.interpreter.variables[array_name] = array
                    self.interpreter.log_output(
                        f"Array {array_name} declared with dimensions {dimensions}"
                    )
        except Exception as e:
            self.interpreter.debug_output(f"DIM statement error: {e}")
        return "continue"

    def _handle_math_functions(self, cmd, parts):
        """Handle mathematical functions"""
        try:
            if cmd == "SIN":
                # SIN(angle) - sine of angle in degrees
                if len(parts) >= 2:
                    angle = float(self.interpreter.evaluate_expression(parts[1]))
                    result = math.sin(math.radians(angle))
                    self.interpreter.variables["RESULT"] = result
                    self.interpreter.log_output(f"SIN({angle}°) = {result:.4f}")
                else:
                    self.interpreter.log_output("SIN requires an angle parameter")
            elif cmd == "COS":
                # COS(angle) - cosine of angle in degrees
                if len(parts) >= 2:
                    angle = float(self.interpreter.evaluate_expression(parts[1]))
                    result = math.cos(math.radians(angle))
                    self.interpreter.variables["RESULT"] = result
                    self.interpreter.log_output(f"COS({angle}°) = {result:.4f}")
                else:
                    self.interpreter.log_output("COS requires an angle parameter")
            elif cmd == "TAN":
                # TAN(angle) - tangent of angle in degrees
                if len(parts) >= 2:
                    angle = float(self.interpreter.evaluate_expression(parts[1]))
                    result = math.tan(math.radians(angle))
                    self.interpreter.variables["RESULT"] = result
                    self.interpreter.log_output(f"TAN({angle}°) = {result:.4f}")
                else:
                    self.interpreter.log_output("TAN requires an angle parameter")
            elif cmd == "SQRT":
                # SQRT(value) - square root
                if len(parts) >= 2:
                    value = float(self.interpreter.evaluate_expression(parts[1]))
                    if value >= 0:
                        result = math.sqrt(value)
                        self.interpreter.variables["RESULT"] = result
                        self.interpreter.log_output(f"SQRT({value}) = {result:.4f}")
                    else:
                        self.interpreter.log_output(
                            "SQRT requires a non-negative value"
                        )
                else:
                    self.interpreter.log_output("SQRT requires a value parameter")
            elif cmd == "ABS":
                # ABS(value) - absolute value
                if len(parts) >= 2:
                    value = float(self.interpreter.evaluate_expression(parts[1]))
                    result = abs(value)
                    self.interpreter.variables["RESULT"] = result
                    self.interpreter.log_output(f"ABS({value}) = {result}")
                else:
                    self.interpreter.log_output("ABS requires a value parameter")
            elif cmd == "INT":
                # INT(value) - integer part
                if len(parts) >= 2:
                    value = float(self.interpreter.evaluate_expression(parts[1]))
                    result = int(value)
                    self.interpreter.variables["RESULT"] = result
                    self.interpreter.log_output(f"INT({value}) = {result}")
                else:
                    self.interpreter.log_output("INT requires a value parameter")
            elif cmd == "RND":
                # RND() or RND(max) - random number
                if len(parts) >= 2:
                    max_val = float(self.interpreter.evaluate_expression(parts[1]))
                    result = random.uniform(0, max_val)
                else:
                    result = random.random()
                self.interpreter.variables["RESULT"] = result
                self.interpreter.log_output(f"RND() = {result:.4f}")
        except Exception as e:
            self.interpreter.debug_output(f"Math function error: {e}")
        return "continue"

    def _handle_string_functions(self, cmd, parts):
        """Handle string manipulation functions"""
        try:
            if cmd == "LEN":
                # LEN(string) - length of string
                if len(parts) >= 2:
                    text = str(self.interpreter.evaluate_expression(parts[1]))
                    result = len(text)
                    self.interpreter.variables["RESULT"] = result
                    self.interpreter.log_output(f"LEN('{text}') = {result}")
                else:
                    self.interpreter.log_output("LEN requires a string parameter")
            elif cmd == "MID":
                # MID(string, start, length) - substring
                if len(parts) >= 4:
                    text = str(self.interpreter.evaluate_expression(parts[1]))
                    start = (
                        int(self.interpreter.evaluate_expression(parts[2])) - 1
                    )  # BASIC is 1-based
                    length = int(self.interpreter.evaluate_expression(parts[3]))
                    result = text[start : start + length]
                    self.interpreter.variables["RESULT"] = result
                    self.interpreter.log_output(
                        f"MID('{text}', {start+1}, {length}) = '{result}'"
                    )
                else:
                    self.interpreter.log_output(
                        "MID requires string, start, and length parameters"
                    )
            elif cmd == "LEFT":
                # LEFT(string, length) - left substring
                if len(parts) >= 3:
                    text = str(self.interpreter.evaluate_expression(parts[1]))
                    length = int(self.interpreter.evaluate_expression(parts[2]))
                    result = text[:length]
                    self.interpreter.variables["RESULT"] = result
                    self.interpreter.log_output(
                        f"LEFT('{text}', {length}) = '{result}'"
                    )
                else:
                    self.interpreter.log_output(
                        "LEFT requires string and length parameters"
                    )
            elif cmd == "RIGHT":
                # RIGHT(string, length) - right substring
                if len(parts) >= 3:
                    text = str(self.interpreter.evaluate_expression(parts[1]))
                    length = int(self.interpreter.evaluate_expression(parts[2]))
                    result = text[-length:]
                    self.interpreter.variables["RESULT"] = result
                    self.interpreter.log_output(
                        f"RIGHT('{text}', {length}) = '{result}'"
                    )
                else:
                    self.interpreter.log_output(
                        "RIGHT requires string and length parameters"
                    )
            elif cmd == "INSTR":
                # INSTR(string, search) - find substring position
                if len(parts) >= 3:
                    text = str(self.interpreter.evaluate_expression(parts[1]))
                    search = str(self.interpreter.evaluate_expression(parts[2]))
                    pos = text.find(search)
                    result = (
                        pos + 1 if pos != -1 else 0
                    )  # BASIC is 1-based, 0 means not found
                    self.interpreter.variables["RESULT"] = result
                    self.interpreter.log_output(
                        f"INSTR('{text}', '{search}') = {result}"
                    )
                else:
                    self.interpreter.log_output(
                        "INSTR requires string and search parameters"
                    )
            elif cmd == "STR":
                # STR(number) - convert number to string
                if len(parts) >= 2:
                    value = self.interpreter.evaluate_expression(parts[1])
                    result = str(value)
                    self.interpreter.variables["RESULT"] = result
                    self.interpreter.log_output(f"STR({value}) = '{result}'")
                else:
                    self.interpreter.log_output("STR requires a value parameter")
            elif cmd == "VAL":
                # VAL(string) - convert string to number
                if len(parts) >= 2:
                    text = str(self.interpreter.evaluate_expression(parts[1]))
                    try:
                        result = float(text)
                        self.interpreter.variables["RESULT"] = result
                        self.interpreter.log_output(f"VAL('{text}') = {result}")
                    except ValueError:
                        result = 0
                        self.interpreter.variables["RESULT"] = result
                        self.interpreter.log_output(
                            f"VAL('{text}') = {result} (conversion failed)"
                        )
                else:
                    self.interpreter.log_output("VAL requires a string parameter")
        except Exception as e:
            self.interpreter.debug_output(f"String function error: {e}")
        return "continue"

    def _handle_file_commands(self, cmd, parts):
        """Handle file I/O commands"""
        try:
            if cmd == "OPEN":
                # OPEN "filename" FOR mode AS #handle
                if (
                    len(parts) >= 5
                    and parts[2].upper() == "FOR"
                    and parts[4].upper() == "AS"
                ):
                    filename = parts[1].strip('"')
                    mode = parts[3].upper()
                    handle_part = parts[5]
                    if handle_part.startswith("#"):
                        handle = int(handle_part[1:])

                        mode_map = {"INPUT": "r", "OUTPUT": "w", "APPEND": "a"}
                        if mode in mode_map:
                            try:
                                file_obj = open(filename, mode_map[mode])
                                if not hasattr(self.interpreter, "open_files"):
                                    self.interpreter.open_files = {}
                                self.interpreter.open_files[handle] = file_obj
                                self.interpreter.log_output(
                                    f"File '{filename}' opened as #{handle} for {mode}"
                                )
                            except Exception as e:
                                self.interpreter.log_output(f"Error opening file: {e}")
                        else:
                            self.interpreter.log_output(
                                "Invalid file mode. Use INPUT, OUTPUT, or APPEND"
                            )
                    else:
                        self.interpreter.log_output("File handle must start with #")
                else:
                    self.interpreter.log_output(
                        'OPEN syntax: OPEN "filename" FOR mode AS #handle'
                    )
            elif cmd == "CLOSE":
                # CLOSE #handle
                if len(parts) >= 2 and parts[1].startswith("#"):
                    handle = int(parts[1][1:])
                    if (
                        hasattr(self.interpreter, "open_files")
                        and handle in self.interpreter.open_files
                    ):
                        self.interpreter.open_files[handle].close()
                        del self.interpreter.open_files[handle]
                        self.interpreter.log_output(f"File #{handle} closed")
                    else:
                        self.interpreter.log_output(f"File #{handle} not open")
                else:
                    self.interpreter.log_output("CLOSE syntax: CLOSE #handle")
            elif cmd == "READ":
                # READ #handle, variable
                if len(parts) >= 3 and parts[1].startswith("#") and parts[2] == ",":
                    handle = int(parts[1][1:])
                    var_name = parts[3]
                    if (
                        hasattr(self.interpreter, "open_files")
                        and handle in self.interpreter.open_files
                    ):
                        try:
                            line = (
                                self.interpreter.open_files[handle].readline().strip()
                            )
                            if line:
                                # Try to parse as number, otherwise keep as string
                                try:
                                    self.interpreter.variables[var_name] = float(line)
                                except ValueError:
                                    self.interpreter.variables[var_name] = line
                                self.interpreter.log_output(
                                    f"Read '{line}' into {var_name}"
                                )
                            else:
                                self.interpreter.variables["EOF"] = True
                                self.interpreter.log_output("End of file reached")
                        except Exception as e:
                            self.interpreter.log_output(f"Error reading file: {e}")
                    else:
                        self.interpreter.log_output(f"File #{handle} not open")
                else:
                    self.interpreter.log_output("READ syntax: READ #handle, variable")
            elif cmd == "WRITE":
                # WRITE #handle, expression
                if len(parts) >= 3 and parts[1].startswith("#") and parts[2] == ",":
                    handle = int(parts[1][1:])
                    expr = " ".join(parts[3:])
                    if (
                        hasattr(self.interpreter, "open_files")
                        and handle in self.interpreter.open_files
                    ):
                        try:
                            value = self.interpreter.evaluate_expression(expr)
                            self.interpreter.open_files[handle].write(str(value) + "\n")
                            self.interpreter.log_output(
                                f"Wrote '{value}' to file #{handle}"
                            )
                        except Exception as e:
                            self.interpreter.log_output(f"Error writing to file: {e}")
                    else:
                        self.interpreter.log_output(f"File #{handle} not open")
                else:
                    self.interpreter.log_output(
                        "WRITE syntax: WRITE #handle, expression"
                    )
            elif cmd == "EOF":
                # EOF(#handle) - check if end of file
                if (
                    len(parts) >= 2
                    and parts[1].startswith("#(")
                    and parts[1].endswith(")")
                ):
                    handle = int(parts[1][2:-1])
                    if (
                        hasattr(self.interpreter, "open_files")
                        and handle in self.interpreter.open_files
                    ):
                        try:
                            current_pos = self.interpreter.open_files[handle].tell()
                            self.interpreter.open_files[handle].readline()
                            eof = (
                                self.interpreter.open_files[handle].tell()
                                == current_pos
                            )
                            self.interpreter.open_files[handle].seek(
                                current_pos
                            )  # Reset position
                            self.interpreter.variables["RESULT"] = eof
                            self.interpreter.log_output(f"EOF(#{handle}) = {eof}")
                        except Exception:
                            self.interpreter.variables["RESULT"] = True
                    else:
                        self.interpreter.variables["RESULT"] = True
                else:
                    self.interpreter.log_output("EOF syntax: EOF(#handle)")
        except Exception as e:
            self.interpreter.debug_output(f"File command error: {e}")
        return "continue"

    def _handle_enhanced_graphics(self, cmd, parts):
        """Handle enhanced graphics commands"""
        try:
            if cmd == "LINE":
                # LINE (x1,y1)-(x2,y2), color
                if len(parts) >= 2:
                    coord_part = parts[1]
                    color = parts[2] if len(parts) > 2 else None

                    if "-" in coord_part and "(" in coord_part and ")" in coord_part:
                        coords = coord_part.split("-")
                        if len(coords) == 2:
                            start_coord = coords[0].strip("()")
                            end_coord = coords[1].strip("()")

                            start_parts = start_coord.split(",")
                            end_parts = end_coord.split(",")

                            if len(start_parts) == 2 and len(end_parts) == 2:
                                x1 = float(start_parts[0])
                                y1 = float(start_parts[1])
                                x2 = float(end_parts[0])
                                y2 = float(end_parts[1])

                                if (
                                    hasattr(self.interpreter, "ide_turtle_canvas")
                                    and self.interpreter.ide_turtle_canvas
                                ):
                                    canvas = self.interpreter.ide_turtle_canvas
                                    color_name = color if color else "black"
                                    canvas.create_line(
                                        x1,
                                        y1,
                                        x2,
                                        y2,
                                        fill=color_name,
                                        tags="game_objects",
                                    )
                                    self.interpreter.log_output(
                                        f"Drew line from ({x1},{y1}) to ({x2},{y2})"
                                    )
                                elif self.pygame_screen:
                                    import pygame

                                    pygame.draw.line(
                                        self.pygame_screen,
                                        self.current_color,
                                        (x1, y1),
                                        (x2, y2),
                                    )
                                    self.interpreter.log_output(
                                        f"Drew line from ({x1},{y1}) to ({x2},{y2})"
                                    )
                                else:
                                    self.interpreter.log_output(
                                        "Graphics not initialized"
                                    )
                            else:
                                self.interpreter.log_output("Invalid LINE coordinates")
                        else:
                            self.interpreter.log_output(
                                "LINE syntax: LINE (x1,y1)-(x2,y2) [,color]"
                            )
                    else:
                        self.interpreter.log_output(
                            "LINE syntax: LINE (x1,y1)-(x2,y2) [,color]"
                        )
            elif cmd == "BOX":
                # BOX (x,y), width, height, filled
                if len(parts) >= 4:
                    coord_part = parts[1].strip("()")
                    width = float(parts[2])
                    height = float(parts[3])
                    filled = parts[4].lower() == "true" if len(parts) > 4 else False

                    coord_parts = coord_part.split(",")
                    if len(coord_parts) == 2:
                        x = float(coord_parts[0])
                        y = float(coord_parts[1])

                        if (
                            hasattr(self.interpreter, "ide_turtle_canvas")
                            and self.interpreter.ide_turtle_canvas
                        ):
                            canvas = self.interpreter.ide_turtle_canvas
                            if filled:
                                canvas.create_rectangle(
                                    x,
                                    y,
                                    x + width,
                                    y + height,
                                    fill="black",
                                    tags="game_objects",
                                )
                            else:
                                canvas.create_rectangle(
                                    x,
                                    y,
                                    x + width,
                                    y + height,
                                    outline="black",
                                    tags="game_objects",
                                )
                            self.interpreter.log_output(
                                f"Drew {'filled ' if filled else ''}box at ({x},{y}) size {width}x{height}"
                            )
                        elif self.pygame_screen:
                            import pygame

                            rect = pygame.Rect(x, y, width, height)
                            if filled:
                                pygame.draw.rect(
                                    self.pygame_screen, self.current_color, rect
                                )
                            else:
                                pygame.draw.rect(
                                    self.pygame_screen, self.current_color, rect, 2
                                )
                            self.interpreter.log_output(
                                f"Drew {'filled ' if filled else ''}box at ({x},{y}) size {width}x{height}"
                            )
                        else:
                            self.interpreter.log_output("Graphics not initialized")
                    else:
                        self.interpreter.log_output("Invalid BOX coordinates")
                else:
                    self.interpreter.log_output(
                        "BOX syntax: BOX (x,y), width, height [,filled]"
                    )
            elif cmd == "TRIANGLE":
                # TRIANGLE (x1,y1)-(x2,y2)-(x3,y3), filled
                if len(parts) >= 2:
                    coord_part = parts[1]
                    filled = parts[2].lower() == "true" if len(parts) > 2 else False

                    if coord_part.count("-") == 2:
                        coords = coord_part.split("-")
                        points = []
                        valid = True
                        for coord in coords:
                            coord = coord.strip("()")
                            parts_coord = coord.split(",")
                            if len(parts_coord) == 2:
                                try:
                                    x = float(parts_coord[0])
                                    y = float(parts_coord[1])
                                    points.extend([x, y])
                                except ValueError:
                                    valid = False
                                    break
                            else:
                                valid = False
                                break

                        if valid and len(points) == 6:
                            if (
                                hasattr(self.interpreter, "ide_turtle_canvas")
                                and self.interpreter.ide_turtle_canvas
                            ):
                                canvas = self.interpreter.ide_turtle_canvas
                                if filled:
                                    canvas.create_polygon(
                                        points, fill="black", tags="game_objects"
                                    )
                                else:
                                    canvas.create_polygon(
                                        points,
                                        outline="black",
                                        fill="",
                                        tags="game_objects",
                                    )
                                self.interpreter.log_output(
                                    f"Drew {'filled ' if filled else ''}triangle"
                                )
                            elif self.pygame_screen:
                                import pygame

                                if filled:
                                    pygame.draw.polygon(
                                        self.pygame_screen,
                                        self.current_color,
                                        [
                                            (points[i], points[i + 1])
                                            for i in range(0, 6, 2)
                                        ],
                                    )
                                else:
                                    pygame.draw.polygon(
                                        self.pygame_screen,
                                        self.current_color,
                                        [
                                            (points[i], points[i + 1])
                                            for i in range(0, 6, 2)
                                        ],
                                        2,
                                    )
                                self.interpreter.log_output(
                                    f"Drew {'filled ' if filled else ''}triangle"
                                )
                            else:
                                self.interpreter.log_output("Graphics not initialized")
                        else:
                            self.interpreter.log_output("Invalid TRIANGLE coordinates")
                    else:
                        self.interpreter.log_output(
                            "TRIANGLE syntax: TRIANGLE (x1,y1)-(x2,y2)-(x3,y3) [,filled]"
                        )
            elif cmd == "ELLIPSE":
                # ELLIPSE (x,y), width, height, filled
                if len(parts) >= 4:
                    coord_part = parts[1].strip("()")
                    width = float(parts[2])
                    height = float(parts[3])
                    filled = parts[4].lower() == "true" if len(parts) > 4 else False

                    coord_parts = coord_part.split(",")
                    if len(coord_parts) == 2:
                        x = float(coord_parts[0])
                        y = float(coord_parts[1])

                        if (
                            hasattr(self.interpreter, "ide_turtle_canvas")
                            and self.interpreter.ide_turtle_canvas
                        ):
                            canvas = self.interpreter.ide_turtle_canvas
                            if filled:
                                canvas.create_oval(
                                    x,
                                    y,
                                    x + width,
                                    y + height,
                                    fill="black",
                                    tags="game_objects",
                                )
                            else:
                                canvas.create_oval(
                                    x,
                                    y,
                                    x + width,
                                    y + height,
                                    outline="black",
                                    tags="game_objects",
                                )
                            self.interpreter.log_output(
                                f"Drew {'filled ' if filled else ''}ellipse at ({x},{y}) size {width}x{height}"
                            )
                        elif self.pygame_screen:
                            import pygame

                            rect = pygame.Rect(x, y, width, height)
                            if filled:
                                pygame.draw.ellipse(
                                    self.pygame_screen, self.current_color, rect
                                )
                            else:
                                pygame.draw.ellipse(
                                    self.pygame_screen, self.current_color, rect, 2
                                )
                            self.interpreter.log_output(
                                f"Drew {'filled ' if filled else ''}ellipse at ({x},{y}) size {width}x{height}"
                            )
                        else:
                            self.interpreter.log_output("Graphics not initialized")
                    else:
                        self.interpreter.log_output("Invalid ELLIPSE coordinates")
                else:
                    self.interpreter.log_output(
                        "ELLIPSE syntax: ELLIPSE (x,y), width, height [,filled]"
                    )
            elif cmd == "FILL":
                # FILL (x,y), color - flood fill from point
                if len(parts) >= 2:
                    coord_part = parts[1].strip("()")
                    color = parts[2] if len(parts) > 2 else "black"

                    coord_parts = coord_part.split(",")
                    if len(coord_parts) == 2:
                        x = float(coord_parts[0])
                        y = float(coord_parts[1])

                        # Flood fill is complex - for now just draw a small filled circle
                        if (
                            hasattr(self.interpreter, "ide_turtle_canvas")
                            and self.interpreter.ide_turtle_canvas
                        ):
                            canvas = self.interpreter.ide_turtle_canvas
                            canvas.create_oval(
                                x - 5,
                                y - 5,
                                x + 5,
                                y + 5,
                                fill=color,
                                tags="game_objects",
                            )
                            self.interpreter.log_output(
                                f"Flood fill at ({x},{y}) with {color}"
                            )
                        elif self.pygame_screen:
                            import pygame

                            pygame.draw.circle(
                                self.pygame_screen, self.current_color, (x, y), 5
                            )
                            self.interpreter.log_output(
                                f"Flood fill at ({x},{y}) with {color}"
                            )
                        else:
                            self.interpreter.log_output("Graphics not initialized")
                    else:
                        self.interpreter.log_output("Invalid FILL coordinates")
                else:
                    self.interpreter.log_output("FILL syntax: FILL (x,y) [,color]")
        except Exception as e:
            self.interpreter.debug_output(f"Enhanced graphics error: {e}")
        return "continue"

    def _handle_sound_commands(self, cmd, parts):
        """Handle sound and music commands"""
        try:
            if cmd == "BEEP":
                # BEEP frequency, duration
                frequency = 800 if len(parts) < 2 else float(parts[1])
                duration = 0.5 if len(parts) < 3 else float(parts[2])

                try:
                    import winsound

                    winsound.Beep(int(frequency), int(duration * 1000))
                    self.interpreter.log_output(f"Beep: {frequency}Hz for {duration}s")
                except ImportError:
                    # On non-Windows systems, just log
                    self.interpreter.log_output(
                        f"Beep: {frequency}Hz for {duration}s (simulated)"
                    )
            elif cmd == "PLAY":
                # PLAY "note" or PLAY frequency
                if len(parts) >= 2:
                    note_or_freq = parts[1].strip('"')

                    # Simple note to frequency mapping
                    note_freqs = {
                        "C4": 261.63,
                        "D4": 293.66,
                        "E4": 329.63,
                        "F4": 349.23,
                        "G4": 392.00,
                        "A4": 440.00,
                        "B4": 493.88,
                        "C5": 523.25,
                    }

                    if note_or_freq.upper() in note_freqs:
                        frequency = note_freqs[note_or_freq.upper()]
                    else:
                        try:
                            frequency = float(note_or_freq)
                        except ValueError:
                            frequency = 440  # Default A4

                    duration = 0.5 if len(parts) < 3 else float(parts[2])

                    try:
                        import winsound

                        winsound.Beep(int(frequency), int(duration * 1000))
                        self.interpreter.log_output(
                            f"Played {note_or_freq} for {duration}s"
                        )
                    except ImportError:
                        self.interpreter.log_output(
                            f"Played {note_or_freq} for {duration}s (simulated)"
                        )
                else:
                    self.interpreter.log_output("PLAY syntax: PLAY note [,duration]")
            elif cmd == "SOUND":
                # SOUND frequency, duration, volume
                if len(parts) >= 3:
                    frequency = float(parts[1])
                    duration = float(parts[2])
                    volume = float(parts[3]) if len(parts) > 3 else 1.0

                    self.interpreter.log_output(
                        f"Sound: {frequency}Hz, {duration}s, volume {volume}"
                    )
                else:
                    self.interpreter.log_output(
                        "SOUND syntax: SOUND frequency, duration [,volume]"
                    )
            elif cmd == "NOTE":
                # NOTE note_name, octave, duration
                if len(parts) >= 3:
                    note = parts[1].strip('"')
                    octave = int(parts[2])
                    duration = float(parts[3]) if len(parts) > 3 else 0.5

                    # Calculate frequency from note and octave
                    note_values = {
                        "C": 0,
                        "C#": 1,
                        "D": 2,
                        "D#": 3,
                        "E": 4,
                        "F": 4,
                        "F#": 5,
                        "G": 6,
                        "G#": 7,
                        "A": 8,
                        "A#": 9,
                        "B": 10,
                    }

                    if note.upper() in note_values:
                        semitone = note_values[note.upper()] + (octave - 4) * 12
                        frequency = 440 * (2 ** (semitone / 12.0))

                        try:
                            import winsound

                            winsound.Beep(int(frequency), int(duration * 1000))
                            self.interpreter.log_output(
                                f"Note: {note}{octave} for {duration}s"
                            )
                        except ImportError:
                            self.interpreter.log_output(
                                f"Note: {note}{octave} for {duration}s (simulated)"
                            )
                    else:
                        self.interpreter.log_output("Invalid note name")
                else:
                    self.interpreter.log_output(
                        "NOTE syntax: NOTE note, octave [,duration]"
                    )
        except Exception as e:
            self.interpreter.debug_output(f"Sound command error: {e}")
        return "continue"

    def _handle_array_operations(self, cmd, parts):
        """Handle array operations"""
        try:
            if cmd == "SORT":
                # SORT array_name
                if len(parts) >= 2:
                    array_name = parts[1]
                    if array_name in self.interpreter.variables:
                        array = self.interpreter.variables[array_name]
                        if isinstance(array, list):
                            try:
                                sorted_array = sorted(array)
                                self.interpreter.variables[array_name] = sorted_array
                                self.interpreter.log_output(
                                    f"Array {array_name} sorted"
                                )
                            except Exception:
                                self.interpreter.log_output(
                                    "Array contains non-comparable elements"
                                )
                        else:
                            self.interpreter.log_output(f"{array_name} is not an array")
                    else:
                        self.interpreter.log_output(f"Array {array_name} not found")
                else:
                    self.interpreter.log_output("SORT syntax: SORT array_name")
            elif cmd == "FIND":
                # FIND array_name, value
                if len(parts) >= 3:
                    array_name = parts[1]
                    search_value = self.interpreter.evaluate_expression(parts[2])

                    if array_name in self.interpreter.variables:
                        array = self.interpreter.variables[array_name]
                        if isinstance(array, list):
                            try:
                                index = array.index(search_value)
                                self.interpreter.variables["RESULT"] = index
                                self.interpreter.log_output(
                                    f"Found {search_value} at index {index} in {array_name}"
                                )
                            except ValueError:
                                self.interpreter.variables["RESULT"] = -1
                                self.interpreter.log_output(
                                    f"Value {search_value} not found in {array_name}"
                                )
                        else:
                            self.interpreter.log_output(f"{array_name} is not an array")
                    else:
                        self.interpreter.log_output(f"Array {array_name} not found")
                else:
                    self.interpreter.log_output("FIND syntax: FIND array_name, value")
            elif cmd in ["SUM", "AVG", "MIN", "MAX"]:
                # SUM/AVG/MIN/MAX array_name
                if len(parts) >= 2:
                    array_name = parts[1]
                    if array_name in self.interpreter.variables:
                        array = self.interpreter.variables[array_name]
                        if isinstance(array, list) and array:
                            try:
                                if cmd == "SUM":
                                    result = sum(array)
                                    operation = "sum"
                                elif cmd == "AVG":
                                    result = sum(array) / len(array)
                                    operation = "average"
                                elif cmd == "MIN":
                                    result = min(array)
                                    operation = "minimum"
                                elif cmd == "MAX":
                                    result = max(array)
                                    operation = "maximum"

                                self.interpreter.variables["RESULT"] = result
                                self.interpreter.log_output(
                                    f"Array {array_name} {operation}: {result}"
                                )
                            except Exception:
                                self.interpreter.log_output(
                                    "Array contains non-numeric elements"
                                )
                        else:
                            self.interpreter.log_output(
                                f"{array_name} is not a valid array"
                            )
                    else:
                        self.interpreter.log_output(f"Array {array_name} not found")
                else:
                    self.interpreter.log_output(f"{cmd} syntax: {cmd} array_name")
        except Exception as e:
            self.interpreter.debug_output(f"Array operation error: {e}")
        return "continue"

    def _handle_game_commands(self, command, cmd, parts):
        """Handle game development commands"""
        if cmd == "GAMESCREEN":
            # GAMESCREEN width, height [, title]
            if len(parts) >= 3:
                try:
                    width = int(parts[1].rstrip(","))
                    height = int(parts[2].rstrip(","))
                    title = (
                        " ".join(parts[3:]).strip('"')
                        if len(parts) > 3
                        else "Time_Warp Game Window"
                    )
                    self.interpreter.log_output(
                        f"🎮 Game screen initialized: {width}x{height} - {title}"
                    )

                    # Initialize graphics - either IDE canvas or standalone pygame
                    if (
                        hasattr(self.interpreter, "ide_turtle_canvas")
                        and self.interpreter.ide_turtle_canvas
                    ):
                        # IDE mode - use turtle canvas
                        canvas = self.interpreter.ide_turtle_canvas
                        canvas.delete("all")  # Clear canvas
                        canvas.config(
                            width=min(width, 600), height=min(height, 400)
                        )  # Limit size
                        canvas.create_text(
                            width // 2, 20, text=title, font=("Arial", 16), fill="white"
                        )
                        self.interpreter.log_output(
                            "🎨 Graphics canvas initialized for game"
                        )
                    else:
                        # Standalone mode - use pygame
                        self._init_pygame_graphics(width, height, title)
                        self.interpreter.log_output(
                            "🎮 Pygame graphics initialized for standalone game"
                        )
                except ValueError:
                    self.interpreter.log_output("Error: Invalid GAMESCREEN parameters")
        elif cmd == "GAMEBG":
            # GAMEBG r, g, b - set background color
            if len(parts) >= 4:
                try:
                    r = int(parts[1].rstrip(","))
                    g = int(parts[2].rstrip(","))
                    b = int(parts[3].rstrip(","))
                    color = f"#{r:02x}{g:02x}{b:02x}"
                    self.interpreter.log_output(
                        f"🎨 Background color set to RGB({r},{g},{b})"
                    )

                    if (
                        hasattr(self.interpreter, "ide_turtle_canvas")
                        and self.interpreter.ide_turtle_canvas
                    ):
                        # IDE mode
                        self.interpreter.ide_turtle_canvas.config(bg=color)
                    elif self.pygame_screen:
                        # Pygame mode
                        self.pygame_screen.fill((r, g, b))
                except ValueError:
                    self.interpreter.log_output("Error: Invalid GAMEBG color values")
        elif cmd == "GAMELOOP":
            self.interpreter.log_output("🔄 Game loop started")
        elif cmd == "GAMEEND":
            self.interpreter.log_output("🎮 Game ended")
        elif cmd == "GAMECLEAR":
            # Clear the game screen
            self.interpreter.log_output("🧹 Game screen cleared")
            if (
                hasattr(self.interpreter, "ide_turtle_canvas")
                and self.interpreter.ide_turtle_canvas
            ):
                # IDE mode
                self.interpreter.ide_turtle_canvas.delete("game_objects")
            elif self.pygame_screen:
                # Pygame mode - fill with black
                self.pygame_screen.fill((0, 0, 0))
        elif cmd == "GAMECOLOR":
            # GAMECOLOR r, g, b - set drawing color
            if len(parts) >= 4:
                try:
                    r = int(parts[1].rstrip(","))
                    g = int(parts[2].rstrip(","))
                    b = int(parts[3].rstrip(","))
                    self.interpreter.variables["GAME_COLOR"] = f"#{r:02x}{g:02x}{b:02x}"
                    self.current_color = (r, g, b)  # Store for pygame
                    self.interpreter.log_output(
                        f"🎨 Drawing color set to RGB({r},{g},{b})"
                    )
                except ValueError:
                    self.interpreter.log_output("Error: Invalid GAMECOLOR values")
        elif cmd == "GAMEPOINT":
            # GAMEPOINT x, y - draw a point
            if len(parts) >= 3:
                try:
                    x = int(parts[1].rstrip(","))
                    y = int(parts[2].rstrip(","))
                    color = self.interpreter.variables.get("GAME_COLOR", "#FFFFFF")

                    if (
                        hasattr(self.interpreter, "ide_turtle_canvas")
                        and self.interpreter.ide_turtle_canvas
                    ):
                        # IDE mode
                        canvas = self.interpreter.ide_turtle_canvas
                        canvas.create_oval(
                            x,
                            y,
                            x + 2,
                            y + 2,
                            fill=color,
                            outline=color,
                            tags="game_objects",
                        )
                    elif self.pygame_screen:
                        # Pygame mode
                        import pygame

                        pygame.draw.circle(
                            self.pygame_screen, self.current_color, (x, y), 1
                        )
                except ValueError:
                    self.interpreter.log_output("Error: Invalid GAMEPOINT coordinates")
        elif cmd == "GAMERECT":
            # GAMERECT x, y, width, height, filled
            if len(parts) >= 6:
                try:
                    x = int(parts[1].rstrip(","))
                    y = int(parts[2].rstrip(","))
                    width = int(parts[3].rstrip(","))
                    height = int(parts[4].rstrip(","))
                    filled = int(parts[5])
                    color = self.interpreter.variables.get("GAME_COLOR", "#FFFFFF")

                    if (
                        hasattr(self.interpreter, "ide_turtle_canvas")
                        and self.interpreter.ide_turtle_canvas
                    ):
                        # IDE mode
                        canvas = self.interpreter.ide_turtle_canvas
                        if filled:
                            canvas.create_rectangle(
                                x,
                                y,
                                x + width,
                                y + height,
                                fill=color,
                                outline=color,
                                tags="game_objects",
                            )
                        else:
                            canvas.create_rectangle(
                                x,
                                y,
                                x + width,
                                y + height,
                                outline=color,
                                tags="game_objects",
                            )
                    elif self.pygame_screen:
                        # Pygame mode
                        import pygame

                        rect = pygame.Rect(x, y, width, height)
                        if filled:
                            pygame.draw.rect(
                                self.pygame_screen, self.current_color, rect
                            )
                        else:
                            pygame.draw.rect(
                                self.pygame_screen, self.current_color, rect, 2
                            )
                except ValueError:
                    self.interpreter.log_output("Error: Invalid GAMERECT parameters")
        elif cmd == "GAMELOOP":
            self.interpreter.log_output("🔄 Game loop started")
        elif cmd == "GAMETEXT":
            # GAMETEXT x, y, "text"
            if len(parts) >= 4:
                try:
                    x = int(parts[1].rstrip(","))
                    y = int(parts[2].rstrip(","))
                    text = " ".join(parts[3:]).strip('"')
                    color = self.interpreter.variables.get("GAME_COLOR", "#FFFFFF")

                    if (
                        hasattr(self.interpreter, "ide_turtle_canvas")
                        and self.interpreter.ide_turtle_canvas
                    ):
                        # IDE mode
                        canvas = self.interpreter.ide_turtle_canvas
                        canvas.create_text(
                            x,
                            y,
                            text=text,
                            fill=color,
                            font=("Arial", 12),
                            tags="game_objects",
                        )
                    elif self.pygame_screen:
                        # Pygame mode
                        import pygame

                        font = pygame.font.Font(None, 24)
                        text_surface = font.render(text, True, self.current_color)
                        self.pygame_screen.blit(text_surface, (x, y))
                except ValueError:
                    self.interpreter.log_output("Error: Invalid GAMETEXT parameters")
        elif cmd == "GAMEUPDATE":
            # Update/refresh the display
            if (
                hasattr(self.interpreter, "ide_turtle_canvas")
                and self.interpreter.ide_turtle_canvas
            ):
                # IDE mode
                self.interpreter.ide_turtle_canvas.update()
                self.interpreter.log_output("🔄 Display updated")
            elif self.pygame_screen:
                # Pygame mode
                import pygame

                pygame.display.flip()
                self.interpreter.log_output("🔄 Pygame display updated")
        elif cmd == "GAMEDELAY":
            # GAMEDELAY milliseconds - delay for frame rate control
            if len(parts) >= 2:
                try:
                    delay_ms = int(parts[1])
                    import time

                    time.sleep(delay_ms / 1000.0)  # Convert to seconds
                except ValueError:
                    self.interpreter.log_output("Error: Invalid GAMEDELAY parameter")
        elif cmd == "GAMECIRCLE":
            # GAMECIRCLE x, y, radius, filled (for 2-param version, assume filled=0)
            if len(parts) >= 4:
                try:
                    x = int(parts[1].rstrip(","))
                    y = int(parts[2].rstrip(","))
                    radius = int(parts[3].rstrip(","))
                    filled = int(parts[4]) if len(parts) >= 5 else 0  # Default unfilled
                    color = self.interpreter.variables.get("GAME_COLOR", "#FFFFFF")

                    if (
                        hasattr(self.interpreter, "ide_turtle_canvas")
                        and self.interpreter.ide_turtle_canvas
                    ):
                        # IDE mode
                        canvas = self.interpreter.ide_turtle_canvas
                        if filled:
                            canvas.create_oval(
                                x - radius,
                                y - radius,
                                x + radius,
                                y + radius,
                                fill=color,
                                outline=color,
                                tags="game_objects",
                            )
                        else:
                            canvas.create_oval(
                                x - radius,
                                y - radius,
                                x + radius,
                                y + radius,
                                outline=color,
                                tags="game_objects",
                            )
                    elif self.pygame_screen:
                        # Pygame mode
                        import pygame

                        if filled:
                            pygame.draw.circle(
                                self.pygame_screen, self.current_color, (x, y), radius
                            )
                        else:
                            pygame.draw.circle(
                                self.pygame_screen,
                                self.current_color,
                                (x, y),
                                radius,
                                2,
                            )
                except ValueError:
                    self.interpreter.log_output("Error: Invalid GAMECIRCLE parameters")
        elif cmd == "GAMEKEY":
            # GAMEKEY() - get pressed key (placeholder - would need real input handling)
            self.interpreter.variables["LAST_KEY"] = ""  # Placeholder
            self.interpreter.log_output("🎮 Key input checked")
        else:
            # Generic game command
            self.interpreter.log_output(f"🎮 Game command: {command}")
        return "continue"

    def _handle_multiplayer_commands(self, command, cmd, parts):
        """Handle multiplayer and networking commands"""
        # Placeholder for multiplayer commands
        self.interpreter.log_output(f"Multiplayer command: {command}")
        return "continue"

    def _handle_audio_commands(self, command, cmd, parts):
        """Handle audio system commands"""
        # Placeholder for audio commands
        self.interpreter.log_output(f"Audio command: {command}")
        return "continue"
