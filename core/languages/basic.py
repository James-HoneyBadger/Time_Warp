
"""
TW BASIC Language Executor
==================================

- Implements the TW BASIC language for the Time_Warp IDE, combining the features of
- BASIC, PILOT, and Logo into a single educational programming environment.

- Language Features:
- Line-numbered and structured BASIC syntax
- PILOT-style colon-prefixed commands (T:, A:, J:, Y:, N:, etc.)
- Logo-style turtle graphics commands (FORWARD, LEFT, RIGHT, etc.)
- Variable assignment, arrays, and interpolation
- Control flow: IF/THEN/ELSE, FOR/NEXT, REPEAT, GOTO, GOSUB, J:
- Turtle graphics, pen/color control, shapes, and screen commands
- Input/output, file I/O, math/string/array functions
- Game, multimedia, and advanced commands

This executor maintains backward compatibility with existing BASIC, PILOT, and Logo programs,
while providing a modern, consistent syntax for new programs.
"""

import math
import random
import re
import time


class TwBasicInterpreter:
    """
    Interpreter for the TW BASIC language (BASIC + PILOT + Logo).
    Standalone, does not require a unified interpreter.
    """

    def __init__(self):
        self.pygame_screen = None
        self.pygame_clock = None
        self.current_color = (255, 255, 255)  # White default
        self.variables = {}
        self.output_callback = None
        self.program_lines = []
        self.current_line = 0
        self.running = False
        self.ide_turtle_canvas = None
        self.for_stack = []
        self.stack = []
        self.open_files = {}

    def set_output_callback(self, callback):
        # Set the output callback used by the IDE. Keep a debug trace when set.
        self.output_callback = callback
        try:
            # Output callback registered
            pass
        except Exception:
            pass

    def log_output(self, text):
        # Route output to the registered callback or fallback to stdout
        if self.output_callback:
            try:
                self.output_callback(text)
            except Exception as e:
                # If callback fails, fall back to printing the text
                try:
                    print(text)
                except Exception:
                    pass
        else:
            try:
                print(text)
            except Exception:
                pass

    def debug_output(self, text):
        # For debugging - no-op in production
        pass

    def evaluate_expression(self, expr):
        """Simple expression evaluator for BASIC"""
        try:
            # Remove spaces
            expr = expr.replace(" ", "")
            
            # Handle variables
            for var_name, var_value in self.variables.items():
                expr = re.sub(r'\b' + re.escape(var_name) + r'\b', str(var_value), expr)
            
            # Evaluate the expression
            result = eval(expr, {"__builtins__": {}}, {})
            return result
        except Exception as e:
            raise ValueError(f"Expression error: {e}")

    def execute_line(self, line):
        """Execute a single line of BASIC code"""
        return self.execute_command(line)

    def get_user_input(self, prompt):
        """Get user input - placeholder for now"""
        # This would need to be implemented with a proper input mechanism.
        # In non-interactive/test environments (pytest capture), input() may raise OSError/EOFError.
        # Catch these and return an empty string so tests don't block.
        try:
            return input(prompt) if prompt else input()
        except (EOFError, OSError):
            # Non-interactive environment: return empty string to allow tests to proceed
            return ""

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
            import os

            import pygame

            # Check if display is available
            display = os.environ.get("DISPLAY")
            self.log_output(f"🖥️  Display environment: {display}")

            pygame.init()

            # Check available drivers
            drivers = pygame.display.get_driver()
            self.log_output(f"🎮 Pygame video driver: {drivers}")

            self.pygame_screen = pygame.display.set_mode((width, height))
            pygame.display.set_caption(title)
            self.pygame_clock = pygame.time.Clock()
            self.pygame_screen.fill((0, 0, 0))  # Black background
            pygame.display.flip()

            self.log_output(
                f"✅ Pygame window created: {width}x{height} '{title}'"
            )
            return True
        except ImportError:
            self.log_output("❌ Error: pygame not available for graphics")
            return False
        except Exception as e:
            self.log_output(f"❌ Error initializing pygame: {e}")
            return False

    def execute_command(self, command):
        """
        Execute a TW BASIC (unified) command.
        Routes to BASIC, PILOT, or Logo handlers as appropriate.
        """
        try:
            command = command.strip()
            if not command:
                return "continue"

            # BASIC: Convert ? to PRINT for compatibility
            if command.startswith('?'):
                command = 'PRINT ' + command[1:].strip()

            # Strip inline comments (REM, ; comments)
            if "REM" in command:
                command = command.split("REM", 1)[0].strip()
            if ";" in command and not command.startswith("REPEAT"):
                command = command.split(";", 1)[0].strip()

            # Modern variable assignment (var = expr)
            if "=" in command and not command.upper().startswith(("IF", "FOR", "WHILE", "LET")):
                parts = command.split("=", 1)
                if len(parts) == 2:
                    var_name = parts[0].strip()
                    expr = parts[1].strip()
                    if var_name.replace("_", "").replace(" ", "").isalnum() and not var_name[0].isdigit():
                        try:
                            if expr.startswith("[") and expr.endswith("]"):
                                array_content = expr[1:-1].strip()
                                if array_content:
                                    elements = [e.strip() for e in array_content.split(",")]
                                    array_dict = {}
                                    for i, elem in enumerate(elements):
                                        try:
                                            if "." in elem or elem.isdigit() or (elem.startswith("-") and elem[1:].replace(".", "").isdigit()):
                                                array_dict[i] = float(elem) if "." in elem else int(elem)
                                            else:
                                                if (elem.startswith('"') and elem.endswith('"')) or (elem.startswith("'") and elem.endswith("'")):
                                                    array_dict[i] = elem[1:-1]
                                                else:
                                                    array_dict[i] = elem
                                        except Exception:
                                            array_dict[i] = elem
                                else:
                                    array_dict = {}
                                self.variables[var_name] = array_dict
                            else:
                                value = self.evaluate_expression(expr)
                                self.variables[var_name] = value
                            return "continue"
                        except Exception as e:
                            self.debug_output(f"Variable assignment error: {e}")
                            return "continue"

            # PILOT-style colon-prefixed commands
            if len(command) > 1 and command[1] == ":":
                cmd_type = command[:2]
                if cmd_type == "T:":
                    return self._handle_text_output(command)
                elif cmd_type == "A:":
                    return self._handle_accept_input(command)
                elif cmd_type == "Y:":
                    return self._handle_yes_condition(command)
                elif cmd_type == "N:":
                    return self._handle_no_condition(command)
                elif cmd_type == "J:":
                    return self._handle_jump(command)
                elif cmd_type == "M:":
                    return self._handle_match_jump(command)
                elif cmd_type == "MT":
                    return self._handle_match_text(command)
                elif cmd_type == "C:":
                    return self._handle_compute_or_return(command)
                elif cmd_type == "U:":
                    return self._handle_update_variable(command)
                elif cmd_type == "R:":
                    return self._handle_runtime_command(command)
                elif cmd_type == "GAME":
                    return self._handle_game_command(command)
                elif cmd_type == "AUDIO":
                    return self._handle_audio_command(command)
                elif cmd_type == "F:":
                    return self._handle_file_command(command)
                elif cmd_type == "W:":
                    return self._handle_web_command(command)
                elif cmd_type == "D:":
                    return self._handle_database_command(command)
                elif cmd_type == "S:":
                    return self._handle_string_command(command)
                elif cmd_type == "DT":
                    return self._handle_datetime_command(command)
                elif cmd_type == "MATH":
                    return self._handle_math_command(command)
                elif cmd_type == "BRANCH":
                    return self._handle_branch_command(command)
                elif cmd_type == "MULTIMEDIA":
                    return self._handle_multimedia_command(command)
                elif cmd_type == "STORAGE":
                    return self._handle_storage_command(command)
                elif cmd_type == "L:":
                    return "continue"  # Label definition

            # BASIC-style commands
            parts = command.split()
            if not parts:
                return "continue"
            cmd = parts[0].upper()

            if cmd == "LET":
                return self._handle_let(command)
            elif cmd == "PRINT":
                return self._handle_print(command)
            elif cmd == "INPUT":
                return self._handle_input(command, parts)
            elif cmd == "IF":
                return self._handle_if(command)
            elif cmd == "FOR":
                return self._handle_for(command)
            elif cmd == "NEXT":
                return self._handle_next(command)
            elif cmd == "GOTO":
                return self._handle_goto(command, parts)
            elif cmd == "GOSUB":
                return self._handle_gosub(command, parts)
            elif cmd == "RETURN":
                return self._handle_return()
            elif cmd == "DIM":
                return self._handle_dim(command, parts)
            elif cmd == "END":
                return "end"
            elif cmd == "REM":
                return "continue"

            # Logo-style turtle graphics commands
            if cmd in ["FORWARD", "FD"]:
                return self._handle_forward(parts)
            elif cmd in ["BACK", "BK", "BACKWARD"]:
                return self._handle_backward(parts)
            elif cmd in ["LEFT", "LT"]:
                return self._handle_left(parts)
            elif cmd in ["RIGHT", "RT"]:
                return self._handle_right(parts)
            elif cmd in ["PENUP", "PU"]:
                return self._handle_penup()
            elif cmd in ["PENDOWN", "PD"]:
                return self._handle_pendown()
            elif cmd in ["CLEARSCREEN", "CS"]:
                return self._handle_clearscreen()
            elif cmd == "HOME":
                return self._handle_home()
            elif cmd == "SETXY":
                return self._handle_setxy(parts)
            elif cmd in ["SETCOLOR", "SETCOLOUR", "COLOR"]:
                return self._handle_setcolor(parts)
            elif cmd == "SETPENSIZE":
                return self._handle_setpensize(parts)
            elif cmd in ["PENCOLOR", "PENCOLOUR"]:
                return self._handle_setcolor(parts)
            elif cmd in ["FILLCOLOR", "FILLCOLOUR"]:
                return self._handle_setfillcolor(parts)
            elif cmd == "BGCOLOR":
                return self._handle_setbgcolor(parts)
            elif cmd == "SETX":
                return self._handle_setx(parts)
            elif cmd == "SETY":
                return self._handle_sety(parts)
            elif cmd == "SETPOS":
                return self._handle_setpos(parts)
            elif cmd == "FONTSIZE":
                return self._handle_fontsize(parts)
            elif cmd == "FONTSTYLE":
                return self._handle_fontstyle(parts)
            elif cmd == "CIRCLE":
                return self._handle_circle(parts)
            elif cmd == "DOT":
                return self._handle_dot(parts)
            elif cmd == "RECT":
                return self._handle_rect(parts)
            elif cmd == "TEXT":
                return self._handle_text(parts)
            elif cmd == "SHOWTURTLE":
                return self._handle_showturtle()
            elif cmd == "HIDETURTLE":
                return self._handle_hideturtle()
            elif cmd == "REPEAT":
                return self._handle_repeat(command)

            # Macro commands
            if cmd == "DEFINE":
                return self._handle_define(command, parts[1] if len(parts) > 1 else "")
            if cmd == "CALL":
                return self._handle_call(parts[1] if len(parts) > 1 else "")

            # Mathematical functions
            if cmd in ["SIN", "COS", "TAN", "SQRT", "ABS", "INT", "RND"]:
                return self._handle_math_functions(cmd, parts)

            # String functions
            if cmd in ["LEN", "MID", "LEFT", "RIGHT", "INSTR", "STR", "VAL", "UPPER", "LOWER"]:
                return self._handle_string_functions(cmd, parts)

            # Array operations
            if cmd in ["SORT", "FIND", "SUM", "AVG", "MIN", "MAX"]:
                return self._handle_array_operations(cmd, parts)

            # Graphics commands
            if cmd in ["LINE", "BOX", "TRIANGLE", "ELLIPSE", "FILL"]:
                return self._handle_enhanced_graphics(cmd, parts)

            # Sound commands
            if cmd in ["BEEP", "PLAY", "SOUND", "NOTE", "PLAYNOTE", "SETSOUND"]:
                return self._handle_sound_commands(cmd, parts)

            # File operations
            if cmd in ["OPEN", "CLOSE", "READ", "WRITE", "EOF"]:
                return self._handle_file_commands(cmd, parts)

            # Unknown command
            self.log_output(f"Unknown TW BASIC command: {cmd}")

        except Exception as e:
            self.debug_output(f"TW BASIC command error: {e}")
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
                    value = self.evaluate_expression(expr)

                    # Handle array assignment
                    if "(" in var_name and ")" in var_name:
                        # Extract array name and indices
                        array_name = var_name[: var_name.index("(")]
                        indices_str = var_name[
                            var_name.index("(") + 1 : var_name.rindex(")")
                        ]
                        indices = [
                            int(self.evaluate_expression(idx.strip()))
                            for idx in indices_str.split(",")
                        ]

                        # Get or create array
                        if array_name not in self.variables:
                            self.variables[array_name] = {}

                        # Set array element
                        current = self.variables[array_name]
                        for idx in indices[:-1]:
                            if idx not in current:
                                current[idx] = {}
                            current = current[idx]
                        current[indices[-1]] = value
                    else:
                        # Simple variable assignment
                        self.variables[var_name] = value
                except Exception as e:
                    self.debug_output(f"Error in LET {assignment}: {e}")
        return "continue"

    def _handle_if(self, command):
        """Handle IF/THEN conditional statement with optional ELSE"""
        try:
            # Match IF ... THEN ... [ELSE ...] pattern
            # This regex captures the THEN part and optionally the ELSE part
            m = re.match(r"IF\s+(.+?)\s+THEN\s+(.+?)(?:\s+ELSE\s+(.+))?$", command, re.IGNORECASE)
            if m:
                cond_expr = m.group(1).strip()
                then_cmd = m.group(2).strip()
                else_cmd = m.group(3).strip() if m.group(3) else None

                try:
                    cond_val = self.evaluate_expression(cond_expr)
                except Exception:
                    cond_val = False

                if cond_val:
                    # Execute the THEN command
                    return self.execute_line(then_cmd)
                elif else_cmd:
                    # Execute the ELSE command
                    return self.execute_line(else_cmd)
        except Exception as e:
            self.debug_output(f"IF statement error: {e}")
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

                start_val = self.evaluate_expression(start_expr)
                end_val = self.evaluate_expression(end_expr)
                step_val = (
                    self.evaluate_expression(step_expr)
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
                self.variables[var_name] = start_val
                self.for_stack.append(
                    {
                        "var": var_name,
                        "end": end_val,
                        "step": step_val,
                        "for_line": self.current_line,
                    }
                )
        except Exception as e:
            self.debug_output(f"FOR statement error: {e}")
        return "continue"

    def _handle_print(self, command):
        """Handle PRINT output statement"""
        text = command[5:].strip()
        if not text:
            self.log_output("")
            return "continue"

        # Parse PRINT statement with proper comma and semicolon handling
        # NOTE: do not split on commas/semicolons that are inside parentheses
        parts = []
        current_part = ""
        in_quotes = False
        paren_depth = 0
        i = 0
        while i < len(text):
            char = text[i]
            if char == '"' and (i == 0 or text[i - 1] != "\\"):
                in_quotes = not in_quotes
                current_part += char
            elif not in_quotes:
                if char == '(':
                    paren_depth += 1
                    current_part += char
                elif char == ')':
                    paren_depth = max(0, paren_depth - 1)
                    current_part += char
                elif char in [",", ";"] and paren_depth == 0:
                    if current_part.strip():
                        parts.append(current_part.strip())
                        current_part = ""
                    parts.append(char)  # Keep the separator
                else:
                    current_part += char
            else:
                current_part += char
            i += 1

        if current_part.strip():
            parts.append(current_part.strip())

        # Process parts
        result_parts = []
        suppress_newline = False

        i = 0
        while i < len(parts):
            part = parts[i]
            if part == ";":
                suppress_newline = True
            elif part == ",":
                # Add tab/space separation
                result_parts.append("\t")
            else:
                # Evaluate the expression
                if part.startswith('"') and part.endswith('"'):
                    # String literal
                    result_parts.append(part[1:-1])
                else:
                    # Expression or variable
                    try:
                        evaluated = self.evaluate_expression(part)
                        if isinstance(evaluated, str):
                            result_parts.append(evaluated)
                        else:
                            result_parts.append(str(evaluated))
                    except Exception as e:
                        self.debug_output(f"Expression error in PRINT: {e}")
                        # For variables that failed evaluation, check if they exist directly
                        var_name = part.strip().upper()
                        if var_name in self.variables:
                            result_parts.append(str(self.variables[var_name]))
                        else:
                            result_parts.append(str(part))
            i += 1

        # Join parts and output
        result = "".join(result_parts)
        if suppress_newline:
            # For semicolon, we need to append without newline
            # This is a limitation - we'll just print normally for now
            self.log_output(result)
        else:
            self.log_output(result)
        return "continue"

    def _handle_rem(self, command):
        """Handle REM comment statement"""
        # Comment - ignore rest of the line
        return "continue"

    def _handle_input(self, command, parts):
        """Handle INPUT statement"""
        # Parse INPUT "prompt"; variable or INPUT variable
        input_text = command[5:].strip()  # Remove "INPUT"

        # Check if there's a semicolon separating prompt and variable
        if ";" in input_text:
            prompt_part, var_part = input_text.split(";", 1)
            prompt = prompt_part.strip().strip('"')
            var_name = var_part.strip()
        else:
            # No semicolon, assume just variable name
            prompt = f"Enter value for {input_text.strip()}:"
            var_name = input_text.strip()

        value = self.get_user_input(prompt)
        try:
            if "." in value:
                self.variables[var_name] = float(value)
            else:
                self.variables[var_name] = int(value)
        except Exception:
            self.variables[var_name] = value
        return "continue"

    def _handle_goto(self, command, parts):
        """Handle GOTO statement"""
                    if len(parts) >= 2:
                        try:
                            delay_ms = int(parts[1])
                            # use module-level time
                            time.sleep(delay_ms / 1000.0)  # Convert to seconds
                        except ValueError:
    def _handle_gosub(self, command, parts):
        """Handle GOSUB statement"""
        if len(parts) > 1:
            line_num = int(parts[1])
            # push next-line index
            self.stack.append(self.current_line + 1)
            for i, (num, _) in enumerate(self.program_lines):
                if num == line_num:
                    return f"jump:{i}"
        return "continue"

    def _handle_return(self):
        """Handle RETURN statement"""
        if self.stack:
            return f"jump:{self.stack.pop()}"
        return "continue"

    def _handle_next(self, command):
        """Handle NEXT statement"""
        try:
            parts = command.split()
            var_spec = parts[1] if len(parts) > 1 else None

            # Find matching FOR on the stack
            if not self.for_stack:
                # Log (not just debug) so tests can assert message
                self.log_output("NEXT without FOR")
                return "continue"

            # If var specified, search from top for match, else take top
            if var_spec:
                # strip possible commas
                var_spec = var_spec.strip()
                found_idx = None
                for i in range(len(self.for_stack) - 1, -1, -1):
                    if self.for_stack[i]["var"].upper() == var_spec.upper():
                        found_idx = i
                        break
                if found_idx is None:
                    self.debug_output(
                        f"NEXT for unknown variable {var_spec}"
                    )
                    return "continue"
                ctx = self.for_stack[found_idx]
                # remove any inner loops above this one? keep nested intact
                # Only pop if loop finishes
            else:
                ctx = self.for_stack[-1]
                found_idx = len(self.for_stack) - 1

            var_name = ctx["var"]
            step = int(ctx["step"])
            end_val = int(ctx["end"])

            # Ensure variable exists (treat as integer)
            current_val = self.variables.get(var_name, 0)
            try:
                current_val = int(current_val)
            except Exception:
                current_val = 0

            next_val = current_val + step
            self.variables[var_name] = int(next_val)

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
                    self.for_stack.pop(found_idx)
                except Exception:
                    pass
        except Exception as e:
            self.debug_output(f"NEXT statement error: {e}")
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

                    # Create multi-dimensional array as nested dicts
                    def create_array_dict(dims):
                        if len(dims) == 1:
                            # Create a dict with indices 0 to dims[0]
                            return {i: 0 for i in range(dims[0] + 1)}
                        else:
                            # Create nested dicts
                            return {i: create_array_dict(dims[1:]) for i in range(dims[0] + 1)}

                    array = create_array_dict(dimensions)

                    # Store the array
                    self.variables[array_name] = array
                    self.log_output(
                        f"Array {array_name} declared with dimensions {dimensions}"
                    )
        except Exception as e:
            self.debug_output(f"DIM statement error: {e}")
        return "continue"

    def _handle_math_functions(self, cmd, parts):
        """Handle mathematical functions"""
        try:
            if cmd == "SIN":
                # SIN(angle) - sine of angle in degrees
                if len(parts) >= 2:
                    # Handle both SIN(45) and SIN 45
                    arg = parts[1].strip()
                    if arg.startswith("(") and arg.endswith(")"):
                        arg = arg[1:-1]
                    angle = float(self.evaluate_expression(arg))
                    result = math.sin(math.radians(angle))
                    self.variables["RESULT"] = result
                    self.log_output(f"SIN({angle}°) = {result:.4f}")
                else:
                    self.log_output("SIN requires an angle parameter")
            elif cmd == "COS":
                # COS(angle) - cosine of angle in degrees
                if len(parts) >= 2:
                    arg = parts[1].strip()
                    if arg.startswith("(") and arg.endswith(")"):
                        arg = arg[1:-1]
                    angle = float(self.evaluate_expression(arg))
                    result = math.cos(math.radians(angle))
                    self.variables["RESULT"] = result
                    self.log_output(f"COS({angle}°) = {result:.4f}")
                else:
                    self.log_output("COS requires an angle parameter")
            elif cmd == "TAN":
                # TAN(angle) - tangent of angle in degrees
                if len(parts) >= 2:
                    arg = parts[1].strip()
                    if arg.startswith("(") and arg.endswith(")"):
                        arg = arg[1:-1]
                    angle = float(self.evaluate_expression(arg))
                    result = math.tan(math.radians(angle))
                    self.variables["RESULT"] = result
                    self.log_output(f"TAN({angle}°) = {result:.4f}")
                else:
                    self.log_output("TAN requires an angle parameter")
            elif cmd == "SQRT":
                # SQRT(value) - square root
                if len(parts) >= 2:
                    arg = parts[1].strip()
                    if arg.startswith("(") and arg.endswith(")"):
                        arg = arg[1:-1]
                    value = float(self.evaluate_expression(arg))
                    if value >= 0:
                        result = math.sqrt(value)
                        self.variables["RESULT"] = result
                        self.log_output(f"SQRT({value}) = {result:.4f}")
                    else:
                        self.log_output(
                            "SQRT requires a non-negative value"
                        )
                else:
                    self.log_output("SQRT requires a value parameter")
            elif cmd == "ABS":
                # ABS(value) - absolute value
                if len(parts) >= 2:
                    arg = parts[1].strip()
                    if arg.startswith("(") and arg.endswith(")"):
                        arg = arg[1:-1]
                    value = float(self.evaluate_expression(arg))
                    result = abs(value)
                    self.variables["RESULT"] = result
                    self.log_output(f"ABS({value}) = {result}")
                else:
                    self.log_output("ABS requires a value parameter")
            elif cmd == "INT":
                # INT(value) - integer part
                if len(parts) >= 2:
                    arg = parts[1].strip()
                    if arg.startswith("(") and arg.endswith(")"):
                        arg = arg[1:-1]
                    value = float(self.evaluate_expression(arg))
                    result = int(value)
                    self.variables["RESULT"] = result
                    self.log_output(f"INT({value}) = {result}")
                else:
                    self.log_output("INT requires a value parameter")
            elif cmd == "RND":
                # RND() or RND(max) - random number
                if len(parts) >= 2:
                    arg = parts[1].strip()
                    if arg.startswith("(") and arg.endswith(")"):
                        arg = arg[1:-1]
                    if arg:  # Has argument
                        max_val = float(self.evaluate_expression(arg))
                        result = random.uniform(0, max_val)
                    else:  # No argument
                        result = random.random()
                else:
                    result = random.random()
                self.variables["RESULT"] = result
                self.log_output(f"RND() = {result:.4f}")
        except Exception as e:
            self.debug_output(f"Math function error: {e}")
        return "continue"

    def _handle_string_functions(self, cmd, parts):
        """Handle string manipulation functions"""
        try:
            if cmd == "LEN":
                # LEN(string) - length of string
                if len(parts) >= 2:
                    arg = parts[1].strip()
                    if arg.startswith("(") and arg.endswith(")"):
                        arg = arg[1:-1]
                    text = str(self.evaluate_expression(arg))
                    result = len(text)
                    self.variables["RESULT"] = result
                    self.log_output(f"LEN('{text}') = {result}")
                else:
                    self.log_output("LEN requires a string parameter")
            elif cmd == "MID":
                # MID(string, start, length) - substring
                if len(parts) >= 4:
                    # Parse arguments: MID string, start, length
                    args_str = " ".join(parts[1:])
                    if args_str.startswith("(") and args_str.endswith(")"):
                        args_str = args_str[1:-1]
                    args = [arg.strip() for arg in args_str.split(",")]
                    if len(args) >= 3:
                        text = str(self.evaluate_expression(args[0]))
                        start = int(self.evaluate_expression(args[1])) - 1  # BASIC is 1-based
                        length = int(self.evaluate_expression(args[2]))
                        result = text[start : start + length]
                        self.variables["RESULT"] = result
                        self.log_output(
                            f"MID('{text}', {start+1}, {length}) = '{result}'"
                        )
                    else:
                        self.log_output("MID requires string, start, and length parameters")
                else:
                    self.log_output(
                        "MID requires string, start, and length parameters"
                    )
            elif cmd == "LEFT":
                # LEFT(string, length) - left substring
                if len(parts) >= 3:
                    args_str = " ".join(parts[1:])
                    if args_str.startswith("(") and args_str.endswith(")"):
                        args_str = args_str[1:-1]
                    args = [arg.strip() for arg in args_str.split(",")]
                    if len(args) >= 2:
                        text = str(self.evaluate_expression(args[0]))
                        length = int(self.evaluate_expression(args[1]))
                        result = text[:length]
                        self.variables["RESULT"] = result
                        self.log_output(
                            f"LEFT('{text}', {length}) = '{result}'"
                        )
                    else:
                        self.log_output(
                            "LEFT requires string and length parameters"
                        )
                else:
                    self.log_output(
                        "LEFT requires string and length parameters"
                    )
            elif cmd == "RIGHT":
                # RIGHT(string, length) - right substring
                if len(parts) >= 3:
                    args_str = " ".join(parts[1:])
                    if args_str.startswith("(") and args_str.endswith(")"):
                        args_str = args_str[1:-1]
                    args = [arg.strip() for arg in args_str.split(",")]
                    if len(args) >= 2:
                        text = str(self.evaluate_expression(args[0]))
                        length = int(self.evaluate_expression(args[1]))
                        result = text[-length:]
                        self.variables["RESULT"] = result
                        self.log_output(
                            f"RIGHT('{text}', {length}) = '{result}'"
                        )
                    else:
                        self.log_output(
                            "RIGHT requires string and length parameters"
                        )
                else:
                    self.log_output(
                        "RIGHT requires string and length parameters"
                    )
            elif cmd == "INSTR":
                # INSTR(string, search) - find substring position
                if len(parts) >= 3:
                    args_str = " ".join(parts[1:])
                    if args_str.startswith("(") and args_str.endswith(")"):
                        args_str = args_str[1:-1]
                    args = [arg.strip() for arg in args_str.split(",")]
                    if len(args) >= 2:
                        text = str(self.evaluate_expression(args[0]))
                        search = str(self.evaluate_expression(args[1]))
                        pos = text.find(search)
                        result = (
                            pos + 1 if pos != -1 else 0
                        )  # BASIC is 1-based, 0 means not found
                        self.variables["RESULT"] = result
                        self.log_output(
                            f"INSTR('{text}', '{search}') = {result}"
                        )
                    else:
                        self.log_output(
                            "INSTR requires string and search parameters"
                        )
                else:
                    self.log_output(
                        "INSTR requires string and search parameters"
                    )
            elif cmd == "STR":
                # STR(number) - convert number to string
                if len(parts) >= 2:
                    arg = parts[1].strip()
                    if arg.startswith("(") and arg.endswith(")"):
                        arg = arg[1:-1]
                    value = self.evaluate_expression(arg)
                    result = str(value)
                    self.variables["RESULT"] = result
                    self.log_output(f"STR({value}) = '{result}'")
                else:
                    self.log_output("STR requires a value parameter")
            elif cmd == "VAL":
                # VAL(string) - convert string to number
                if len(parts) >= 2:
                    arg = parts[1].strip()
                    if arg.startswith("(") and arg.endswith(")"):
                        arg = arg[1:-1]
                    text = str(self.evaluate_expression(arg))
                    try:
                        result = float(text)
                        self.variables["RESULT"] = result
                        self.log_output(f"VAL('{text}') = {result}")
                    except ValueError:
                        result = 0
                        self.variables["RESULT"] = result
                        self.log_output(
                            f"VAL('{text}') = {result} (conversion failed)"
                        )
                else:
                    self.log_output("VAL requires a string parameter")
        except Exception as e:
            self.debug_output(f"String function error: {e}")
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
                                    self.open_files = {}
                                self.open_files[handle] = file_obj
                                self.log_output(
                                    f"File '{filename}' opened as #{handle} for {mode}"
                                )
                            except Exception as e:
                                self.log_output(f"Error opening file: {e}")
                        else:
                            self.log_output(
                                "Invalid file mode. Use INPUT, OUTPUT, or APPEND"
                            )
                    else:
                        self.log_output("File handle must start with #")
                else:
                    self.log_output(
                        'OPEN syntax: OPEN "filename" FOR mode AS #handle'
                    )
            elif cmd == "CLOSE":
                # CLOSE #handle
                if len(parts) >= 2 and parts[1].startswith("#"):
                    handle = int(parts[1][1:])
                    if (
                        hasattr(self.interpreter, "open_files")
                        and handle in self.open_files
                    ):
                        self.open_files[handle].close()
                        del self.open_files[handle]
                        self.log_output(f"File #{handle} closed")
                    else:
                        self.log_output(f"File #{handle} not open")
                else:
                    self.log_output("CLOSE syntax: CLOSE #handle")
            elif cmd == "READ":
                # READ #handle, variable
                if len(parts) >= 3 and parts[1].startswith("#") and parts[2] == ",":
                    handle = int(parts[1][1:])
                    var_name = parts[3]
                    if (
                        hasattr(self.interpreter, "open_files")
                        and handle in self.open_files
                    ):
                        try:
                            line = (
                                self.open_files[handle].readline().strip()
                            )
                            if line:
                                # Try to parse as number, otherwise keep as string
                                try:
                                    self.variables[var_name] = float(line)
                                except ValueError:
                                    self.variables[var_name] = line
                                self.log_output(
                                    f"Read '{line}' into {var_name}"
                                )
                            else:
                                self.variables["EOF"] = True
                                self.log_output("End of file reached")
                        except Exception as e:
                            self.log_output(f"Error reading file: {e}")
                    else:
                        self.log_output(f"File #{handle} not open")
                else:
                    self.log_output("READ syntax: READ #handle, variable")
            elif cmd == "WRITE":
                # WRITE #handle, expression
                if len(parts) >= 3 and parts[1].startswith("#") and parts[2] == ",":
                    handle = int(parts[1][1:])
                    expr = " ".join(parts[3:])
                    if (
                        hasattr(self.interpreter, "open_files")
                        and handle in self.open_files
                    ):
                        try:
                            value = self.evaluate_expression(expr)
                            self.open_files[handle].write(str(value) + "\n")
                            self.log_output(
                                f"Wrote '{value}' to file #{handle}"
                            )
                        except Exception as e:
                            self.log_output(f"Error writing to file: {e}")
                    else:
                        self.log_output(f"File #{handle} not open")
                else:
                    self.log_output(
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
                        and handle in self.open_files
                    ):
                        try:
                            current_pos = self.open_files[handle].tell()
                            self.open_files[handle].readline()
                            eof = (
                                self.open_files[handle].tell()
                                == current_pos
                            )
                            self.open_files[handle].seek(
                                current_pos
                            )  # Reset position
                            self.variables["RESULT"] = eof
                            self.log_output(f"EOF(#{handle}) = {eof}")
                        except Exception:
                            self.variables["RESULT"] = True
                    else:
                        self.variables["RESULT"] = True
                else:
                    self.log_output("EOF syntax: EOF(#handle)")
        except Exception as e:
            self.debug_output(f"File command error: {e}")
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
                                    and self.ide_turtle_canvas
                                ):
                                    canvas = self.ide_turtle_canvas
                                    color_name = color if color else "black"
                                    canvas.draw_line(
                                        x1,
                                        y1,
                                        x2,
                                        y2,
                                        color=color_name
                                    )
                                    self.log_output(
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
                                    self.log_output(
                                        f"Drew line from ({x1},{y1}) to ({x2},{y2})"
                                    )
                                else:
                                    self.log_output(
                                        "Graphics not initialized"
                                    )
                            else:
                                self.log_output("Invalid LINE coordinates")
                        else:
                            self.log_output(
                                "LINE syntax: LINE (x1,y1)-(x2,y2) [,color]"
                            )
                    else:
                        self.log_output(
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
                            and self.ide_turtle_canvas
                        ):
                            canvas = self.ide_turtle_canvas
                            canvas.draw_rectangle(
                                x,
                                y,
                                x + width,
                                y + height,
                                filled=filled,
                                color="black"
                            )
                            self.log_output(
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
                            self.log_output(
                                f"Drew {'filled ' if filled else ''}box at ({x},{y}) size {width}x{height}"
                            )
                        else:
                            self.log_output("Graphics not initialized")
                    else:
                        self.log_output("Invalid BOX coordinates")
                else:
                    self.log_output(
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
                                and self.ide_turtle_canvas
                            ):
                                canvas = self.ide_turtle_canvas
                                canvas.draw_polygon(
                                    points,
                                    filled=filled,
                                    color="black"
                                )
                                self.log_output(
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
                                self.log_output(
                                    f"Drew {'filled ' if filled else ''}triangle"
                                )
                            else:
                                self.log_output("Graphics not initialized")
                        else:
                            self.log_output("Invalid TRIANGLE coordinates")
                    else:
                        self.log_output(
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
                            and self.ide_turtle_canvas
                        ):
                            canvas = self.ide_turtle_canvas
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
                            self.log_output(
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
                            self.log_output(
                                f"Drew {'filled ' if filled else ''}ellipse at ({x},{y}) size {width}x{height}"
                            )
                        else:
                            self.log_output("Graphics not initialized")
                    else:
                        self.log_output("Invalid ELLIPSE coordinates")
                else:
                    self.log_output(
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
                            and self.ide_turtle_canvas
                        ):
                            canvas = self.ide_turtle_canvas
                            canvas.create_oval(
                                x - 5,
                                y - 5,
                                x + 5,
                                y + 5,
                                fill=color,
                                tags="game_objects",
                            )
                            self.log_output(
                                f"Flood fill at ({x},{y}) with {color}"
                            )
                        elif self.pygame_screen:
                            import pygame

                            pygame.draw.circle(
                                self.pygame_screen, self.current_color, (x, y), 5
                            )
                            self.log_output(
                                f"Flood fill at ({x},{y}) with {color}"
                            )
                        else:
                            self.log_output("Graphics not initialized")
                    else:
                        self.log_output("Invalid FILL coordinates")
                else:
                    self.log_output("FILL syntax: FILL (x,y) [,color]")
        except Exception as e:
            self.debug_output(f"Enhanced graphics error: {e}")
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
                    self.log_output(f"Beep: {frequency}Hz for {duration}s")
                except ImportError:
                    # On non-Windows systems, just log
                    self.log_output(
                        f"Beep: {frequency}Hz for {duration}s (simulated)"
                    )
            elif cmd == "PLAY":
                # PLAY "note" or PLAY frequency [, duration]
                if len(parts) >= 2:
                    # Handle cases like PLAY "C4", 0.5 where comma is attached
                    note_part = parts[1]
                    if note_part.endswith(","):
                        note_part = note_part[:-1]  # Remove trailing comma
                    note_or_freq = note_part.strip('"')

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

                    duration = 0.5
                    if len(parts) >= 3:
                        duration_part = parts[2]
                        try:
                            duration = float(duration_part)
                        except ValueError:
                            duration = 0.5

                    try:
                        import winsound

                        winsound.Beep(int(frequency), int(duration * 1000))
                        self.log_output(
                            f"Played {note_or_freq} for {duration}s"
                        )
                    except ImportError:
                        self.log_output(
                            f"Played {note_or_freq} for {duration}s (simulated)"
                        )
                else:
                    self.log_output("PLAY syntax: PLAY note [,duration]")
            elif cmd == "SOUND":
                # SOUND frequency, duration, volume
                if len(parts) >= 3:
                    frequency = float(parts[1])
                    duration = float(parts[2])
                    volume = float(parts[3]) if len(parts) > 3 else 1.0

                    self.log_output(
                        f"Sound: {frequency}Hz, {duration}s, volume {volume}"
                    )
                else:
                    self.log_output(
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
                            self.log_output(
                                f"Note: {note}{octave} for {duration}s"
                            )
                        except ImportError:
                            self.log_output(
                                f"Note: {note}{octave} for {duration}s (simulated)"
                            )
                    else:
                        self.log_output("Invalid note name")
                else:
                    self.log_output(
                        "NOTE syntax: NOTE note, octave [,duration]"
                    )
        except Exception as e:
            self.debug_output(f"Sound command error: {e}")
        return "continue"

    def _handle_array_operations(self, cmd, parts):
        """Handle array operations"""
        try:
            if cmd == "SORT":
                # SORT array_name
                if len(parts) >= 2:
                    array_name = parts[1]
                    if array_name in self.variables:
                        array = self.variables[array_name]
                        if isinstance(array, dict):
                            try:
                                # Convert dict values to list, sort, and convert back
                                values = list(array.values())
                                sorted_values = sorted(values)
                                # Reassign back to dict indices
                                for i, val in enumerate(sorted_values):
                                    if i in array:
                                        array[i] = val
                                self.log_output(
                                    f"Array {array_name} sorted"
                                )
                            except Exception:
                                self.log_output(
                                    "Array contains non-comparable elements"
                                )
                        else:
                            self.log_output(f"{array_name} is not an array")
                    else:
                        self.log_output(f"Array {array_name} not found")
                else:
                    self.log_output("SORT syntax: SORT array_name")
            elif cmd == "FIND":
                # FIND array_name, value
                if len(parts) >= 3:
                    array_name = parts[1]
                    search_value = self.evaluate_expression(parts[2])

                    if array_name in self.variables:
                        array = self.variables[array_name]
                        if isinstance(array, dict):
                            try:
                                for idx, val in array.items():
                                    if val == search_value:
                                        self.variables["RESULT"] = idx
                                        self.log_output(
                                            f"Found {search_value} at index {idx} in {array_name}"
                                        )
                                        return "continue"
                                self.variables["RESULT"] = -1
                                self.log_output(
                                    f"Value {search_value} not found in {array_name}"
                                )
                            except Exception:
                                self.variables["RESULT"] = -1
                                self.log_output(
                                    f"Error searching in {array_name}"
                                )
                        else:
                            self.log_output(f"{array_name} is not an array")
                    else:
                        self.log_output(f"Array {array_name} not found")
                else:
                    self.log_output("FIND syntax: FIND array_name, value")
            elif cmd in ["SUM", "AVG", "MIN", "MAX"]:
                # SUM/AVG/MIN/MAX array_name
                if len(parts) >= 2:
                    array_name = parts[1]
                    if array_name in self.variables:
                        array = self.variables[array_name]
                        if isinstance(array, dict) and array:
                            try:
                                values = list(array.values())
                                if cmd == "SUM":
                                    result = sum(values)
                                    operation = "sum"
                                elif cmd == "AVG":
                                    result = sum(values) / len(values)
                                    operation = "average"
                                elif cmd == "MIN":
                                    result = min(values)
                                    operation = "minimum"
                                elif cmd == "MAX":
                                    result = max(values)
                                    operation = "maximum"

                                self.variables["RESULT"] = result
                                self.log_output(
                                    f"Array {array_name} {operation}: {result}"
                                )
                            except Exception:
                                self.log_output(
                                    "Array contains non-numeric elements"
                                )
                        else:
                            self.log_output(
                                f"{array_name} is not a valid array"
                            )
                    else:
                        self.log_output(f"Array {array_name} not found")
                else:
                    self.log_output(f"{cmd} syntax: {cmd} array_name")
        except Exception as e:
            self.debug_output(f"Array operation error: {e}")
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
                    self.log_output(
                        f"🎮 Game screen initialized: {width}x{height} - {title}"
                    )

                    # Initialize graphics - either IDE canvas or standalone pygame
                    if (
                        hasattr(self.interpreter, "ide_turtle_canvas")
                        and self.ide_turtle_canvas
                    ):
                        # IDE mode - use turtle canvas
                        canvas = self.ide_turtle_canvas
                        canvas.delete("all")  # Clear canvas
                        canvas.config(
                            width=min(width, 600), height=min(height, 400)
                        )  # Limit size
                        canvas.create_text(
                            width // 2, 20, text=title, font=("Arial", 16), fill="white"
                        )
                        self.log_output(
                            "🎨 Graphics canvas initialized for game"
                        )
                    else:
                        # Standalone mode - use pygame
                        self._init_pygame_graphics(width, height, title)
                        self.log_output(
                            "🎮 Pygame graphics initialized for standalone game"
                        )
                except ValueError:
                    self.log_output("Error: Invalid GAMESCREEN parameters")
        elif cmd == "GAMEBG":
            # GAMEBG r, g, b - set background color
            if len(parts) >= 4:
                try:
                    r = int(parts[1].rstrip(","))
                    g = int(parts[2].rstrip(","))
                    b = int(parts[3].rstrip(","))
                    color = f"#{r:02x}{g:02x}{b:02x}"
                    self.log_output(
                        f"🎨 Background color set to RGB({r},{g},{b})"
                    )

                    if (
                        hasattr(self.interpreter, "ide_turtle_canvas")
                        and self.ide_turtle_canvas
                    ):
                        # IDE mode
                        self.ide_turtle_canvas.config(bg=color)
                    elif self.pygame_screen:
                        # Pygame mode
                        self.pygame_screen.fill((r, g, b))
                except ValueError:
                    self.log_output("Error: Invalid GAMEBG color values")
        elif cmd == "GAMELOOP":
            self.log_output("🔄 Game loop started")
        elif cmd == "GAMEEND":
            self.log_output("🎮 Game ended")
        elif cmd == "GAMECLEAR":
            # Clear the game screen
            self.log_output("🧹 Game screen cleared")
            if (
                hasattr(self.interpreter, "ide_turtle_canvas")
                and self.ide_turtle_canvas
            ):
                # IDE mode
                self.ide_turtle_canvas.delete("game_objects")
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
                    self.variables["GAME_COLOR"] = f"#{r:02x}{g:02x}{b:02x}"
                    self.current_color = (r, g, b)  # Store for pygame
                    self.log_output(
                        f"🎨 Drawing color set to RGB({r},{g},{b})"
                    )
                except ValueError:
                    self.log_output("Error: Invalid GAMECOLOR values")
        elif cmd == "GAMEPOINT":
            # GAMEPOINT x, y - draw a point
            if len(parts) >= 3:
                try:
                    x = int(parts[1].rstrip(","))
                    y = int(parts[2].rstrip(","))
                    color = self.variables.get("GAME_COLOR", "#FFFFFF")

                    if (
                        hasattr(self.interpreter, "ide_turtle_canvas")
                        and self.ide_turtle_canvas
                    ):
                        # IDE mode
                        canvas = self.ide_turtle_canvas
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
                    self.log_output("Error: Invalid GAMEPOINT coordinates")
        elif cmd == "GAMERECT":
            # GAMERECT x, y, width, height, filled
            if len(parts) >= 6:
                try:
                    x = int(parts[1].rstrip(","))
                    y = int(parts[2].rstrip(","))
                    width = int(parts[3].rstrip(","))
                    height = int(parts[4].rstrip(","))
                    filled = int(parts[5])
                    color = self.variables.get("GAME_COLOR", "#FFFFFF")

                    if (
                        hasattr(self.interpreter, "ide_turtle_canvas")
                        and self.ide_turtle_canvas
                    ):
                        # IDE mode
                        canvas = self.ide_turtle_canvas
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
                    self.log_output("Error: Invalid GAMERECT parameters")
        elif cmd == "GAMELOOP":
            self.log_output("🔄 Game loop started")
        elif cmd == "GAMETEXT":
            # GAMETEXT x, y, "text"
            if len(parts) >= 4:
                try:
                    x = int(parts[1].rstrip(","))
                    y = int(parts[2].rstrip(","))
                    text = " ".join(parts[3:]).strip('"')
                    color = self.variables.get("GAME_COLOR", "#FFFFFF")

                    if (
                        hasattr(self.interpreter, "ide_turtle_canvas")
                        and self.ide_turtle_canvas
                    ):
                        # IDE mode
                        canvas = self.ide_turtle_canvas
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
                    self.log_output("Error: Invalid GAMETEXT parameters")
        elif cmd == "GAMEUPDATE":
            # Update/refresh the display
            if (
                hasattr(self.interpreter, "ide_turtle_canvas")
                and self.ide_turtle_canvas
            ):
                # IDE mode
                self.ide_turtle_canvas.update()
                self.log_output("🔄 Display updated")
            elif self.pygame_screen:
                # Pygame mode
                import pygame

                pygame.display.flip()
                self.log_output("🔄 Pygame display updated")
        elif cmd == "GAMEDELAY":
            # GAMEDELAY milliseconds - delay for frame rate control
            if len(parts) >= 2:
                try:
                    delay_ms = int(parts[1])
                    import time

                    time.sleep(delay_ms / 1000.0)  # Convert to seconds
                except ValueError:
                    self.log_output("Error: Invalid GAMEDELAY parameter")
        elif cmd == "GAMECIRCLE":
            # GAMECIRCLE x, y, radius, filled (for 2-param version, assume filled=0)
            if len(parts) >= 4:
                try:
                    x = int(parts[1].rstrip(","))
                    y = int(parts[2].rstrip(","))
                    radius = int(parts[3].rstrip(","))
                    filled = int(parts[4]) if len(parts) >= 5 else 0  # Default unfilled
                    color = self.variables.get("GAME_COLOR", "#FFFFFF")

                    if (
                        hasattr(self.interpreter, "ide_turtle_canvas")
                        and self.ide_turtle_canvas
                    ):
                        # IDE mode
                        canvas = self.ide_turtle_canvas
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
                    self.log_output("Error: Invalid GAMECIRCLE parameters")
        elif cmd == "GAMEKEY":
            # GAMEKEY() - get pressed key (placeholder - would need real input handling)
            self.variables["LAST_KEY"] = ""  # Placeholder
            self.log_output("🎮 Key input checked")
        else:
            # Generic game command
            self.log_output(f"🎮 Game command: {command}")
        return "continue"

    def _handle_multiplayer_commands(self, command, cmd, parts):
        """Handle multiplayer and networking commands"""
        # Placeholder for multiplayer commands
        self.log_output(f"Multiplayer command: {command}")
        return "continue"

    def _handle_audio_commands(self, command, cmd, parts):
        """Handle audio system commands"""
        # Placeholder for audio commands
        self.log_output(f"Audio command: {command}")
        return "continue"
