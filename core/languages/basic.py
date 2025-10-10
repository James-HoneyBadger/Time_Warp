"""
BASIC Language Executor for TimeWarp IDE
========================================

BASIC (Beginner's All-purpose Symbolic Instruction Code) is a family of general-purpose,
high-level programming languages designed for ease of use.

This module handles BASIC command execution including:
- Variable assignment (LET)
- Text output (PRINT)
- User input (INPUT)
- Control flow (IF/THEN, FOR/NEXT, GOTO, GOSUB/RETURN)
- Comments (REM)
"""

import re
import time


class BasicExecutor:
    """Handles BASIC language command execution"""

    def __init__(self, interpreter):
        """Initialize with reference to main interpreter"""
        self.interpreter = interpreter
        self.pygame_screen = None
        self.pygame_clock = None
        self.current_color = (255, 255, 255)  # White default

    def _init_pygame_graphics(self, width, height, title):
        """Initialize pygame graphics for standalone mode"""
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

            self.interpreter.log_output(f"✅ Pygame window created: {width}x{height} '{title}'")
            return True
        except ImportError:
            self.interpreter.log_output("❌ Error: pygame not available for graphics")
            return False
        except Exception as e:
            self.interpreter.log_output(f"❌ Error initializing pygame: {e}")
            return False

    def execute_command(self, command):
        """Execute a BASIC command and return the result"""
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
            # Game and Graphics Commands
            # Game Development Commands (BASIC style)
            elif cmd.startswith("GAME"):
                return self._handle_game_commands(command, cmd, parts)
            # Multiplayer (BASIC style)
            elif cmd.startswith("MP") or cmd.startswith("NET"):
                return self._handle_multiplayer_commands(command, cmd, parts)
            # Audio System Commands (BASIC style)
            elif cmd.startswith("SOUND") or cmd.startswith("MUSIC") or cmd == "MASTERVOLUME":
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
                        indices_str = var_name[var_name.index("(") + 1 : var_name.rindex(")")]
                        indices = [
                            int(self.interpreter.evaluate_expression(idx.strip())) for idx in indices_str.split(",")
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
            m = re.match(r"FOR\s+([A-Za-z_]\w*)\s*=\s*(.+?)\s+TO\s+(.+?)(?:\s+STEP\s+(.+))?$", command, re.IGNORECASE)
            if m:
                var_name = m.group(1)
                start_expr = m.group(2).strip()
                end_expr = m.group(3).strip()
                step_expr = m.group(4).strip() if m.group(4) else None

                start_val = self.interpreter.evaluate_expression(start_expr)
                end_val = self.interpreter.evaluate_expression(end_expr)
                step_val = self.interpreter.evaluate_expression(step_expr) if step_expr is not None else 1

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
                    {"var": var_name, "end": end_val, "step": step_val, "for_line": self.interpreter.current_line}
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
                    self.interpreter.debug_output(f"NEXT for unknown variable {var_spec}")
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
                        array = [0] * (dimensions[0] + 1)  # +1 for BASIC 0-based indexing
                    elif len(dimensions) == 2:
                        array = [[0 for _ in range(dimensions[1] + 1)] for _ in range(dimensions[0] + 1)]
                    else:
                        # For higher dimensions, create nested lists
                        def create_array(dims):
                            if len(dims) == 1:
                                return [0] * (dims[0] + 1)
                            else:
                                return [create_array(dims[1:]) for _ in range(dims[0] + 1)]

                        array = create_array(dimensions)

                    # Store the array
                    self.interpreter.variables[array_name] = array
                    self.interpreter.log_output(f"Array {array_name} declared with dimensions {dimensions}")
        except Exception as e:
            self.interpreter.debug_output(f"DIM statement error: {e}")
        return "continue"

    def _handle_game_commands(self, command, cmd, parts):
        """Handle game development commands"""
        if cmd == "GAMESCREEN":
            # GAMESCREEN width, height [, title]
            if len(parts) >= 3:
                try:
                    width = int(parts[1].rstrip(","))
                    height = int(parts[2].rstrip(","))
                    title = " ".join(parts[3:]).strip('"') if len(parts) > 3 else "TimeWarp Game Window"
                    self.interpreter.log_output(f"🎮 Game screen initialized: {width}x{height} - {title}")

                    # Initialize graphics - either IDE canvas or standalone pygame
                    if hasattr(self.interpreter, "ide_turtle_canvas") and self.interpreter.ide_turtle_canvas:
                        # IDE mode - use turtle canvas
                        canvas = self.interpreter.ide_turtle_canvas
                        canvas.delete("all")  # Clear canvas
                        canvas.config(width=min(width, 600), height=min(height, 400))  # Limit size
                        canvas.create_text(width // 2, 20, text=title, font=("Arial", 16), fill="white")
                        self.interpreter.log_output("🎨 Graphics canvas initialized for game")
                    else:
                        # Standalone mode - use pygame
                        self._init_pygame_graphics(width, height, title)
                        self.interpreter.log_output("🎮 Pygame graphics initialized for standalone game")
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
                    self.interpreter.log_output(f"🎨 Background color set to RGB({r},{g},{b})")

                    if hasattr(self.interpreter, "ide_turtle_canvas") and self.interpreter.ide_turtle_canvas:
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
            if hasattr(self.interpreter, "ide_turtle_canvas") and self.interpreter.ide_turtle_canvas:
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
                    self.interpreter.log_output(f"🎨 Drawing color set to RGB({r},{g},{b})")
                except ValueError:
                    self.interpreter.log_output("Error: Invalid GAMECOLOR values")
        elif cmd == "GAMEPOINT":
            # GAMEPOINT x, y - draw a point
            if len(parts) >= 3:
                try:
                    x = int(parts[1].rstrip(","))
                    y = int(parts[2].rstrip(","))
                    color = self.interpreter.variables.get("GAME_COLOR", "#FFFFFF")

                    if hasattr(self.interpreter, "ide_turtle_canvas") and self.interpreter.ide_turtle_canvas:
                        # IDE mode
                        canvas = self.interpreter.ide_turtle_canvas
                        canvas.create_oval(x, y, x + 2, y + 2, fill=color, outline=color, tags="game_objects")
                    elif self.pygame_screen:
                        # Pygame mode
                        import pygame

                        pygame.draw.circle(self.pygame_screen, self.current_color, (x, y), 1)
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

                    if hasattr(self.interpreter, "ide_turtle_canvas") and self.interpreter.ide_turtle_canvas:
                        # IDE mode
                        canvas = self.interpreter.ide_turtle_canvas
                        if filled:
                            canvas.create_rectangle(
                                x, y, x + width, y + height, fill=color, outline=color, tags="game_objects"
                            )
                        else:
                            canvas.create_rectangle(x, y, x + width, y + height, outline=color, tags="game_objects")
                    elif self.pygame_screen:
                        # Pygame mode
                        import pygame

                        rect = pygame.Rect(x, y, width, height)
                        if filled:
                            pygame.draw.rect(self.pygame_screen, self.current_color, rect)
                        else:
                            pygame.draw.rect(self.pygame_screen, self.current_color, rect, 2)
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

                    if hasattr(self.interpreter, "ide_turtle_canvas") and self.interpreter.ide_turtle_canvas:
                        # IDE mode
                        canvas = self.interpreter.ide_turtle_canvas
                        canvas.create_text(x, y, text=text, fill=color, font=("Arial", 12), tags="game_objects")
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
            if hasattr(self.interpreter, "ide_turtle_canvas") and self.interpreter.ide_turtle_canvas:
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

                    if hasattr(self.interpreter, "ide_turtle_canvas") and self.interpreter.ide_turtle_canvas:
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
                                x - radius, y - radius, x + radius, y + radius, outline=color, tags="game_objects"
                            )
                    elif self.pygame_screen:
                        # Pygame mode
                        import pygame

                        if filled:
                            pygame.draw.circle(self.pygame_screen, self.current_color, (x, y), radius)
                        else:
                            pygame.draw.circle(self.pygame_screen, self.current_color, (x, y), radius, 2)
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
