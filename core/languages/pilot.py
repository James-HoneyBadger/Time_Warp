"""
PILOT Language Executor for JAMES IDE
=====================================

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
                colon_idx = command.find(':')
                if colon_idx != -1:
                    cmd_type = command[:colon_idx+1]
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
                if value.isdigit() or (value.startswith('-') and value[1:].isdigit()):
                    self.interpreter.variables[var_name] = int(value)
                else:
                    float_val = float(value)
                    self.interpreter.variables[var_name] = float_val
            except Exception:
                self.interpreter.variables[var_name] = value
        else:
            self.interpreter.variables[var_name] = ""
        # Debug: show type and value of input variable
        self.interpreter.debug_output(f"[DEBUG] {var_name} = {self.interpreter.variables[var_name]!r} (type: {type(self.interpreter.variables[var_name]).__name__})")
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
        match = re.match(r'^J\((.+)\):(.+)$', command.strip())
        if match:
            condition = match.group(1).strip()
            label = match.group(2).strip()
            try:
                cond_val = self.interpreter.evaluate_expression(condition)
                self.interpreter.debug_output(f"[DEBUG] Condition string: '{condition}', AGE = {self.interpreter.variables.get('AGE', None)} (type: {type(self.interpreter.variables.get('AGE', None)).__name__})")
                is_true = False
                if isinstance(cond_val, bool):
                    is_true = cond_val
                elif isinstance(cond_val, (int, float)):
                    is_true = cond_val != 0
                elif isinstance(cond_val, str):
                    is_true = cond_val.strip().lower() in ("true", "1")
                self.interpreter.debug_output(f"[DEBUG] Evaluating condition: {condition} => {cond_val!r} (type: {type(cond_val).__name__}), interpreted as {is_true}")
                if is_true:
                    self.interpreter.debug_output(f"[DEBUG] Attempting to jump to label '{label}'. Labels dict: {self.interpreter.labels}")
                    if label in self.interpreter.labels:
                        self.interpreter.debug_output(f"🎯 Condition '{condition}' is TRUE, jumping to {label} (line {self.interpreter.labels[label]})")
                        return f"jump:{self.interpreter.labels[label]}"
                    else:
                        self.interpreter.debug_output(f"⚠️ Label '{label}' not found. Labels dict: {self.interpreter.labels}")
                else:
                    self.interpreter.debug_output(f"🚫 Condition '{condition}' is FALSE, continuing")
                return "continue"
            except Exception as e:
                self.interpreter.debug_output(f"❌ Error evaluating condition '{condition}': {e}")
                return "continue"
        
        # If not conditional, treat as unconditional jump
        rest = command[2:].strip()
        label = rest
        if self.interpreter._last_match_set:
            self.interpreter._last_match_set = False
            if not self.interpreter.match_flag:
                return "continue"
        self.interpreter.debug_output(f"[DEBUG] Unconditional jump to label '{label}'. Labels dict: {self.interpreter.labels}")
        if label in self.interpreter.labels:
            self.interpreter.debug_output(f"[DEBUG] Unconditional jump to {label} (line {self.interpreter.labels[label]})")
            return f"jump:{self.interpreter.labels[label]}"
        else:
            self.interpreter.debug_output(f"⚠️ Unconditional jump label '{label}' not found. Labels dict: {self.interpreter.labels}")
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
        if '=' in payload:
            var_part, expr_part = payload.split('=', 1)
            var_name = var_part.strip().rstrip(':')
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
            try:
                value = self.interpreter.evaluate_expression(expr)
                self.interpreter.variables[var_name] = value
            except Exception as e:
                self.interpreter.debug_output(f"Error in assignment {assignment}: {e}")
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
        """Handle F: file I/O commands - placeholder for now"""
        # This would contain the full implementation from the original interpreter
        self.interpreter.log_output(f"File command: {command[2:].strip()}")
        return "continue"
    
    def _handle_web_command(self, command):
        """Handle W: web/HTTP commands - placeholder for now"""
        # This would contain the full implementation from the original interpreter
        self.interpreter.log_output(f"Web command: {command[2:].strip()}")
        return "continue"
    
    def _handle_database_command(self, command):
        """Handle D: database commands - placeholder for now"""
        # This would contain the full implementation from the original interpreter
        self.interpreter.log_output(f"Database command: {command[2:].strip()}")
        return "continue"
    
    def _handle_string_command(self, command):
        """Handle S: string processing commands - placeholder for now"""
        # This would contain the full implementation from the original interpreter
        self.interpreter.log_output(f"String command: {command[2:].strip()}")
        return "continue"
    
    def _handle_datetime_command(self, command):
        """Handle DT: date/time commands - placeholder for now"""
        # This would contain the full implementation from the original interpreter
        self.interpreter.log_output(f"DateTime command: {command[3:].strip()}")
        return "continue"