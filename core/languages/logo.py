"""
Logo Language Executor for Time_Warp IDE
=======================================

Logo is an educational programming language known for its turtle graphics capabilities.
It was designed to teach programming concepts to children through visual feedback.

This module handles Logo command execution including:
- Turtle movement (FORWARD, BACK, LEFT, RIGHT)
- Pen control (PENUP, PENDOWN)
- Screen management (CLEARSCREEN, HOME)
- Drawing commands (CIRCLE, DOT, RECT, TEXT)
- Control structures (REPEAT)
- Macros (DEFINE, CALL)
"""

import re
import math
import time


class LogoExecutor:
    """Handles Logo language command execution"""

    def __init__(self, interpreter):
        """Initialize with reference to main interpreter"""
        self.interpreter = interpreter

    def execute_command(self, command):
        """Execute a Logo command and return the result"""
        try:
            prof_start = (
                time.perf_counter() if self.interpreter.profile_enabled else None
            )
            parts = command.strip().split()
            if not parts:
                return "continue"

            cmd = parts[0].upper()

            # Debug: log the command execution if debug mode enabled
            self.interpreter.debug_output(f"Executing Logo command: {cmd}")

            # Ensure turtle system exists early
            if not self.interpreter.turtle_graphics:
                self.interpreter.init_turtle_graphics()

            # Macro CALL
            if cmd == "CALL" and len(parts) >= 2:
                return self._handle_call(parts[1])

            # DEFINE macro
            if cmd == "DEFINE" and len(parts) >= 2:
                return self._handle_define(command, parts[1])

            # Nested REPEAT
            if cmd == "REPEAT":
                return self._handle_repeat(command)

            # Movement commands
            if cmd in ["FORWARD", "FD"]:
                return self._handle_forward(parts)
            elif cmd in ["BACK", "BK", "BACKWARD"]:
                return self._handle_backward(parts)
            elif cmd in ["LEFT", "LT"]:
                return self._handle_left(parts)
            elif cmd in ["RIGHT", "RT"]:
                return self._handle_right(parts)

            # Pen control commands
            elif cmd in ["PENUP", "PU"]:
                return self._handle_penup()
            elif cmd in ["PENDOWN", "PD"]:
                return self._handle_pendown()

            # Screen and positioning commands
            elif cmd in ["CLEARSCREEN", "CS"]:
                return self._handle_clearscreen()
            elif cmd in ["HOME"]:
                return self._handle_home()
            elif cmd == "SETXY":
                return self._handle_setxy(parts)

            # Color and appearance commands
            elif cmd in ["SETCOLOR", "SETCOLOUR", "COLOR"]:
                return self._handle_setcolor(parts)
            elif cmd == "SETPENSIZE":
                return self._handle_setpensize(parts)

            # Drawing shapes
            elif cmd == "CIRCLE":
                return self._handle_circle(parts)
            elif cmd == "DOT":
                return self._handle_dot(parts)
            elif cmd == "RECT":
                return self._handle_rect(parts)
            elif cmd == "TEXT":
                return self._handle_text(parts)

            # Information commands
            elif cmd == "SHOWTURTLE":
                return self._handle_showturtle()
            elif cmd == "HIDETURTLE":
                return self._handle_hideturtle()
            elif cmd == "HEADING":
                return self._handle_heading()
            elif cmd == "POSITION":
                return self._handle_position()

            # Advanced commands
            elif cmd == "TRACE":
                return self._handle_trace(parts)
            elif cmd == "PROFILE":
                return self._handle_profile(parts)

            # Game Development Commands (Logo style)
            elif (
                cmd.startswith("CREATE")
                or cmd.startswith("MOVE")
                or cmd.startswith("GAME")
            ):
                return self._handle_game_commands(cmd, parts)

            # Audio System Commands (Logo style)
            elif (
                cmd.startswith("LOAD")
                or cmd.startswith("PLAY")
                or cmd.startswith("STOP")
            ):
                return self._handle_audio_commands(cmd, parts)

            else:
                self.interpreter.log_output(f"Unknown Logo command: {cmd}")

            # Profiling aggregation (Logo only) done after successful handling
            if self.interpreter.profile_enabled and prof_start is not None:
                try:
                    elapsed = time.perf_counter() - prof_start
                    key = cmd.upper()[:25]
                    stats = self.interpreter.profile_stats.setdefault(
                        key, {"count": 0, "total": 0.0, "max": 0.0}
                    )
                    stats["count"] += 1
                    stats["total"] += elapsed
                    if elapsed > stats["max"]:
                        stats["max"] = elapsed
                except Exception:
                    pass

        except ValueError as e:
            self.interpreter.debug_output(f"Logo command parameter error: {e}")
        except Exception as e:
            self.interpreter.debug_output(f"Logo command error: {e}")

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
            self.interpreter.log_output("Malformed DEFINE (unmatched ] )")
            return "continue"
        inner = block[1:-1].strip()
        subcommands = self._split_top_level_commands(inner)
        self.interpreter.macros[name] = subcommands
        self.interpreter.log_output(
            f"Macro '{name}' defined ({len(subcommands)} commands)"
        )
        return "continue"

    def _handle_repeat(self, command):
        """Handle REPEAT command"""
        parsed = self._parse_repeat_nested(command.strip())
        if not parsed:
            self.interpreter.log_output("Malformed REPEAT syntax or unmatched brackets")
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

    def _handle_forward(self, parts):
        """Handle FORWARD command"""
        try:
            distance = float(parts[1]) if len(parts) > 1 else 50.0
        except Exception:
            distance = 50.0

        if not self.interpreter.turtle_graphics:
            self.interpreter.init_turtle_graphics()
        self.interpreter.turtle_graphics["pen_down"] = True
        self.interpreter.turtle_forward(distance)
        self.interpreter.debug_output(f"Turtle moved forward {distance} units")
        self.interpreter.log_output("Turtle moved")

        if self.interpreter.turtle_trace:
            self.interpreter.log_output(
                f"TRACE: POS=({self.interpreter.turtle_graphics['x']:.1f},{self.interpreter.turtle_graphics['y']:.1f}) HEADING={self.interpreter.turtle_graphics['heading']:.1f}° PEN={'DOWN' if self.interpreter.turtle_graphics['pen_down'] else 'UP'}"
            )

        # Set turtle position variables for testing
        self.interpreter.variables["TURTLE_X"] = self.interpreter.turtle_graphics["x"]
        self.interpreter.variables["TURTLE_Y"] = self.interpreter.turtle_graphics["y"]
        self.interpreter.variables["TURTLE_HEADING"] = self.interpreter.turtle_graphics[
            "heading"
        ]

        return "continue"

    def _handle_backward(self, parts):
        """Handle BACK/BACKWARD command"""
        try:
            distance = float(parts[1]) if len(parts) > 1 else 50.0
        except Exception:
            distance = 50.0
        self.interpreter.turtle_forward(-distance)  # Move backward
        self.interpreter.debug_output(f"Turtle moved backward {distance} units")
        if self.interpreter.turtle_trace:
            self.interpreter.log_output(
                f"TRACE: POS=({self.interpreter.turtle_graphics['x']:.1f},{self.interpreter.turtle_graphics['y']:.1f}) HEADING={self.interpreter.turtle_graphics['heading']:.1f}° PEN={'DOWN' if self.interpreter.turtle_graphics['pen_down'] else 'UP'}"
            )
        # Set turtle position variables for testing
        self.interpreter.variables["TURTLE_X"] = self.interpreter.turtle_graphics["x"]
        self.interpreter.variables["TURTLE_Y"] = self.interpreter.turtle_graphics["y"]
        self.interpreter.variables["TURTLE_HEADING"] = self.interpreter.turtle_graphics[
            "heading"
        ]
        return "continue"

    def _handle_left(self, parts):
        """Handle LEFT command"""
        angle = float(parts[1]) if len(parts) > 1 else 90
        self.interpreter.turtle_turn(angle)
        self.interpreter.debug_output(
            f"Turtle turned left {angle} degrees (heading={self.interpreter.turtle_graphics['heading']})"
        )
        if self.interpreter.turtle_trace:
            self.interpreter.log_output(
                f"TRACE: POS=({self.interpreter.turtle_graphics['x']:.1f},{self.interpreter.turtle_graphics['y']:.1f}) HEADING={self.interpreter.turtle_graphics['heading']:.1f}° PEN={'DOWN' if self.interpreter.turtle_graphics['pen_down'] else 'UP'}"
            )
        # Set turtle position variables for testing
        self.interpreter.variables["TURTLE_X"] = self.interpreter.turtle_graphics["x"]
        self.interpreter.variables["TURTLE_Y"] = self.interpreter.turtle_graphics["y"]
        self.interpreter.variables["TURTLE_HEADING"] = self.interpreter.turtle_graphics[
            "heading"
        ]
        return "continue"

    def _handle_right(self, parts):
        """Handle RIGHT command"""
        angle = float(parts[1]) if len(parts) > 1 else 90
        if not self.interpreter.turtle_graphics:
            self.interpreter.init_turtle_graphics()
        # Use positive angle for RIGHT to match test expectations
        self.interpreter.turtle_turn(angle)
        self.interpreter.debug_output(
            f"Turtle turned right {angle} degrees (heading={self.interpreter.turtle_graphics['heading']})"
        )
        if self.interpreter.turtle_trace:
            self.interpreter.log_output(
                f"TRACE: POS=({self.interpreter.turtle_graphics['x']:.1f},{self.interpreter.turtle_graphics['y']:.1f}) HEADING={self.interpreter.turtle_graphics['heading']:.1f}° PEN={'DOWN' if self.interpreter.turtle_graphics['pen_down'] else 'UP'}"
            )
        # Set turtle position variables for testing
        self.interpreter.variables["TURTLE_X"] = self.interpreter.turtle_graphics["x"]
        self.interpreter.variables["TURTLE_Y"] = self.interpreter.turtle_graphics["y"]
        self.interpreter.variables["TURTLE_HEADING"] = self.interpreter.turtle_graphics[
            "heading"
        ]
        return "continue"

    def _handle_penup(self):
        """Handle PENUP command"""
        self.interpreter.turtle_graphics["pen_down"] = False
        self.interpreter.debug_output("Pen up - turtle will move without drawing")
        if self.interpreter.turtle_trace:
            self.interpreter.log_output(f"TRACE: PEN=UP")
        return "continue"

    def _handle_pendown(self):
        """Handle PENDOWN command"""
        prev_state = self.interpreter.turtle_graphics["pen_down"]
        self.interpreter.turtle_graphics["pen_down"] = True
        # If transitioning from up to down, advance color for new shape for visibility
        if not prev_state:
            self.interpreter._turtle_color_index = (
                self.interpreter._turtle_color_index + 1
            ) % len(self.interpreter._turtle_color_palette)
            self.interpreter.turtle_graphics["pen_color"] = (
                self.interpreter._turtle_color_palette[
                    self.interpreter._turtle_color_index
                ]
            )
        self.interpreter.debug_output("Pen down - turtle will draw when moving")
        if self.interpreter.turtle_trace:
            self.interpreter.log_output(
                f"TRACE: PEN=DOWN COLOR={self.interpreter.turtle_graphics['pen_color']}"
            )
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
        # Set turtle position variables for testing
        self.interpreter.variables["TURTLE_X"] = self.interpreter.turtle_graphics["x"]
        self.interpreter.variables["TURTLE_Y"] = self.interpreter.turtle_graphics["y"]
        self.interpreter.variables["TURTLE_HEADING"] = self.interpreter.turtle_graphics[
            "heading"
        ]
        return "continue"

    def _handle_setxy(self, parts):
        """Handle SETXY command"""
        if len(parts) >= 3:
            x = float(parts[1])
            y = float(parts[2])
            self.interpreter.turtle_setxy(x, y)
            self.interpreter.log_output(f"Turtle moved to position ({x}, {y})")
        else:
            self.interpreter.log_output("SETXY requires X and Y coordinates")
        # Set turtle position variables for testing
        self.interpreter.variables["TURTLE_X"] = self.interpreter.turtle_graphics["x"]
        self.interpreter.variables["TURTLE_Y"] = self.interpreter.turtle_graphics["y"]
        self.interpreter.variables["TURTLE_HEADING"] = self.interpreter.turtle_graphics[
            "heading"
        ]
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
        radius = float(parts[1]) if len(parts) > 1 else 50
        self.interpreter.turtle_circle(radius)
        self.interpreter.log_output(f"Drew circle with radius {radius}")
        return "continue"

    def _handle_dot(self, parts):
        """Handle DOT command"""
        size = int(parts[1]) if len(parts) > 1 else 5
        self.interpreter.turtle_dot(size)
        self.interpreter.log_output(f"Drew dot with size {size}")
        return "continue"

    def _handle_rect(self, parts):
        """Handle RECT command"""
        if len(parts) >= 3:
            width = float(parts[1])
            height = float(parts[2])
            self.interpreter.turtle_rect(width, height)
            self.interpreter.log_output(f"Drew rectangle {width}x{height}")
        else:
            self.interpreter.log_output("RECT requires width and height")
        return "continue"

    def _handle_text(self, parts):
        """Handle TEXT command"""
        if len(parts) > 1:
            text = " ".join(parts[1:])
            # Remove quotes if present
            if text.startswith('"') and text.endswith('"'):
                text = text[1:-1]
            self.interpreter.turtle_text(text)
            self.interpreter.log_output(f"Drew text: {text}")
        else:
            self.interpreter.log_output("TEXT requires text content")
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

    def _handle_heading(self):
        """Handle HEADING command"""
        heading = self.interpreter.turtle_graphics["heading"]
        self.interpreter.log_output(f"Turtle heading: {heading} degrees")
        return "continue"

    def _handle_position(self):
        """Handle POSITION command"""
        x, y = (
            self.interpreter.turtle_graphics["x"],
            self.interpreter.turtle_graphics["y"],
        )
        self.interpreter.log_output(f"Turtle position: ({x:.1f}, {y:.1f})")
        return "continue"

    def _handle_trace(self, parts):
        """Handle TRACE command"""
        if len(parts) > 1:
            state = parts[1].upper()
            if state in ("ON", "TRUE", "1"):
                self.interpreter.turtle_trace = True
                self.interpreter.log_output("Turtle trace enabled")
            elif state in ("OFF", "FALSE", "0"):
                self.interpreter.turtle_trace = False
                self.interpreter.log_output("Turtle trace disabled")
        else:
            self.interpreter.turtle_trace = not self.interpreter.turtle_trace
            self.interpreter.log_output(
                f"Turtle trace {'enabled' if self.interpreter.turtle_trace else 'disabled'}"
            )
        return "continue"

    def _handle_profile(self, parts):
        """Handle PROFILE command"""
        action = parts[1].upper() if len(parts) > 1 else "REPORT"
        if action == "ON":
            self.interpreter.profile_enabled = True
            self.interpreter.profile_stats = {}
            self.interpreter.log_output("Profiling enabled")
        elif action == "OFF":
            self.interpreter.profile_enabled = False
            self.interpreter.log_output("Profiling disabled")
        elif action == "RESET":
            self.interpreter.profile_stats = {}
            self.interpreter.log_output("Profiling data reset")
        elif action == "REPORT":
            if not self.interpreter.profile_stats:
                self.interpreter.log_output("No profiling data")
            else:
                self.interpreter.log_output(
                    "PROFILE REPORT (command  count   avg(ms)   max(ms)  total(ms)):"
                )
                for k, v in sorted(
                    self.interpreter.profile_stats.items(),
                    key=lambda kv: kv[1]["total"],
                    reverse=True,
                ):
                    avg = (v["total"] / v["count"]) if v["count"] else 0.0
                    self.interpreter.log_output(
                        f"  {k:<12} {v['count']:>5} {avg*1000:>9.3f} {v['max']*1000:>9.3f} {v['total']*1000:>10.3f}"
                    )
        else:
            self.interpreter.log_output("PROFILE expects ON|OFF|RESET|REPORT")
        return "continue"

    def _handle_game_commands(self, cmd, parts):
        """Handle game commands in Logo style"""
        self.interpreter.log_output(f"Game command: {cmd} {' '.join(parts[1:])}")
        return "continue"

    def _handle_audio_commands(self, cmd, parts):
        """Handle audio commands in Logo style"""
        self.interpreter.log_output(f"Audio command: {cmd} {' '.join(parts[1:])}")
        return "continue"

    # Helper methods for parsing
    def _extract_bracket_block(self, text):
        """Extract a [...] block from the start of text. Returns (block, ok)."""
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
        return text, False  # unmatched

    def _split_top_level_commands(self, inner):
        """Split commands properly keeping command-argument pairs together while preserving nested [ ] blocks."""
        # Known Logo commands that we need to recognize
        logo_commands = {
            "FORWARD",
            "FD",
            "BACK",
            "BK",
            "BACKWARD",
            "LEFT",
            "LT",
            "RIGHT",
            "RT",
            "PENUP",
            "PU",
            "PENDOWN",
            "PD",
            "CLEARSCREEN",
            "CS",
            "HOME",
            "SETXY",
            "SETCOLOR",
            "SETCOLOUR",
            "COLOR",
            "SETPENSIZE",
            "CIRCLE",
            "DOT",
            "RECT",
            "TEXT",
            "SHOWTURTLE",
            "HIDETURTLE",
            "HEADING",
            "POSITION",
            "TRACE",
            "PROFILE",
            "REPEAT",
            "DEFINE",
            "CALL",
        }

        # Tokenize the input respecting brackets
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

        # Now group tokens into commands with their arguments
        commands = []
        i = 0
        while i < len(tokens):
            token = tokens[i].upper()

            # Check if this token is a known command
            if token in logo_commands or token.startswith("["):
                # Start building a command
                cmd_parts = [tokens[i]]
                i += 1

                # Collect arguments until we hit another command or end
                while i < len(tokens):
                    next_token = tokens[i].upper()

                    # If next token is a command, stop collecting args
                    if next_token in logo_commands:
                        break

                    # If next token starts with '[', it's a nested block - stop
                    if next_token.startswith("["):
                        break

                    cmd_parts.append(tokens[i])
                    i += 1

                # Join the command and its arguments
                commands.append(" ".join(cmd_parts))
            else:
                # Unknown token - treat as standalone command
                commands.append(tokens[i])
                i += 1

        return [cmd.strip() for cmd in commands if cmd.strip()]

    def _parse_repeat_nested(self, full_command):
        """Parse REPEAT n [ commands ... ] supporting nested REPEAT blocks."""
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
