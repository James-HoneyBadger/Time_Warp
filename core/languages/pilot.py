"""
PILOT Language Executor for TimeWarp IDE
========================================

PILOT (Programmed Inquiry, Learning, Or Teaching) is an educational programming language
designed for teaching and learning programming concepts.

This module handles PILOT command execution including:
- Text output (T:)
- User input (A:)
- Conditional branching (Y:, N:)
- Jumps and labels (J:, L:)
- Variable updates (U:)
- Match conditions (M:, MT:)
- Subroutine calls (C:)
- Advanced runtime commands (R:)
"""

import re
import random
from tkinter import simpledialog


class PilotExecutor:
    """Handles PILOT language command execution"""

    def __init__(self, interpreter):
        """Initialize with reference to main interpreter"""
        self.interpreter = interpreter

    def execute_command(self, command):
        """Execute a PILOT command and return the result"""
        try:
            # Robust command type detection for J: and J(...):
            if command.startswith("J:") or command.startswith("J("):
                cmd_type = "J:"
            else:
                colon_idx = command.find(":")
                if colon_idx != -1:
                    cmd_type = command[: colon_idx + 1]
                else:
                    cmd_type = command[:2] if len(command) > 1 else command

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
            elif cmd_type == "L:":
                # Label - do nothing
                return "continue"
            elif cmd_type == "U:":
                return self._handle_update_variable(command)
            elif command.strip().upper() == "END":
                return "end"

        except Exception as e:
            self.interpreter.debug_output(f"PILOT command error: {e}")
            return "continue"

        return "continue"

    def _handle_text_output(self, command):
        """Handle T: text output command"""
        text = command[2:].strip()
        # If the previous command set a match (Y: or N:), then this T: is
        # treated as conditional and only prints when match_flag is True.
        if self.interpreter._last_match_set:
            # consume the sentinel
            self.interpreter._last_match_set = False
            if not self.interpreter.match_flag:
                # do not print when match is false
                return "continue"

        text = self.interpreter.interpolate_text(text)
        self.interpreter.log_output(text)
        return "continue"

    def _handle_accept_input(self, command):
        """Handle A: accept input command"""
        var_name = command[2:].strip()
        prompt = f"Enter value for {var_name}: "
        value = self.interpreter.get_user_input(prompt)
        # Distinguish numeric and alphanumeric input
        if value is not None and value.strip() != "":
            try:
                # Accept int if possible, else float, else string
                if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
                    self.interpreter.variables[var_name] = int(value)
                else:
                    float_val = float(value)
                    self.interpreter.variables[var_name] = float_val
            except Exception:
                self.interpreter.variables[var_name] = value
        else:
            self.interpreter.variables[var_name] = ""
        # Debug: show type and value of input variable
        self.interpreter.debug_output(
            f"[DEBUG] {var_name} = {self.interpreter.variables[var_name]!r} (type: {type(self.interpreter.variables[var_name]).__name__})"
        )
        return "continue"

    def _handle_yes_condition(self, command):
        """Handle Y: match if condition is true"""
        condition = command[2:].strip()
        try:
            result = self.interpreter.evaluate_expression(condition)
            self.interpreter.match_flag = bool(result)
        except:
            self.interpreter.match_flag = False
        # mark that the last command set the match flag so a following T: can be conditional
        self.interpreter._last_match_set = True
        return "continue"

    def _handle_no_condition(self, command):
        """Handle N: match if condition is false"""
        condition = command[2:].strip()
        try:
            result = self.interpreter.evaluate_expression(condition)
            # N: treat like a plain conditional (match when the condition is TRUE).
            self.interpreter.match_flag = bool(result)
        except:
            # On error, default to no match
            self.interpreter.match_flag = False
        # mark that the last command set the match flag so a following T: can be conditional
        self.interpreter._last_match_set = True
        return "continue"

    def _handle_jump(self, command):
        """Handle J: jump command (conditional or unconditional)"""
        # Robustly detect conditional jump: J(<condition>):<label> using regex
        import re

        match = re.match(r"^J\((.+)\):(.+)$", command.strip())
        if match:
            condition = match.group(1).strip()
            label = match.group(2).strip()
            try:
                cond_val = self.interpreter.evaluate_expression(condition)
                self.interpreter.debug_output(
                    f"[DEBUG] Condition string: '{condition}', AGE = {self.interpreter.variables.get('AGE', None)} (type: {type(self.interpreter.variables.get('AGE', None)).__name__})"
                )
                is_true = False
                if isinstance(cond_val, bool):
                    is_true = cond_val
                elif isinstance(cond_val, (int, float)):
                    is_true = cond_val != 0
                elif isinstance(cond_val, str):
                    is_true = cond_val.strip().lower() in ("true", "1")
                self.interpreter.debug_output(
                    f"[DEBUG] Evaluating condition: {condition} => {cond_val!r} (type: {type(cond_val).__name__}), interpreted as {is_true}"
                )
                if is_true:
                    self.interpreter.debug_output(
                        f"[DEBUG] Attempting to jump to label '{label}'. Labels dict: {self.interpreter.labels}"
                    )
                    if label in self.interpreter.labels:
                        self.interpreter.debug_output(
                            f"🎯 Condition '{condition}' is TRUE, jumping to {label} (line {self.interpreter.labels[label]})"
                        )
                        return f"jump:{self.interpreter.labels[label]}"
                    else:
                        self.interpreter.debug_output(
                            f"⚠️ Label '{label}' not found. Labels dict: {self.interpreter.labels}"
                        )
                else:
                    self.interpreter.debug_output(
                        f"🚫 Condition '{condition}' is FALSE, continuing"
                    )
                return "continue"
            except Exception as e:
                self.interpreter.debug_output(
                    f"❌ Error evaluating condition '{condition}': {e}"
                )
                return "continue"

        # If not conditional, treat as unconditional jump
        rest = command[2:].strip()
        label = rest
        if self.interpreter._last_match_set:
            self.interpreter._last_match_set = False
            if not self.interpreter.match_flag:
                return "continue"
        self.interpreter.debug_output(
            f"[DEBUG] Unconditional jump to label '{label}'. Labels dict: {self.interpreter.labels}"
        )
        if label in self.interpreter.labels:
            self.interpreter.debug_output(
                f"[DEBUG] Unconditional jump to {label} (line {self.interpreter.labels[label]})"
            )
            return f"jump:{self.interpreter.labels[label]}"
        else:
            self.interpreter.debug_output(
                f"⚠️ Unconditional jump label '{label}' not found. Labels dict: {self.interpreter.labels}"
            )
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
        # Unrecognized payload after C:, ignore
        return "continue"

    def _handle_update_variable(self, command):
        """Handle U: update variable command"""
        assignment = command[2:].strip()
        if "=" in assignment:
            var_name, expr = assignment.split("=", 1)
            var_name = var_name.strip()
            expr = expr.strip()

            # First try to interpolate text (for string assignments)
            interpolated = self.interpreter.interpolate_text(expr)

            # If the interpolated result looks like a mathematical expression, evaluate it
            if re.match(r"^[-+0-9\s\+\-\*\/\(\)\.]+$", interpolated):
                try:
                    value = eval(interpolated)
                    self.interpreter.variables[var_name] = value
                    return "continue"
                except Exception:
                    pass

            # If interpolation changed the text and it's not a math expression, use as string
            if interpolated != expr:
                self.interpreter.variables[var_name] = interpolated
            else:
                # Otherwise try to evaluate as expression using the interpreter method
                try:
                    value = self.interpreter.evaluate_expression(expr)
                    # Remove quotes if the result is a quoted string
                    if (
                        isinstance(value, str)
                        and value.startswith('"')
                        and value.endswith('"')
                    ):
                        value = value[1:-1]
                    self.interpreter.variables[var_name] = value
                except Exception as e:
                    # If evaluation fails, just store the raw text
                    self.interpreter.variables[var_name] = expr
                    self.interpreter.debug_output(
                        f"Error in assignment {assignment}: {e}"
                    )
        return "continue"

    def _handle_runtime_command(self, command):
        """Handle R: runtime commands - placeholder for now"""
        # This would contain the full implementation from the original interpreter
        self.interpreter.log_output(f"Runtime command: {command[2:].strip()}")
        return "continue"

    def _handle_game_command(self, command):
        """Handle GAME: game development commands - placeholder for now"""
        # This would contain the full implementation from the original interpreter
        self.interpreter.log_output(f"Game command: {command[5:].strip()}")
        return "continue"

    def _handle_audio_command(self, command):
        """Handle AUDIO: audio system commands - placeholder for now"""
        # This would contain the full implementation from the original interpreter
        self.interpreter.log_output(f"Audio command: {command[6:].strip()}")
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

            elif operation == "EXISTS" and len(parts) >= 3:
                filename = parts[1].strip('"')
                var_name = parts[2].strip()
                exists = "1" if os.path.exists(filename) else "0"
                self.interpreter.variables[var_name] = exists

            elif operation == "SIZE" and len(parts) >= 3:
                filename = parts[1].strip('"')
                var_name = parts[2].strip()
                if os.path.exists(filename):
                    size = str(os.path.getsize(filename))
                    self.interpreter.variables[var_name] = size
                else:
                    self.interpreter.variables[var_name] = "0"

        except Exception as e:
            self.interpreter.debug_output(f"File operation error: {e}")

        return "continue"

    def _handle_web_command(self, command):
        """Handle W: web/HTTP commands"""
        import urllib.parse

        cmd = command[2:].strip()

        # Parse arguments respecting quoted strings
        pattern = r'"([^"]*)"|\S+'
        args = []
        for match in re.finditer(pattern, cmd):
            if match.group(1) is not None:  # Quoted string
                args.append(match.group(1))
            else:  # Unquoted word
                args.append(match.group(0))

        if not args:
            return "continue"

        operation = args[0].upper()

        try:
            if operation == "ENCODE" and len(args) >= 3:
                text = args[1]
                var_name = args[2]
                text = self.interpreter.interpolate_text(text)
                encoded = urllib.parse.quote(text)
                self.interpreter.variables[var_name] = encoded

            elif operation == "DECODE" and len(args) >= 3:
                text = args[1]
                var_name = args[2]
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

                # Store database connection (simplified)
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

                if (
                    hasattr(self.interpreter, "db_connections")
                    and "current" in self.interpreter.db_connections
                ):
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

            elif operation == "INSERT" and len(parts) >= 2:
                # D:INSERT "table" "columns" "values"
                full_parts = cmd.split(" ", 3)
                if len(full_parts) >= 4:
                    table = full_parts[1].strip('"')
                    columns = full_parts[2].strip('"')
                    values = full_parts[3].strip('"')

                    table = self.interpreter.interpolate_text(table)
                    columns = self.interpreter.interpolate_text(columns)
                    values = self.interpreter.interpolate_text(values)

                    query = f"INSERT INTO {table} ({columns}) VALUES ({values})"

                    if (
                        hasattr(self.interpreter, "db_connections")
                        and "current" in self.interpreter.db_connections
                    ):
                        try:
                            conn = self.interpreter.db_connections["current"]
                            cursor = conn.cursor()
                            cursor.execute(query)
                            conn.commit()
                            self.interpreter.variables["DB_INSERT_SUCCESS"] = "1"
                        except sqlite3.Error:
                            self.interpreter.variables["DB_INSERT_SUCCESS"] = "0"
                    else:
                        self.interpreter.variables["DB_INSERT_SUCCESS"] = "0"

        except Exception as e:
            self.interpreter.debug_output(f"Database operation error: {e}")

        return "continue"

    def _handle_string_command(self, command):
        """Handle S: string processing commands"""
        import re

        cmd = command[2:].strip()

        # Parse arguments respecting quoted strings
        # Pattern to match quoted strings or unquoted words
        pattern = r'"([^"]*)"|\S+'
        matches = re.findall(pattern, cmd)

        # Extract actual arguments from regex matches
        args = []
        for match in re.finditer(pattern, cmd):
            if match.group(1) is not None:  # Quoted string
                args.append(match.group(1))
            else:  # Unquoted word
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

            elif operation == "FIND" and len(args) >= 4:
                text = args[1]
                search = args[2]
                var_name = args[3]
                text = self.interpreter.interpolate_text(text)
                search = self.interpreter.interpolate_text(search)
                pos = text.find(search)
                self.interpreter.variables[var_name] = str(pos)

            elif operation == "REPLACE" and len(args) >= 5:
                # S:REPLACE "text" "old" "new" VAR
                text = args[1]
                old = args[2]
                new = args[3]
                var_name = args[4]
                text = self.interpreter.interpolate_text(text)
                old = self.interpreter.interpolate_text(old)
                new = self.interpreter.interpolate_text(new)
                if old:  # Don't replace empty strings
                    result = text.replace(old, new)
                else:
                    result = text
                self.interpreter.variables[var_name] = result

            elif operation == "SUBSTRING" and len(args) >= 5:
                # S:SUBSTRING "text" start length VAR
                text = args[1]
                start = int(args[2])
                length = int(args[3])
                var_name = args[4]
                text = self.interpreter.interpolate_text(text)
                result = text[start : start + length]
                self.interpreter.variables[var_name] = result

            elif operation == "SPLIT" and len(args) >= 4:
                text = args[1]
                delimiter = args[2]
                var_name = args[3]
                text = self.interpreter.interpolate_text(text)
                delimiter = self.interpreter.interpolate_text(delimiter)
                split_parts = text.split(delimiter)
                # Store first part in variable, could be extended
                if split_parts:
                    self.interpreter.variables[var_name] = split_parts[0]
                else:
                    self.interpreter.variables[var_name] = ""

        except (ValueError, IndexError) as e:
            self.interpreter.debug_output(f"String operation error: {e}")

        return "continue"

    def _handle_datetime_command(self, command):
        """Handle DT: date/time commands"""
        from datetime import datetime
        import time

        cmd = command[3:].strip()  # Skip "DT:"
        parts = cmd.split(" ", 2)

        if not parts:
            return "continue"

        operation = parts[0].upper()

        try:
            if operation == "NOW" and len(parts) >= 3:
                format_str = parts[1].strip('"')
                var_name = parts[2].strip()

                # Simple format mapping
                format_map = {
                    "YYYY-MM-DD": "%Y-%m-%d",
                    "HH:MM:SS": "%H:%M:%S",
                    "YYYY-MM-DD HH:MM:SS": "%Y-%m-%d %H:%M:%S",
                }

                fmt = format_map.get(format_str, format_str)
                now = datetime.now().strftime(fmt)
                self.interpreter.variables[var_name] = now

            elif operation == "TIMESTAMP" and len(parts) >= 2:
                var_name = parts[1].strip()
                timestamp = str(int(time.time()))
                self.interpreter.variables[var_name] = timestamp

            elif operation == "PARSE" and len(parts) >= 4:
                date_str = parts[1].strip('"')
                format_str = parts[2].strip('"')
                var_name = parts[3].strip()

                # Simple parsing - just store the original for now
                self.interpreter.variables[var_name] = date_str

            elif operation == "FORMAT" and len(parts) >= 4:
                timestamp = parts[1].strip('"')
                format_str = parts[2].strip('"')
                var_name = parts[3].strip()

                # Try to format timestamp
                try:
                    ts = int(self.interpreter.interpolate_text(timestamp))
                    dt = datetime.fromtimestamp(ts)

                    format_map = {
                        "YYYY-MM-DD": "%Y-%m-%d",
                        "HH:MM:SS": "%H:%M:%S",
                        "YYYY-MM-DD HH:MM:SS": "%Y-%m-%d %H:%M:%S",
                    }

                    fmt = format_map.get(format_str, format_str)
                    formatted = dt.strftime(fmt)
                    self.interpreter.variables[var_name] = formatted
                except (ValueError, OSError):
                    self.interpreter.variables[var_name] = timestamp

        except Exception as e:
            self.interpreter.debug_output(f"DateTime operation error: {e}")

        return "continue"
