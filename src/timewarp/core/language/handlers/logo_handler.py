"""
Logo Turtle Graphics Handler for Time_Warp IDE
Implements Logo-style turtle graphics and geometric programming
"""

import math
from typing import List, Tuple, Optional, Callable, Any
from ..parser import LogoCommandNode


class TurtleState:
    """Represents the state of the Logo turtle"""

    def __init__(self):
        self.x: float = 0.0
        self.y: float = 0.0
        self.heading: float = 0.0  # degrees, 0 = north
        self.pen_down: bool = True
        self.pen_color: str = "black"
        self.pen_width: int = 1

    def copy(self) -> "TurtleState":
        """Create a copy of the turtle state"""
        new_state = TurtleState()
        new_state.x = self.x
        new_state.y = self.y
        new_state.heading = self.heading
        new_state.pen_down = self.pen_down
        new_state.pen_color = self.pen_color
        new_state.pen_width = self.pen_width
        return new_state


class LogoPath:
    """Represents a path drawn by the turtle"""

    def __init__(
        self,
        start_x: float,
        start_y: float,
        end_x: float,
        end_y: float,
        color: str = "black",
        width: int = 1,
    ):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.color = color
        self.width = width


class LogoHandler:
    """Handler for Logo turtle graphics commands"""

    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.turtle = TurtleState()
        self.paths: List[LogoPath] = []
        self.state_stack: List[TurtleState] = []

        # Graphics callbacks
        self.draw_callback: Optional[Callable[[LogoPath], None]] = None
        self.clear_callback: Optional[Callable[[], None]] = None

        # Bounds tracking
        self.min_x = self.max_x = 0.0
        self.min_y = self.max_y = 0.0

    def execute_command(self, node: LogoCommandNode) -> Any:
        """Execute a Logo command"""
        command = node.command.upper()
        args = [self.interpreter.execute(arg) for arg in node.arguments]

        # Movement commands
        if command in ["FORWARD", "FD"]:
            return self._forward(args[0] if args else 1)
        elif command in ["BACK", "BK"]:
            return self._forward(-(args[0] if args else 1))
        elif command in ["LEFT", "LT"]:
            return self._turn_left(args[0] if args else 90)
        elif command in ["RIGHT", "RT"]:
            return self._turn_right(args[0] if args else 90)

        # Pen commands
        elif command in ["PENUP", "PU"]:
            return self._pen_up()
        elif command in ["PENDOWN", "PD"]:
            return self._pen_down()
        elif command == "SETCOLOR":
            return self._set_color(args[0] if args else "black")
        elif command == "SETWIDTH":
            return self._set_width(args[0] if args else 1)

        # Position commands
        elif command == "HOME":
            return self._home()
        elif command == "SETXY":
            return self._set_position(
                args[0] if len(args) > 0 else 0, args[1] if len(args) > 1 else 0
            )
        elif command == "SETHEADING":
            return self._set_heading(args[0] if args else 0)

        # Screen commands
        elif command in ["CLEARSCREEN", "CS"]:
            return self._clear_screen()

        # Control commands
        elif command == "REPEAT":
            return self._repeat(
                args[0] if args else 1,
                node.arguments[1:] if len(node.arguments) > 1 else [],
            )

        # Query commands
        elif command == "XCOR":
            return self.turtle.x
        elif command == "YCOR":
            return self.turtle.y
        elif command == "HEADING":
            return self.turtle.heading
        elif command == "PENDOWN?":
            return self.turtle.pen_down

        else:
            raise ValueError(f"Unknown Logo command: {command}")

    def _forward(self, distance: float) -> None:
        """Move turtle forward by distance"""
        old_x, old_y = self.turtle.x, self.turtle.y

        # Calculate new position
        radians = math.radians(self.turtle.heading)
        self.turtle.x += distance * math.sin(radians)
        self.turtle.y += distance * math.cos(radians)

        # Update bounds
        self._update_bounds(self.turtle.x, self.turtle.y)

        # Draw line if pen is down
        if self.turtle.pen_down:
            path = LogoPath(
                old_x,
                old_y,
                self.turtle.x,
                self.turtle.y,
                self.turtle.pen_color,
                self.turtle.pen_width,
            )
            self.paths.append(path)

            if self.draw_callback:
                self.draw_callback(path)

    def _turn_left(self, angle: float) -> None:
        """Turn turtle left by angle degrees"""
        self.turtle.heading = (self.turtle.heading - angle) % 360

    def _turn_right(self, angle: float) -> None:
        """Turn turtle right by angle degrees"""
        self.turtle.heading = (self.turtle.heading + angle) % 360

    def _pen_up(self) -> None:
        """Lift pen up (stop drawing)"""
        self.turtle.pen_down = False

    def _pen_down(self) -> None:
        """Put pen down (start drawing)"""
        self.turtle.pen_down = True

    def _set_color(self, color: str) -> None:
        """Set pen color"""
        self.turtle.pen_color = str(color)

    def _set_width(self, width: int) -> None:
        """Set pen width"""
        self.turtle.pen_width = int(width)

    def _home(self) -> None:
        """Move turtle to home position (0, 0) facing north"""
        old_x, old_y = self.turtle.x, self.turtle.y
        self.turtle.x = 0.0
        self.turtle.y = 0.0
        self.turtle.heading = 0.0

        # Draw line if pen is down
        if self.turtle.pen_down:
            path = LogoPath(
                old_x, old_y, 0.0, 0.0, self.turtle.pen_color, self.turtle.pen_width
            )
            self.paths.append(path)

            if self.draw_callback:
                self.draw_callback(path)

    def _set_position(self, x: float, y: float) -> None:
        """Set turtle position"""
        old_x, old_y = self.turtle.x, self.turtle.y
        self.turtle.x = float(x)
        self.turtle.y = float(y)

        # Update bounds
        self._update_bounds(self.turtle.x, self.turtle.y)

        # Draw line if pen is down
        if self.turtle.pen_down:
            path = LogoPath(
                old_x,
                old_y,
                self.turtle.x,
                self.turtle.y,
                self.turtle.pen_color,
                self.turtle.pen_width,
            )
            self.paths.append(path)

            if self.draw_callback:
                self.draw_callback(path)

    def _set_heading(self, heading: float) -> None:
        """Set turtle heading"""
        self.turtle.heading = float(heading) % 360

    def _clear_screen(self) -> None:
        """Clear the screen and reset turtle"""
        self.paths.clear()
        self.turtle = TurtleState()
        self.min_x = self.max_x = 0.0
        self.min_y = self.max_y = 0.0

        if self.clear_callback:
            self.clear_callback()

    def _repeat(self, count: int, commands: List[Any]) -> None:
        """Repeat commands count times"""
        for _ in range(int(count)):
            for command in commands:
                if hasattr(command, "command"):  # It's a LogoCommandNode
                    self.execute_command(command)
                else:
                    # Execute as general statement
                    self.interpreter.execute(command)

    def _update_bounds(self, x: float, y: float) -> None:
        """Update drawing bounds"""
        self.min_x = min(self.min_x, x)
        self.max_x = max(self.max_x, x)
        self.min_y = min(self.min_y, y)
        self.max_y = max(self.max_y, y)

    def get_bounds(self) -> Tuple[float, float, float, float]:
        """Get drawing bounds (min_x, min_y, max_x, max_y)"""
        return (self.min_x, self.min_y, self.max_x, self.max_y)

    def push_state(self) -> None:
        """Push current turtle state onto stack"""
        self.state_stack.append(self.turtle.copy())

    def pop_state(self) -> None:
        """Pop turtle state from stack"""
        if self.state_stack:
            self.turtle = self.state_stack.pop()

    def set_callbacks(
        self,
        draw_callback: Callable[[LogoPath], None],
        clear_callback: Callable[[], None],
    ):
        """Set graphics callbacks"""
        self.draw_callback = draw_callback
        self.clear_callback = clear_callback

    def reset(self):
        """Reset Logo graphics state"""
        self.turtle = TurtleState()
        self.paths.clear()
        self.state_stack.clear()
        self.min_x = self.max_x = 0.0
        self.min_y = self.max_y = 0.0

    def export_svg(self, width: int = 400, height: int = 400) -> str:
        """Export paths as SVG"""
        if not self.paths:
            return f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg"></svg>'

        # Calculate scale and offset
        bounds = self.get_bounds()
        drawing_width = bounds[2] - bounds[0]
        drawing_height = bounds[3] - bounds[1]

        if drawing_width == 0 and drawing_height == 0:
            scale = 1
            offset_x = width // 2
            offset_y = height // 2
        else:
            scale_x = (width - 40) / drawing_width if drawing_width > 0 else 1
            scale_y = (height - 40) / drawing_height if drawing_height > 0 else 1
            scale = min(scale_x, scale_y)

            offset_x = width // 2 - (bounds[0] + bounds[2]) * scale // 2
            offset_y = height // 2 - (bounds[1] + bounds[3]) * scale // 2

        svg_lines = [
            f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
        ]

        for path in self.paths:
            x1 = path.start_x * scale + offset_x
            y1 = height - (path.start_y * scale + offset_y)  # Flip Y coordinate
            x2 = path.end_x * scale + offset_x
            y2 = height - (path.end_y * scale + offset_y)  # Flip Y coordinate

            svg_lines.append(
                f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="{path.color}" stroke-width="{path.width}" />'
            )

        svg_lines.append("</svg>")
        return "\\n".join(svg_lines)
