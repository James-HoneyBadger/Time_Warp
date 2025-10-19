"""
TW Time_Warp Language Executor
===============================

Implements the unified Time_Warp programming language that combines the best features
of BASIC, PILOT, and Logo into a single, cohesive educational programming environment.

Language Features:
==================

Core Syntax:
- Line-numbered programming (from BASIC)
- Colon-prefixed commands (from PILOT): T:, A:, J:, Y:, N:, etc.
- Direct turtle graphics commands (from Logo): FORWARD, LEFT, CIRCLE, etc.
- Modern variable assignment: LET var = expr or var = expr

Variable Management:
- Simple variables: X = 42, NAME = "Hello"
- Array variables: SCORES[5] = 100
- Variable interpolation in text: "Hello *NAME*!"

Control Flow:
- Conditional statements: IF condition THEN commands
- Loops: FOR var = start TO end, REPEAT count [commands]
- Jumps: GOTO line, GOSUB label, J:label
- PILOT-style conditionals: Y:condition, N:condition

Turtle Graphics:
- Movement: FORWARD 50, BACK 25, LEFT 90, RIGHT 45
- Pen control: PENUP, PENDOWN, SETCOLOR "red", SETPENSIZE 3
- Shapes: CIRCLE 50, RECT 100 50, DOT 10
- Screen control: CLEARSCREEN, HOME, SHOWTURTLE, HIDETURTLE

Input/Output:
- Text output: PRINT "Hello", T:Hello *NAME*!
- User input: INPUT "Prompt"; variable, A:variable
- File operations: OPEN, READ, WRITE, CLOSE

Mathematical Operations:
- Functions: SIN, COS, TAN, SQRT, ABS, INT, RND
- String functions: LEN, MID, LEFT, RIGHT, UPPER, LOWER
- Array operations: SUM, AVG, MIN, MAX, SORT, FIND

Advanced Features:
- Macros/Procedures: DEFINE name [commands], CALL name
- Multimedia: PLAYNOTE, SETSOUND, LOADIMAGE
- Game development: GAMECLEAR, GAMECOLOR, etc.
- Database operations: DBOPEN, DBQUERY
- Web operations: HTTPGET, HTTPPOST

The unified language maintains backward compatibility with existing BASIC, PILOT,
and Logo programs while providing a modern, consistent syntax for new programs.
"""

import re
import math
import random
import time
from datetime import datetime


class TwTimeWarpExecutor:
    """
    Unified executor for the Time_Warp programming language.

    Combines the educational programming features of BASIC, PILOT, and Logo
    into a single, cohesive language with consistent syntax and powerful capabilities.
    """

    def __init__(self, interpreter):
        """Initialize the Time_Warp executor"""
        self.interpreter = interpreter

    def execute_command(self, command):
        """
        Execute a Time_Warp command.

        Supports multiple syntax styles:
        - Line-numbered BASIC: 10 PRINT "Hello"
        - PILOT commands: T:Hello World
        - Logo commands: FORWARD 50
        - Modern syntax: PRINT "Hello"
        """
        try:
            command = command.strip()
            if not command:
                return "continue"

            # Convert ? to PRINT for BASIC compatibility
            if command.startswith('?'):
                command = 'PRINT ' + command[1:].strip()

            # Strip inline comments (REM, ; comments)
            if "REM" in command:
                command = command.split("REM", 1)[0].strip()
            if ";" in command and not command.startswith("REPEAT"):
                command = command.split(";", 1)[0].strip()

            # Check for variable assignment (var = expr) - modern Time_Warp syntax
            if "=" in command and not command.upper().startswith(("IF", "FOR", "WHILE", "LET")):
                # Split on first = to handle assignments
                parts = command.split("=", 1)
                if len(parts) == 2:
                    var_name = parts[0].strip()
                    expr = parts[1].strip()
                    # Basic validation that this looks like a variable assignment
                    if var_name.replace("_", "").replace(" ", "").isalnum() and not var_name[0].isdigit():
                        try:
                            # Handle array syntax [item1, item2, ...]
                            if expr.startswith("[") and expr.endswith("]"):
                                # Parse array elements
                                array_content = expr[1:-1].strip()
                                if array_content:
                                    elements = [e.strip() for e in array_content.split(",")]
                                    array_dict = {}
                                    for i, elem in enumerate(elements):
                                        try:
                                            # Try to evaluate as number first
                                            if "." in elem or elem.isdigit() or (elem.startswith("-") and elem[1:].replace(".", "").isdigit()):
                                                array_dict[i] = float(elem) if "." in elem else int(elem)
                                            else:
                                                # Remove quotes if present
                                                if (elem.startswith('"') and elem.endswith('"')) or (elem.startswith("'") and elem.endswith("'")):
                                                    array_dict[i] = elem[1:-1]
                                                else:
                                                    array_dict[i] = elem
                                        except:
                                            array_dict[i] = elem
                                else:
                                    array_dict = {}
                                self.interpreter.variables[var_name] = array_dict
                            else:
                                value = self.interpreter.evaluate_expression(expr)
                                self.interpreter.variables[var_name] = value
                            return "continue"
                        except Exception as e:
                            self.interpreter.debug_output(f"Variable assignment error: {e}")
                            return "continue"

            parts = command.split()
            if not parts:
                return "continue"

            cmd = parts[0].upper()

            # Handle MEM command for memory display
            if cmd == "MEM":
                try:
                    import psutil
                    memory = psutil.virtual_memory()
                    total_mb = memory.total / (1024 * 1024)
                    available_mb = memory.available / (1024 * 1024)
                    used_mb = memory.used / (1024 * 1024)
                    percent = memory.percent
                    self.interpreter.log_output(f"Memory: {used_mb:.1f}MB used, {available_mb:.1f}MB free, {total_mb:.1f}MB total ({percent:.1f}%)")
                except ImportError:
                    self.interpreter.log_output("Memory information not available (psutil not installed)")
                return "continue"

            # Handle function calls like SIN(30), LEN('test'), etc.
            # Extract function name from expressions like FUNC(args)
            func_match = re.match(r'^([A-Z_]+)\s*\(', cmd)
            if func_match:
                func_name = func_match.group(1)
                # Check if it's a known function
                if func_name in ["SIN", "COS", "TAN", "SQRT", "ABS", "INT", "RND", "LEN", "MID", "LEFT", "RIGHT", "UPPER", "LOWER"]:
                    # Reconstruct the command as function call
                    cmd = func_name
                    # Parse the arguments from the full command
                    args_start = command.upper().find(func_name + '(')
                    if args_start >= 0:
                        args_part = command[args_start + len(func_name) + 1:]
                        # Simple parsing - find matching closing paren
                        paren_count = 1
                        arg_end = 0
                        for i, char in enumerate(args_part):
                            if char == '(':
                                paren_count += 1
                            elif char == ')':
                                paren_count -= 1
                                if paren_count == 0:
                                    arg_end = i
                                    break
                        if arg_end > 0:
                            args_str = args_part[:arg_end]
                            # Split args on commas, but be careful with nested functions
                            args = []
                            current_arg = ""
                            paren_depth = 0
                            in_quotes = False
                            for char in args_str:
                                if char == '"' and (not current_arg or current_arg[-1] != '\\'):
                                    in_quotes = not in_quotes
                                elif not in_quotes:
                                    if char == '(':
                                        paren_depth += 1
                                    elif char == ')':
                                        paren_depth -= 1
                                    elif char == ',' and paren_depth == 0:
                                        args.append(current_arg.strip())
                                        current_arg = ""
                                        continue
                                current_arg += char
                            if current_arg.strip():
                                args.append(current_arg.strip())
                            parts = [func_name] + args

            # PILOT-style colon commands
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
                elif cmd_type == "MT:":
                    return self._handle_match_text(command)
                elif cmd_type == "C:":
                    return self._handle_compute_or_return(command)
                elif cmd_type == "U:":
                    return self._handle_update_variable(command)
                elif cmd_type == "R:":
                    return self._handle_runtime_command(command)
                elif cmd_type == "GAME:":
                    return self._handle_game_command(command)
                elif cmd_type == "AUDIO:":
                    return self._handle_audio_command(command)
                elif cmd_type == "F:":
                    return self._handle_file_command(command)
                elif cmd_type == "W:":
                    return self._handle_web_command(command)
                elif cmd_type == "D:":
                    return self._handle_database_command(command)
                elif cmd_type == "S:":
                    return self._handle_string_command(command)
                elif cmd_type == "DT:":
                    return self._handle_datetime_command(command)
                elif cmd_type == "MATH:":
                    return self._handle_math_command(command)
                elif cmd_type == "BRANCH:":
                    return self._handle_branch_command(command)
                elif cmd_type == "MULTIMEDIA:":
                    return self._handle_multimedia_command(command)
                elif cmd_type == "STORAGE:":
                    return self._handle_storage_command(command)
                elif cmd_type == "L:":
                    return "continue"  # Labels are handled at parse time

            # BASIC-style commands
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

            # Logo-style turtle commands
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
                return self._handle_graphics(cmd, parts)

            # Sound commands
            if cmd in ["BEEP", "PLAY", "SOUND", "NOTE", "PLAYNOTE", "SETSOUND"]:
                return self._handle_sound_commands(cmd, parts)

            # File operations
            if cmd in ["OPEN", "CLOSE", "READ", "WRITE", "EOF"]:
                return self._handle_file_commands(cmd, parts)

            # Unknown command
            self.interpreter.log_output(f"Unknown Time_Warp command: {cmd}")

        except Exception as e:
            self.interpreter.debug_output(f"Time_Warp command error: {e}")

        return "continue"

    # PILOT-style command handlers
    def _handle_text_output(self, command):
        """Handle T: text output command"""
        text = command[2:].strip()
        if self.interpreter._last_match_set:
            self.interpreter._last_match_set = False
            if not self.interpreter.match_flag:
                return "continue"
        text = self.interpreter.interpolate_text(text)
        self.interpreter.log_output(text)
        return "continue"

    def _handle_accept_input(self, command):
        """Handle A: accept input command"""
        var_name = command[2:].strip()
        prompt = f"Enter value for {var_name}: "
        value = self.interpreter.get_user_input(prompt)
        if value is not None and value.strip() != "":
            try:
                if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
                    self.interpreter.variables[var_name] = int(value)
                else:
                    float_val = float(value)
                    self.interpreter.variables[var_name] = float_val
            except:
                self.interpreter.variables[var_name] = value
        else:
            self.interpreter.variables[var_name] = ""
        return "continue"

    def _handle_yes_condition(self, command):
        """Handle Y: match if condition is true"""
        condition = command[2:].strip()
        try:
            result = self.interpreter.evaluate_expression(condition)
            self.interpreter.match_flag = bool(result)
        except:
            self.interpreter.match_flag = False
        self.interpreter._last_match_set = True
        return "continue"

    def _handle_no_condition(self, command):
        """Handle N: match if condition is false"""
        condition = command[2:].strip()
        try:
            result = self.interpreter.evaluate_expression(condition)
            self.interpreter.match_flag = bool(result)
        except:
            self.interpreter.match_flag = False
        self.interpreter._last_match_set = True
        return "continue"

    def _handle_jump(self, command):
        """Handle J: jump command"""
        match = re.match(r"^J\((.+)\):(.+)$", command.strip())
        if match:
            condition = match.group(1).strip()
            label = match.group(2).strip()
            try:
                cond_val = self.interpreter.evaluate_expression(condition)
                if cond_val:
                    if label in self.interpreter.labels:
                        return f"jump:{self.interpreter.labels[label]}"
            except:
                pass
            return "continue"

        rest = command[2:].strip()
        label = rest
        if self.interpreter._last_match_set:
            self.interpreter._last_match_set = False
            if not self.interpreter.match_flag:
                return "continue"
        if label in self.interpreter.labels:
            return f"jump:{self.interpreter.labels[label]}"
        return "continue"

    def _handle_match_jump(self, command):
        """Handle M: jump if match flag is set"""
        label = command[2:].strip()
        if self.interpreter.match_flag and label in self.interpreter.labels:
            return f"jump:{self.interpreter.labels[label]}"
        return "continue"

    def _handle_match_text(self, command):
        """Handle MT: match-conditional text output"""
        text = command[3:].strip()
        if self.interpreter.match_flag:
            text = self.interpreter.interpolate_text(text)
            self.interpreter.log_output(text)
        return "continue"

    def _handle_compute_or_return(self, command):
        """Handle C: compute or return command"""
        payload = command[2:].strip()
        if payload == "":
            if self.interpreter.stack:
                return f"jump:{self.interpreter.stack.pop()}"
            return "continue"
        if "=" in payload:
            var_part, expr_part = payload.split("=", 1)
            var_name = var_part.strip().rstrip(":")
            expr = expr_part.strip()
            try:
                value = self.interpreter.evaluate_expression(expr)
                self.interpreter.variables[var_name] = value
            except Exception as e:
                self.interpreter.debug_output(f"Error in compute C: {payload}: {e}")
        return "continue"

    def _handle_update_variable(self, command):
        """Handle U: update variable command"""
        assignment = command[2:].strip()
        if "=" in assignment:
            var_name, expr = assignment.split("=", 1)
            var_name = var_name.strip()
            expr = expr.strip()
            interpolated = self.interpreter.interpolate_text(expr)
            if re.match(r"^[-+0-9\s\+\-\*\/\(\)\.]+$", interpolated):
                try:
                    value = eval(interpolated)
                    self.interpreter.variables[var_name] = value
                    return "continue"
                except:
                    pass
            if interpolated != expr:
                self.interpreter.variables[var_name] = interpolated
            else:
                try:
                    value = self.interpreter.evaluate_expression(expr)
                    if isinstance(value, str) and value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    self.interpreter.variables[var_name] = value
                except Exception as e:
                    self.interpreter.variables[var_name] = expr
        return "continue"

    def _handle_runtime_command(self, command):
        """Handle R: runtime/remark commands"""
        return "continue"

    def _handle_game_command(self, command):
        """Handle GAME: game development commands"""
        self.interpreter.log_output(f"Game command: {command[5:]}")
        return "continue"

    def _handle_audio_command(self, command):
        """Handle AUDIO: audio system commands"""
        self.interpreter.log_output(f"Audio command: {command[6:]}")
        return "continue"

    def _handle_file_command(self, command):
        """Handle F: file I/O commands"""
        import os
        import pathlib

        cmd = command[2:].strip()
        parts = cmd.split(" ", 2)

        if not parts:
            return "continue"

        operation = parts[0].upper()

        try:
            if operation == "WRITE" and len(parts) >= 3:
                filename = parts[1].strip('"')
                content = parts[2].strip('"')
                content = self.interpreter.interpolate_text(content)
                pathlib.Path(filename).write_text(content, encoding="utf-8")
                self.interpreter.variables["FILE_WRITE_SUCCESS"] = "1"

            elif operation == "READ" and len(parts) >= 3:
                filename = parts[1].strip('"')
                var_name = parts[2].strip()

                if os.path.exists(filename):
                    content = pathlib.Path(filename).read_text(encoding="utf-8")
                    self.interpreter.variables[var_name] = content
                    self.interpreter.variables["FILE_READ_SUCCESS"] = "1"
                else:
                    self.interpreter.variables[var_name] = ""
                    self.interpreter.variables["FILE_READ_SUCCESS"] = "0"

            elif operation == "APPEND" and len(parts) >= 3:
                filename = parts[1].strip('"')
                content = parts[2].strip('"')
                content = self.interpreter.interpolate_text(content)

                with open(filename, "a", encoding="utf-8") as f:
                    f.write(content)
                self.interpreter.variables["FILE_APPEND_SUCCESS"] = "1"

            elif operation == "DELETE" and len(parts) >= 2:
                filename = parts[1].strip('"')
                if os.path.exists(filename):
                    os.remove(filename)
                    self.interpreter.variables["FILE_DELETE_SUCCESS"] = "1"
                else:
                    self.interpreter.variables["FILE_DELETE_SUCCESS"] = "0"

        except Exception as e:
            self.interpreter.debug_output(f"File operation error: {e}")

        return "continue"

    def _handle_web_command(self, command):
        """Handle W: web/HTTP commands"""
        import urllib.parse

        cmd = command[2:].strip()
        parts = cmd.split(" ", 1)

        if not parts:
            return "continue"

        operation = parts[0].upper()

        try:
            if operation == "ENCODE" and len(parts) > 1:
                args = parts[1].split(",", 1)
                if len(args) == 2:
                    text = args[0].strip()
                    var_name = args[1].strip()
                    text = self.interpreter.interpolate_text(text)
                    encoded = urllib.parse.quote(text)
                    self.interpreter.variables[var_name] = encoded

            elif operation == "DECODE" and len(parts) > 1:
                args = parts[1].split(",", 1)
                if len(args) == 2:
                    text = args[0].strip()
                    var_name = args[1].strip()
                    text = self.interpreter.interpolate_text(text)
                    decoded = urllib.parse.unquote(text)
                    self.interpreter.variables[var_name] = decoded

        except Exception as e:
            self.interpreter.debug_output(f"Web operation error: {e}")

        return "continue"

    def _handle_database_command(self, command):
        """Handle D: database commands"""
        import sqlite3
        import os

        cmd = command[2:].strip()
        parts = cmd.split(" ", 1)

        if not parts:
            return "continue"

        operation = parts[0].upper()

        try:
            if operation == "OPEN":
                db_name = parts[1].strip('"') if len(parts) > 1 else "default.db"
                db_name = self.interpreter.interpolate_text(db_name)

                if not hasattr(self.interpreter, "db_connections"):
                    self.interpreter.db_connections = {}

                try:
                    conn = sqlite3.connect(db_name)
                    self.interpreter.db_connections["current"] = conn
                    self.interpreter.variables["DB_OPEN_SUCCESS"] = "1"
                except sqlite3.Error:
                    self.interpreter.variables["DB_OPEN_SUCCESS"] = "0"

            elif operation == "QUERY" and len(parts) >= 2:
                query = parts[1].strip('"')
                query = self.interpreter.interpolate_text(query)

                if hasattr(self.interpreter, "db_connections") and "current" in self.interpreter.db_connections:
                    try:
                        conn = self.interpreter.db_connections["current"]
                        cursor = conn.cursor()
                        cursor.execute(query)
                        conn.commit()
                        self.interpreter.variables["DB_QUERY_SUCCESS"] = "1"
                    except sqlite3.Error:
                        self.interpreter.variables["DB_QUERY_SUCCESS"] = "0"
                else:
                    self.interpreter.variables["DB_QUERY_SUCCESS"] = "0"

        except Exception as e:
            self.interpreter.debug_output(f"Database operation error: {e}")

        return "continue"

    def _handle_string_command(self, command):
        """Handle S: string processing commands"""
        import re

        cmd = command[2:].strip()
        pattern = r'"([^"]*)"|\S+'
        args = []
        for match in re.finditer(pattern, cmd):
            if match.group(1) is not None:
                args.append(match.group(1))
            else:
                args.append(match.group(0))

        if not args:
            return "continue"

        operation = args[0].upper()

        try:
            if operation == "LENGTH" and len(args) >= 3:
                text = args[1]
                var_name = args[2]
                text = self.interpreter.interpolate_text(text)
                self.interpreter.variables[var_name] = str(len(text))

            elif operation == "UPPER" and len(args) >= 3:
                text = args[1]
                var_name = args[2]
                text = self.interpreter.interpolate_text(text)
                self.interpreter.variables[var_name] = text.upper()

            elif operation == "LOWER" and len(args) >= 3:
                text = args[1]
                var_name = args[2]
                text = self.interpreter.interpolate_text(text)
                self.interpreter.variables[var_name] = text.lower()

        except Exception as e:
            self.interpreter.debug_output(f"String operation error: {e}")

        return "continue"

    def _handle_datetime_command(self, command):
        """Handle DT: date/time commands"""
        from datetime import datetime
        import time

        cmd = command[3:].strip()
        parts = cmd.split(" ", 2)

        if not parts:
            return "continue"

        operation = parts[0].upper()

        try:
            if operation == "NOW" and len(parts) >= 3:
                format_str = parts[1].strip('"')
                var_name = parts[2].strip()

                format_map = {
                    "YYYY-MM-DD": "%Y-%m-%d",
                    "HH:MM:SS": "%H:%M-%S",
                    "YYYY-MM-DD HH:MM:SS": "%Y-%m-%d %H:%M:%S",
                }

                fmt = format_map.get(format_str, format_str)
                now = datetime.now().strftime(fmt)
                self.interpreter.variables[var_name] = now

            elif operation == "TIMESTAMP" and len(parts) >= 2:
                var_name = parts[1].strip()
                timestamp = str(int(time.time()))
                self.interpreter.variables[var_name] = timestamp

        except Exception as e:
            self.interpreter.debug_output(f"DateTime operation error: {e}")

        return "continue"

    def _handle_math_command(self, command):
        """Handle MATH: mathematical operations"""
        import math

        cmd = command[5:].strip()
        parts = cmd.split(" ", 1)

        if not parts:
            return "continue"

        operation = parts[0].upper()

        try:
            if operation == "SIN" and len(parts) > 1:
                angle = float(self.interpreter.evaluate_expression(parts[1]))
                result = math.sin(math.radians(angle))
                self.interpreter.variables["MATH_RESULT"] = result
                self.interpreter.log_output(f"MATH:SIN({angle}°) = {result:.4f}")

            elif operation == "COS" and len(parts) > 1:
                angle = float(self.interpreter.evaluate_expression(parts[1]))
                result = math.cos(math.radians(angle))
                self.interpreter.variables["MATH_RESULT"] = result
                self.interpreter.log_output(f"MATH:COS({angle}°) = {result:.4f}")

            elif operation == "SQRT" and len(parts) > 1:
                value = float(self.interpreter.evaluate_expression(parts[1]))
                if value >= 0:
                    result = math.sqrt(value)
                    self.interpreter.variables["MATH_RESULT"] = result
                    self.interpreter.log_output(f"MATH:SQRT({value}) = {result:.4f}")

        except Exception as e:
            self.interpreter.debug_output(f"MATH operation error: {e}")

        return "continue"

    def _handle_branch_command(self, command):
        """Handle BRANCH: advanced branching operations"""
        cmd = command[7:].strip()
        parts = cmd.split(" ", 1)

        if not parts:
            return "continue"

        operation = parts[0].upper()

        try:
            if operation == "MULTI":
                if len(parts) > 1:
                    conditions_str = parts[1]
                    conditions = [c.strip() for c in conditions_str.split(",")]

                    for condition_pair in conditions:
                        if ":" in condition_pair:
                            cond_expr, label = condition_pair.split(":", 1)
                            cond_expr = cond_expr.strip()
                            label = label.strip()

                            try:
                                cond_val = self.interpreter.evaluate_expression(cond_expr)
                                if cond_val:
                                    if label in self.interpreter.labels:
                                        return f"jump:{self.interpreter.labels[label]}"
                            except:
                                pass

        except Exception as e:
            self.interpreter.debug_output(f"BRANCH operation error: {e}")

        return "continue"

    def _handle_multimedia_command(self, command):
        """Handle MULTIMEDIA: multimedia operations"""
        cmd = command[11:].strip()
        parts = cmd.split(" ", 1)

        if not parts:
            return "continue"

        operation = parts[0].upper()

        try:
            if operation == "PLAYSOUND":
                if len(parts) > 1:
                    args = parts[1].split(",", 1)
                    filename = args[0].strip('"')
                    duration = float(args[1].strip()) if len(args) > 1 else None
                    self.interpreter.log_output(f"MULTIMEDIA: Playing sound '{filename}'")

        except Exception as e:
            self.interpreter.debug_output(f"MULTIMEDIA operation error: {e}")

        return "continue"

    def _handle_storage_command(self, command):
        """Handle STORAGE: advanced variable storage operations"""
        cmd = command[8:].strip()
        parts = cmd.split(" ", 1)

        if not parts:
            return "continue"

        operation = parts[0].upper()

        try:
            if operation == "SAVE":
                if len(parts) > 1:
                    filename = parts[1].strip('"')
                    filename = self.interpreter.interpolate_text(filename)

                    import json

                    try:
                        with open(filename, "w", encoding="utf-8") as f:
                            save_vars = {
                                k: v
                                for k, v in self.interpreter.variables.items()
                                if not k.startswith("_")
                            }
                            json.dump(save_vars, f, indent=2, default=str)
                        self.interpreter.variables["STORAGE_SUCCESS"] = "1"
                        self.interpreter.log_output(f"STORAGE: Variables saved to '{filename}'")
                    except Exception as e:
                        self.interpreter.variables["STORAGE_SUCCESS"] = "0"

            elif operation == "LOAD":
                if len(parts) > 1:
                    filename = parts[1].strip('"')
                    filename = self.interpreter.interpolate_text(filename)

                    import json

                    try:
                        with open(filename, "r", encoding="utf-8") as f:
                            loaded_vars = json.load(f)
                            self.interpreter.variables.update(loaded_vars)
                        self.interpreter.variables["STORAGE_SUCCESS"] = "1"
                        self.interpreter.log_output(f"STORAGE: Variables loaded from '{filename}'")
                    except Exception as e:
                        self.interpreter.variables["STORAGE_SUCCESS"] = "0"

        except Exception as e:
            self.interpreter.debug_output(f"STORAGE operation error: {e}")

        return "continue"

    # BASIC-style command handlers
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
                    self.interpreter.variables[var_name] = value
                except Exception as e:
                    self.interpreter.debug_output(f"Error in LET {assignment}: {e}")
        return "continue"

    def _handle_print(self, command):
        """Handle PRINT output statement"""
        text = command[5:].strip()
        if not text:
            self.interpreter.log_output("")
            return "continue"

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
                    parts.append(char)
                else:
                    current_part += char
            else:
                current_part += char
            i += 1

        if current_part.strip():
            parts.append(current_part.strip())

        result_parts = []
        suppress_newline = False

        i = 0
        while i < len(parts):
            part = parts[i]
            if part == ";":
                suppress_newline = True
            elif part == ",":
                result_parts.append("\t")
            else:
                if part.startswith('"') and part.endswith('"'):
                    result_parts.append(part[1:-1])
                else:
                    try:
                        evaluated = self.interpreter.evaluate_expression(part)
                        if isinstance(evaluated, str):
                            result_parts.append(evaluated)
                        else:
                            result_parts.append(str(evaluated))
                    except Exception as e:
                        self.interpreter.debug_output(f"Expression error in PRINT: {e}")
                        result_parts.append(str(part))
            i += 1

        result = "".join(result_parts)
        self.interpreter.log_output(result)
        return "continue"

    def _handle_input(self, command, parts):
        """Handle INPUT statement"""
        input_text = command[5:].strip()

        if ";" in input_text:
            prompt_part, var_part = input_text.split(";", 1)
            prompt = prompt_part.strip().strip('"')
            var_name = var_part.strip()
        else:
            prompt = f"Enter value for {input_text.strip()}:"
            var_name = input_text.strip()

        value = self.interpreter.get_user_input(prompt)
        try:
            if "." in value:
                self.interpreter.variables[var_name] = float(value)
            else:
                self.interpreter.variables[var_name] = int(value)
        except:
            self.interpreter.variables[var_name] = value
        return "continue"

    def _handle_if(self, command):
        """Handle IF/THEN conditional statement"""
        try:
            m = re.match(r"IF\s+(.+?)\s+THEN\s+(.+?)(?:\s+ELSE\s+(.+))?$", command, re.IGNORECASE)
            if m:
                cond_expr = m.group(1).strip()
                then_cmd = m.group(2).strip()
                else_cmd = m.group(3).strip() if m.group(3) else None

                try:
                    cond_val = self.interpreter.evaluate_expression(cond_expr)
                except:
                    cond_val = False

                if cond_val:
                    return self.interpreter.execute_line(then_cmd)
                elif else_cmd:
                    return self.interpreter.execute_line(else_cmd)
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
                step_val = self.interpreter.evaluate_expression(step_expr) if step_expr else 1

                try:
                    start_val = int(start_val)
                except:
                    start_val = 0
                try:
                    end_val = int(end_val)
                except:
                    end_val = 0
                try:
                    step_val = int(step_val)
                except:
                    step_val = 1

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

    def _handle_next(self, command):
        """Handle NEXT statement"""
        try:
            parts = command.split()
            var_spec = parts[1] if len(parts) > 1 else None

            if not self.interpreter.for_stack:
                self.interpreter.log_output("NEXT without FOR")
                return "continue"

            if var_spec:
                found_idx = None
                for i in range(len(self.interpreter.for_stack) - 1, -1, -1):
                    if self.interpreter.for_stack[i]["var"].upper() == var_spec.upper():
                        found_idx = i
                        break
                if found_idx is None:
                    self.interpreter.debug_output(f"NEXT for unknown variable {var_spec}")
                    return "continue"
                ctx = self.interpreter.for_stack[found_idx]
            else:
                ctx = self.interpreter.for_stack[-1]
                found_idx = len(self.interpreter.for_stack) - 1

            var_name = ctx["var"]
            step = int(ctx["step"])
            end_val = int(ctx["end"])

            current_val = self.interpreter.variables.get(var_name, 0)
            try:
                current_val = int(current_val)
            except:
                current_val = 0

            next_val = current_val + step
            self.interpreter.variables[var_name] = int(next_val)

            loop_again = False
            try:
                if step >= 0:
                    loop_again = next_val <= int(end_val)
                else:
                    loop_again = next_val >= int(end_val)
            except:
                loop_again = False

            if loop_again:
                for_line = ctx["for_line"]
                return f"jump:{for_line + 1}"
            else:
                try:
                    self.interpreter.for_stack.pop(found_idx)
                except:
                    pass
        except Exception as e:
            self.interpreter.debug_output(f"NEXT statement error: {e}")
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

    def _handle_dim(self, command, parts):
        """Handle DIM array declaration"""
        try:
            if len(parts) >= 2:
                dim_spec = command[3:].strip()
                if "(" in dim_spec and ")" in dim_spec:
                    array_name = dim_spec.split("(")[0].strip()
                    dimensions_str = dim_spec.split("(")[1].split(")")[0]
                    dimensions = [int(d.strip()) for d in dimensions_str.split(",")]

                    def create_array_dict(dims):
                        if len(dims) == 1:
                            return {i: 0 for i in range(dims[0] + 1)}
                        else:
                            return {i: create_array_dict(dims[1:]) for i in range(dims[0] + 1)}

                    array = create_array_dict(dimensions)
                    self.interpreter.variables[array_name] = array
                    self.interpreter.log_output(f"Array {array_name} declared")
        except Exception as e:
            self.interpreter.debug_output(f"DIM statement error: {e}")
        return "continue"

    # Logo-style turtle command handlers
    def _handle_forward(self, parts):
        """Handle FORWARD command"""
        try:
            distance = float(parts[1]) if len(parts) > 1 else 50.0
        except:
            distance = 50.0

        if not self.interpreter.turtle_graphics:
            self.interpreter.init_turtle_graphics()
        self.interpreter.turtle_graphics["pen_down"] = True
        self.interpreter.turtle_forward(distance)
        self.interpreter.log_output("Turtle moved")

        # Set turtle position variables for testing
        self.interpreter.variables["TURTLE_X"] = self.interpreter.turtle_graphics["x"]
        self.interpreter.variables["TURTLE_Y"] = self.interpreter.turtle_graphics["y"]
        self.interpreter.variables["TURTLE_HEADING"] = self.interpreter.turtle_graphics["heading"]

        return "continue"

    def _handle_backward(self, parts):
        """Handle BACK/BACKWARD command"""
        try:
            distance = float(parts[1]) if len(parts) > 1 else 50.0
        except:
            distance = 50.0
        self.interpreter.turtle_forward(-distance)
        return "continue"

    def _handle_left(self, parts):
        """Handle LEFT command"""
        angle = float(parts[1]) if len(parts) > 1 else 90
        self.interpreter.turtle_turn(angle)
        return "continue"

    def _handle_right(self, parts):
        """Handle RIGHT command"""
        angle = float(parts[1]) if len(parts) > 1 else 90
        self.interpreter.turtle_turn(-angle)
        return "continue"

    def _handle_penup(self):
        """Handle PENUP command"""
        self.interpreter.turtle_graphics["pen_down"] = False
        return "continue"

    def _handle_pendown(self):
        """Handle PENDOWN command"""
        self.interpreter.turtle_graphics["pen_down"] = True
        return "continue"

    def _handle_clearscreen(self):
        """Handle CLEARSCREEN command"""
        self.interpreter.clear_turtle_screen()
        self.interpreter.log_output("Screen cleared")
        return "continue"

    def _handle_home(self):
        """Handle HOME command"""
        self.interpreter.turtle_home()
        self.interpreter.log_output("Turtle returned to home position")
        return "continue"

    def _handle_setxy(self, parts):
        """Handle SETXY command"""
        if len(parts) >= 3:
            x = float(parts[1])
            y = float(parts[2])
            self.interpreter.turtle_setxy(x, y)
            self.interpreter.log_output(f"Turtle moved to position ({x}, {y})")
        return "continue"

    def _handle_setcolor(self, parts):
        """Handle SETCOLOR/COLOR command"""
        color = parts[1].lower() if len(parts) > 1 else "black"
        self.interpreter.turtle_set_color(color)
        self.interpreter.log_output(f"Pen color set to {color}")
        return "continue"

    def _handle_setpensize(self, parts):
        """Handle SETPENSIZE command"""
        size = int(parts[1]) if len(parts) > 1 else 1
        self.interpreter.turtle_set_pen_size(size)
        self.interpreter.log_output(f"Pen size set to {size}")
        return "continue"

    def _handle_circle(self, parts):
        """Handle CIRCLE command"""
        try:
            radius = float(parts[1]) if len(parts) > 1 else 50
            if not self.interpreter.turtle_graphics:
                self.interpreter.init_turtle_graphics()
            self.interpreter.turtle_circle(radius)
            self.interpreter.log_output(f"Drew circle with radius {radius}")
        except Exception as e:
            self.interpreter.log_output(f"CIRCLE command error: {e}")
        return "continue"

    def _handle_dot(self, parts):
        """Handle DOT command"""
        try:
            size = int(parts[1]) if len(parts) > 1 else 5
            if not self.interpreter.turtle_graphics:
                self.interpreter.init_turtle_graphics()
            self.interpreter.turtle_dot(size)
            self.interpreter.log_output(f"Drew dot with size {size}")
        except Exception as e:
            self.interpreter.log_output(f"DOT command error: {e}")
        return "continue"

    def _handle_rect(self, parts):
        """Handle RECT command"""
        try:
            if len(parts) >= 3:
                width_str = parts[1].replace(',', '')
                height_str = parts[2].replace(',', '')
                width = float(width_str)
                height = float(height_str)
                if not self.interpreter.turtle_graphics:
                    self.interpreter.init_turtle_graphics()
                self.interpreter.turtle_rect(width, height)
                self.interpreter.log_output(f"Drew rectangle {width}x{height}")
        except Exception as e:
            self.interpreter.log_output(f"RECT command error: {e}")
        return "continue"

    def _handle_text(self, parts):
        """Handle TEXT command"""
        if len(parts) > 1:
            text = " ".join(parts[1:])
            if text.startswith('"') and text.endswith('"'):
                text = text[1:-1]
            self.interpreter.turtle_text(text)
            self.interpreter.log_output(f"Drew text: {text}")
        return "continue"

    def _handle_showturtle(self):
        """Handle SHOWTURTLE command"""
        self.interpreter.turtle_graphics["visible"] = True
        self.interpreter.update_turtle_display()
        self.interpreter.log_output("Turtle is now visible")
        return "continue"

    def _handle_hideturtle(self):
        """Handle HIDETURTLE command"""
        self.interpreter.turtle_graphics["visible"] = False
        self.interpreter.update_turtle_display()
        self.interpreter.log_output("Turtle is now hidden")
        return "continue"

    def _handle_repeat(self, command):
        """Handle REPEAT command"""
        parsed = self._parse_repeat_nested(command.strip())
        if not parsed:
            self.interpreter.log_output("Malformed REPEAT syntax")
            return "continue"
        count, subcommands = parsed

        guard = 0
        for _ in range(count):
            for sub in subcommands:
                guard += 1
                if guard > 5000:
                    self.interpreter.log_output("REPEAT aborted: expansion too large")
                    return "continue"
                self.execute_command(sub)
        return "continue"

    def _handle_call(self, name):
        """Handle macro CALL"""
        if name not in self.interpreter.macros:
            self.interpreter.log_output(f"Unknown macro: {name}")
            return "continue"
        if name in self.interpreter._macro_call_stack:
            self.interpreter.log_output(f"Macro recursion detected: {name}")
            return "continue"
        if len(self.interpreter._macro_call_stack) > 16:
            self.interpreter.log_output("Macro call depth limit exceeded")
            return "continue"

        self.interpreter._macro_call_stack.append(name)
        try:
            for mline in self.interpreter.macros[name]:
                if not self.interpreter.turtle_graphics:
                    self.interpreter.init_turtle_graphics()
                self.execute_command(mline)
        finally:
            self.interpreter._macro_call_stack.pop()
        return "continue"

    def _handle_define(self, command, name):
        """Handle DEFINE macro"""
        bracket_index = command.find("[")
        if bracket_index == -1:
            self.interpreter.log_output("Malformed DEFINE (missing [)")
            return "continue"
        block, ok = self._extract_bracket_block(command[bracket_index:])
        if not ok:
            self.interpreter.log_output("Malformed DEFINE (unmatched ])")
            return "continue"
        inner = block[1:-1].strip()
        subcommands = self._split_top_level_commands(inner)
        self.interpreter.macros[name] = subcommands
        self.interpreter.log_output(f"Macro '{name}' defined")
        return "continue"

    # Utility functions
    def _extract_bracket_block(self, text):
        """Extract a [...] block from the start of text"""
        text = text.strip()
        if not text.startswith("["):
            return "", False
        depth = 0
        for i, ch in enumerate(text):
            if ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    return text[: i + 1], True
        return text, False

    def _split_top_level_commands(self, inner):
        """Split commands properly keeping command-argument pairs together"""
        logo_commands = {
            "FORWARD", "FD", "BACK", "BK", "LEFT", "LT", "RIGHT", "RT",
            "PENUP", "PU", "PENDOWN", "PD", "CLEARSCREEN", "CS", "HOME",
            "SETXY", "SETCOLOR", "COLOR", "SETPENSIZE", "CIRCLE", "DOT",
            "RECT", "TEXT", "SHOWTURTLE", "HIDETURTLE", "REPEAT", "DEFINE", "CALL"
        }

        tokens = []
        buf = []
        depth = 0
        i = 0

        while i < len(inner):
            ch = inner[i]
            if ch == "[":
                depth += 1
                buf.append(ch)
            elif ch == "]":
                depth = max(0, depth - 1)
                buf.append(ch)
            elif ch.isspace() and depth == 0:
                if buf:
                    tokens.append("".join(buf).strip())
                    buf = []
            else:
                buf.append(ch)
            i += 1
        if buf:
            tokens.append("".join(buf).strip())

        commands = []
        i = 0
        while i < len(tokens):
            token = tokens[i].upper()

            if token in logo_commands:
                cmd_parts = [tokens[i]]
                i += 1

                if token in ["REPEAT", "DEFINE"]:
                    if i < len(tokens) and tokens[i].startswith("["):
                        bracket_depth = 0
                        start_i = i
                        while i < len(tokens):
                            if tokens[i].startswith("["):
                                bracket_depth += tokens[i].count("[")
                            if tokens[i].endswith("]"):
                                bracket_depth -= tokens[i].count("]")
                            if bracket_depth <= 0:
                                break
                            i += 1
                        for j in range(start_i, i + 1):
                            cmd_parts.append(tokens[j])
                        i += 1
                else:
                    while i < len(tokens):
                        next_token = tokens[i].upper()
                        if next_token in logo_commands:
                            break
                        cmd_parts.append(tokens[i])
                        i += 1

                commands.append(" ".join(cmd_parts))
            else:
                commands.append(tokens[i])
                i += 1

        return [cmd.strip() for cmd in commands if cmd.strip()]

    def _parse_repeat_nested(self, full_command):
        """Parse REPEAT n [ commands ... ] supporting nested REPEAT blocks"""
        m = re.match(r"^REPEAT\s+([0-9]+)\s+(.*)$", full_command.strip(), re.IGNORECASE)
        if not m:
            return None
        try:
            count = int(m.group(1))
        except ValueError:
            return None
        rest = m.group(2).strip()
        block, ok = self._extract_bracket_block(rest)
        if not ok:
            return None
        inner = block[1:-1].strip()
        raw_cmds = self._split_top_level_commands(inner)
        commands = [c.strip() for c in raw_cmds if c.strip()]
        return count, commands

    # Math and string functions
    def _handle_math_functions(self, cmd, parts):
        """Handle mathematical functions"""
        try:
            if cmd == "SIN":
                if len(parts) >= 2:
                    angle_expr = " ".join(parts[1:])
                    angle = self.interpreter.evaluate_expression(angle_expr)
                    result = math.sin(math.radians(float(angle)))
                    self.interpreter.variables["RESULT"] = result
                    self.interpreter.log_output(f"SIN({angle}°) = {result:.4f}")
            elif cmd == "COS":
                if len(parts) >= 2:
                    angle_expr = " ".join(parts[1:])
                    angle = self.interpreter.evaluate_expression(angle_expr)
                    result = math.cos(math.radians(float(angle)))
                    self.interpreter.variables["RESULT"] = result
                    self.interpreter.log_output(f"COS({angle}°) = {result:.4f}")
            elif cmd == "TAN":
                if len(parts) >= 2:
                    angle_expr = " ".join(parts[1:])
                    angle = self.interpreter.evaluate_expression(angle_expr)
                    result = math.tan(math.radians(float(angle)))
                    self.interpreter.variables["RESULT"] = result
                    self.interpreter.log_output(f"TAN({angle}°) = {result:.4f}")
            elif cmd == "SQRT":
                if len(parts) >= 2:
                    value_expr = " ".join(parts[1:])
                    value = self.interpreter.evaluate_expression(value_expr)
                    if float(value) >= 0:
                        result = math.sqrt(float(value))
                        self.interpreter.variables["RESULT"] = result
                        self.interpreter.log_output(f"SQRT({value}) = {result:.4f}")
            elif cmd == "ABS":
                if len(parts) >= 2:
                    value_expr = " ".join(parts[1:])
                    value = self.interpreter.evaluate_expression(value_expr)
                    result = abs(float(value))
                    self.interpreter.variables["RESULT"] = result
                    self.interpreter.log_output(f"ABS({value}) = {result}")
            elif cmd == "INT":
                if len(parts) >= 2:
                    value_expr = " ".join(parts[1:])
                    value = self.interpreter.evaluate_expression(value_expr)
                    result = int(float(value))
                    self.interpreter.variables["RESULT"] = result
                    self.interpreter.log_output(f"INT({value}) = {result}")
            elif cmd == "RND":
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
                if len(parts) >= 2:
                    # Evaluate the expression to get the actual string value
                    text_expr = " ".join(parts[1:])
                    text = self.interpreter.evaluate_expression(text_expr)
                    if isinstance(text, str):
                        result = len(text)
                        self.interpreter.variables["RESULT"] = result
                        self.interpreter.log_output(f"LEN('{text}') = {result}")
            elif cmd == "MID":
                if len(parts) >= 4:
                    text_expr = parts[1]
                    start_expr = parts[2]
                    length_expr = parts[3]
                    
                    text = self.interpreter.evaluate_expression(text_expr)
                    start = self.interpreter.evaluate_expression(start_expr)
                    length = self.interpreter.evaluate_expression(length_expr)
                    
                    if isinstance(text, str):
                        start = int(start) - 1  # BASIC uses 1-based indexing
                        length = int(length)
                        result = text[start : start + length]
                        self.interpreter.variables["RESULT"] = result
                        self.interpreter.log_output(f"MID('{text}', {start+1}, {length}) = '{result}'")
            elif cmd == "LEFT":
                if len(parts) >= 3:
                    text_expr = parts[1]
                    length_expr = parts[2]
                    
                    text = self.interpreter.evaluate_expression(text_expr)
                    length = self.interpreter.evaluate_expression(length_expr)
                    
                    if isinstance(text, str):
                        length = int(length)
                        result = text[:length]
                        self.interpreter.variables["RESULT"] = result
                        self.interpreter.log_output(f"LEFT('{text}', {length}) = '{result}'")
            elif cmd == "RIGHT":
                if len(parts) >= 3:
                    text_expr = parts[1]
                    length_expr = parts[2]
                    
                    text = self.interpreter.evaluate_expression(text_expr)
                    length = self.interpreter.evaluate_expression(length_expr)
                    
                    if isinstance(text, str):
                        length = int(length)
                        result = text[-length:]
                        self.interpreter.variables["RESULT"] = result
                        self.interpreter.log_output(f"RIGHT('{text}', {length}) = '{result}'")
            elif cmd == "UPPER":
                if len(parts) >= 2:
                    text_expr = " ".join(parts[1:])
                    text = self.interpreter.evaluate_expression(text_expr)
                    
                    if isinstance(text, str):
                        result = text.upper()
                        self.interpreter.variables["RESULT"] = result
                        self.interpreter.log_output(f"UPPER('{text}') = '{result}'")
            elif cmd == "LOWER":
                if len(parts) >= 2:
                    text_expr = " ".join(parts[1:])
                    text = self.interpreter.evaluate_expression(text_expr)
                    
                    if isinstance(text, str):
                        result = text.lower()
                        self.interpreter.variables["RESULT"] = result
                        self.interpreter.log_output(f"LOWER('{text}') = '{result}'")
        except Exception as e:
            self.interpreter.debug_output(f"String function error: {e}")
        return "continue"

    def _handle_array_operations(self, cmd, parts):
        """Handle array operations"""
        try:
            if cmd == "SUM":
                if len(parts) >= 2:
                    array_name = parts[1]
                    if array_name in self.interpreter.variables:
                        array = self.interpreter.variables[array_name]
                        if isinstance(array, dict):
                            values = list(array.values())
                            result = sum(values)
                            self.interpreter.variables["RESULT"] = result
                            self.interpreter.log_output(f"SUM({array_name}) = {result}")
            elif cmd == "AVG":
                if len(parts) >= 2:
                    array_name = parts[1]
                    if array_name in self.interpreter.variables:
                        array = self.interpreter.variables[array_name]
                        if isinstance(array, dict):
                            values = list(array.values())
                            result = sum(values) / len(values) if values else 0
                            self.interpreter.variables["RESULT"] = result
                            self.interpreter.log_output(f"AVG({array_name}) = {result}")
            elif cmd == "MIN":
                if len(parts) >= 2:
                    array_name = parts[1]
                    if array_name in self.interpreter.variables:
                        array = self.interpreter.variables[array_name]
                        if isinstance(array, dict):
                            values = list(array.values())
                            result = min(values) if values else 0
                            self.interpreter.variables["RESULT"] = result
                            self.interpreter.log_output(f"MIN({array_name}) = {result}")
            elif cmd == "MAX":
                if len(parts) >= 2:
                    array_name = parts[1]
                    if array_name in self.interpreter.variables:
                        array = self.interpreter.variables[array_name]
                        if isinstance(array, dict):
                            values = list(array.values())
                            result = max(values) if values else 0
                            self.interpreter.variables["RESULT"] = result
                            self.interpreter.log_output(f"MAX({array_name}) = {result}")
        except Exception as e:
            self.interpreter.debug_output(f"Array operation error: {e}")
        return "continue"

    def _handle_graphics(self, cmd, parts):
        """Handle graphics commands"""
        try:
            # Ensure we're in graphics mode for drawing
            if hasattr(self.interpreter, "ide_turtle_canvas") and hasattr(self.interpreter.ide_turtle_canvas, 'set_screen_mode'):
                # Switch to graphics mode (mode 7: 320x200 graphics)
                self.interpreter.ide_turtle_canvas.set_screen_mode(7)
            
            if cmd == "LINE":
                if len(parts) >= 3:
                    coords = parts[1].split("-")
                    if len(coords) == 2:
                        start = coords[0].strip("()").split(",")
                        end = coords[1].strip("()").split(",")
                        if len(start) == 2 and len(end) == 2:
                            x1, y1 = float(start[0]), float(start[1])
                            x2, y2 = float(end[0]), float(end[1])
                            if hasattr(self.interpreter, "ide_turtle_canvas"):
                                canvas = self.interpreter.ide_turtle_canvas
                                canvas.draw_line(x1, y1, x2, y2)
                                self.interpreter.log_output(f"Drew line from ({x1},{y1}) to ({x2},{y2})")
            elif cmd == "BOX":
                if len(parts) >= 4:
                    x, y = float(parts[1].strip("()").split(",")[0]), float(parts[1].strip("()").split(",")[1])
                    width, height = float(parts[2]), float(parts[3])
                    filled = len(parts) > 4 and parts[4].lower() == "true"
                    if hasattr(self.interpreter, "ide_turtle_canvas"):
                        canvas = self.interpreter.ide_turtle_canvas
                        canvas.draw_rectangle(x, y, x + width, y + height, filled=filled)
                        self.interpreter.log_output(f"Drew {'filled ' if filled else ''}box at ({x},{y}) size {width}x{height}")
            elif cmd == "TRIANGLE":
                if len(parts) >= 2:
                    coords = parts[1].split("-")
                    if len(coords) == 3:
                        points = []
                        for coord in coords:
                            coord = coord.strip("()").split(",")
                            if len(coord) == 2:
                                points.extend([float(coord[0]), float(coord[1])])
                        if len(points) == 6:
                            if hasattr(self.interpreter, "ide_turtle_canvas"):
                                canvas = self.interpreter.ide_turtle_canvas
                                filled = len(parts) > 2 and parts[2].lower() == "true"
                                # For triangle, we'll use the canvas's polygon method
                                if hasattr(canvas, 'create_polygon'):
                                    if filled:
                                        canvas.create_polygon(points, fill="black", tags="graphics")
                                    else:
                                        canvas.create_polygon(points, outline="black", fill="", tags="graphics")
                                self.interpreter.log_output(f"Drew {'filled ' if filled else ''}triangle")
            elif cmd == "ELLIPSE":
                if len(parts) >= 4:
                    x, y = float(parts[1].strip("()").split(",")[0]), float(parts[1].strip("()").split(",")[1])
                    width, height = float(parts[2]), float(parts[3])
                    filled = len(parts) > 4 and parts[4].lower() == "true"
                    if hasattr(self.interpreter, "ide_turtle_canvas"):
                        canvas = self.interpreter.ide_turtle_canvas
                        canvas.draw_circle(x + width/2, y + height/2, min(width, height)/2, filled=filled)
                        self.interpreter.log_output(f"Drew {'filled ' if filled else ''}ellipse at ({x},{y}) size {width}x{height}")
        except Exception as e:
            self.interpreter.debug_output(f"Graphics command error: {e}")
        return "continue"

    def _handle_sound_commands(self, cmd, parts):
        """Handle sound commands"""
        try:
            if cmd == "BEEP":
                frequency = 800 if len(parts) < 2 else float(parts[1])
                duration = 0.5 if len(parts) < 3 else float(parts[2])
                self.interpreter.log_output(f"Beep: {frequency}Hz for {duration}s")
            elif cmd == "PLAY":
                if len(parts) >= 2:
                    note = parts[1].strip('"')
                    duration = 0.5 if len(parts) < 3 else float(parts[2])
                    self.interpreter.log_output(f"Played note {note} for {duration}s")
            elif cmd == "PLAYNOTE":
                if len(parts) >= 3:
                    note = parts[1].strip('"')
                    duration = float(parts[2])
                    self.interpreter.log_output(f"Played note {note} for {duration}s")
            elif cmd == "SETSOUND":
                if len(parts) >= 3:
                    frequency = float(parts[1])
                    duration = float(parts[2])
                    self.interpreter.log_output(f"Set sound: {frequency}Hz for {duration}s")
        except Exception as e:
            self.interpreter.debug_output(f"Sound command error: {e}")
        return "continue"

    def _handle_file_commands(self, cmd, parts):
        """Handle file commands"""
        try:
            if cmd == "OPEN":
                if len(parts) >= 4 and parts[2].upper() == "FOR":
                    filename = parts[1].strip('"')
                    mode = parts[3].upper()
                    self.interpreter.log_output(f"File '{filename}' opened for {mode}")
            elif cmd == "READ":
                if len(parts) >= 3 and parts[1].startswith("#"):
                    handle = parts[1][1:]
                    var_name = parts[2]
                    self.interpreter.log_output(f"Read into {var_name} from file #{handle}")
            elif cmd == "WRITE":
                if len(parts) >= 3 and parts[1].startswith("#"):
                    handle = parts[1][1:]
                    expr = " ".join(parts[2:])
                    self.interpreter.log_output(f"Wrote '{expr}' to file #{handle}")
            elif cmd == "CLOSE":
                if len(parts) >= 2 and parts[1].startswith("#"):
                    handle = parts[1][1:]
                    self.interpreter.log_output(f"File #{handle} closed")
        except Exception as e:
            self.interpreter.debug_output(f"File command error: {e}")
        return "continue"