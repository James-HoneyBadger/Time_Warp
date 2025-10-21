"""
Time Warp IDE Unified Canvas System

A modern, feature-rich canvas system designed specifically for
the Time Warp IDE. Supports dynamic theming, font customization,
syntax highlighting, and advanced text/graphics rendering.
"""

import tkinter as tk
import tkinter.font as tkfont
from typing import Dict, List, Optional, Union


class Theme:
    """Theme configuration for Time Warp IDE"""

    def __init__(self, name: str, colors: Dict[str, str]):
        self.name = name
        self.colors = colors

    @property
    def background(self) -> str:
        return self.colors.get("background", "#000000")

    @property
    def foreground(self) -> str:
        return self.colors.get("foreground", "#ffffff")

    @property
    def accent(self) -> str:
        return self.colors.get("accent", "#00ff00")

    @property
    def panel_bg(self) -> str:
        return self.colors.get("panel_bg", "#333333")

    @property
    def panel_fg(self) -> str:
        return self.colors.get("panel_fg", "#ffffff")

    @property
    def cursor_color(self) -> str:
        return self.colors.get("cursor", "#ffffff")

    @property
    def selection_bg(self) -> str:
        return self.colors.get("selection_bg", "#444444")

    @property
    def syntax_colors(self) -> Dict[str, str]:
        return self.colors.get(
            "syntax",
            {
                "keyword": "#ff6b6b",
                "string": "#4ecdc4",
                "number": "#45b7d1",
                "comment": "#7d8796",
                "function": "#f9ca24",
                "variable": "#6c5ce7",
            },
        )


class UnifiedCanvas(tk.Canvas):
    def _append_text(
        self,
        text: str,
        color: Optional[Union[str, int]] = None,
        style: str = "normal",
    ):
        """Append text at the end of the canvas output buffer"""
        if isinstance(color, int):
            color = self._get_color_from_index(color)

        lines = text.split("\n")
        for i, line_text in enumerate(lines):
            if i > 0:
                self.lines.append("")
                self.line_attributes.append({})
                self.cursor_line = len(self.lines) - 1
                self.cursor_col = 0

            current_line = self.lines[self.cursor_line]
            before = current_line[:self.cursor_col]
            after = current_line[self.cursor_col:]
            new_line = before + line_text + after
            self.lines[self.cursor_line] = new_line

            if color or style != "normal":
                line_attrs = self.line_attributes[self.cursor_line]
                if "segments" not in line_attrs:
                    line_attrs["segments"] = []
                start_col = self.cursor_col
                end_col = start_col + len(line_text)
                seg_color = color or self.current_theme.foreground
                line_attrs["segments"].append(
                    {
                        "start": start_col,
                        "end": end_col,
                        "color": seg_color,
                        "style": style,
                    }
                )
            self.cursor_col += len(line_text)

    def write_text(
        self,
        text: str,
        color: Optional[Union[str, int]] = None,
        style: str = "normal",
        line: Optional[int] = None,
    ):
        """Write text to the canvas with advanced formatting (always append for output console)"""
        # Ensure we always append at the end of the buffer for output writes
        try:
            self.cursor_line = len(self.lines) - 1
            self.cursor_col = len(self.lines[self.cursor_line])
        except Exception:
            # If internal state is inconsistent, fallback to default positions
            if not self.lines:
                self.lines = [""]
                self.line_attributes = [{}]
            self.cursor_line = len(self.lines) - 1
            self.cursor_col = len(self.lines[self.cursor_line])
        self._append_text(text, color, style)
        # Use a debounced redraw to avoid blocking the UI when many writes occur
        try:
            self.schedule_redraw()
        except Exception:
            # If scheduling fails, fallback to an immediate redraw
            self.redraw()

    """
    Modern unified canvas for Time Warp IDE with advanced features:
    - Dynamic theming support
    - Customizable fonts
    - Syntax highlighting
    - Line numbers
    - Advanced text and graphics rendering
    - Modern IDE features
    """

    def __init__(
        self,
        parent,
        width: int = 1024,
        height: int = 768,
        font_family: str = "Consolas",
        font_size: int = 12,
        theme: Optional[Theme] = None,
        **kwargs,
    ):
        # Extract our custom parameters
        self.rows = kwargs.pop("rows", 25)
        self.cols = kwargs.pop("cols", 80)

        super().__init__(parent, **kwargs)
        # UnifiedCanvas initialized

        # Canvas dimensions
        self.canvas_width = width
        self.canvas_height = height
        self.config(width=width, height=height)

        # Font configuration
        self.font_family = font_family
        self.font_size = font_size
        self.font = tkfont.Font(family=font_family, size=font_size)

        # Theme system
        self.current_theme = theme or self._create_default_theme()

        # Text buffer system (modern approach) - ensure at least one empty line
        self.lines: List[str] = [""]
        self.line_attributes: List[Dict] = [{}]
        self.cursor_line = 0
        self.cursor_col = 0

        # Display settings
        self.show_line_numbers = False
        self.line_number_width = 50
        self.tab_size = 4
        self.word_wrap = False

        # Update font metrics after all attributes are set
        self.update_font_metrics()

        # Graphics layer
        self.graphics_objects: List[int] = []
        self.graphics_commands: List[Dict] = []

        # Input handling
        self.input_mode = False
        self.input_callback = None
        self.input_buffer = ""

        # Cursor blinking
        self.cursor_visible = True
        self.cursor_blink_timer = None
        self.start_cursor_blink()
        # Redraw scheduling (debounce to avoid UI freezes on many small writes)
        self._redraw_scheduled = False
        self._redraw_after_id = None

    def start_cursor_blink(self):
        """Start the cursor blinking timer"""
        if self.cursor_blink_timer:
            self.after_cancel(self.cursor_blink_timer)
        self.cursor_blink_timer = self.after(500, self._blink_cursor)

    def stop_cursor_blink(self):
        """Stop the cursor blinking timer"""
        if self.cursor_blink_timer:
            self.after_cancel(self.cursor_blink_timer)
            self.cursor_blink_timer = None

    def _blink_cursor(self):
        """Toggle cursor visibility and schedule next blink"""
        self.cursor_visible = not self.cursor_visible
        # Cursor blink can be handled by a scheduled redraw to avoid immediate heavy redraws
        self.schedule_redraw()
        self.cursor_blink_timer = self.after(500, self._blink_cursor)

    def schedule_redraw(self, delay: int = 50):
        """Schedule a debounced redraw on the Tk mainloop.

        Multiple calls within `delay` ms will coalesce into a single redraw.
        """
        try:
            if self._redraw_scheduled:
                return
            self._redraw_scheduled = True
            # Store after id so we can cancel if an immediate redraw is requested
            self._redraw_after_id = self.after(
                delay, self._do_scheduled_redraw
            )
        except Exception:
            # If scheduling fails for any reason, fallback to immediate redraw
            self.redraw()

    def _do_scheduled_redraw(self):
        """Internal handler invoked by Tk after the debounce period."""
        self._redraw_scheduled = False
        self._redraw_after_id = None
        # Perform the visual update
        self.redraw()

    def cancel_scheduled_redraw(self):
        """Cancel a pending scheduled redraw, if any."""
        if self._redraw_after_id:
            try:
                self.after_cancel(self._redraw_after_id)
            except Exception:
                pass
        self._redraw_scheduled = False
        self._redraw_after_id = None

    def redraw_immediate(self):
        """Cancel any scheduled redraw and perform an immediate redraw."""
        self.cancel_scheduled_redraw()
        self.redraw()

    def update_font_metrics(self):
        """Update font metrics when font changes"""
        self.char_width = self.font.measure("W")
        self.char_height = self.font.metrics("linespace")
        visible_width = self.canvas_width - (
            self.line_number_width if self.show_line_numbers else 0
        )
        self.cols = max(1, visible_width // self.char_width)
        self.rows = max(1, self.canvas_height // self.char_height)

    def _create_default_theme(self) -> Theme:
        """Create the default dark theme"""
        return Theme(
            "Time Warp Dark",
            {
                "background": "#1a1a1a",
                "foreground": "#ffffff",
                "accent": "#00ff88",
                "panel_bg": "#2d2d2d",
                "panel_fg": "#ffffff",
                "cursor": "#ffffff",
                "selection_bg": "#404040",
                "syntax": {
                    "keyword": "#ff6b6b",
                    "string": "#4ecdc4",
                    "number": "#45b7d1",
                    "comment": "#7d8796",
                    "function": "#f9ca24",
                    "variable": "#6c5ce7",
                },
            },
        )

    def apply_theme(self, theme: Theme):
        """Apply a theme to the canvas"""
        self.current_theme = theme
        self.config(bg=theme.background)
        self.redraw()

    def set_font(self, family: str, size: int):
        """Dynamically update font settings"""
        self.font_family = family
        self.font_size = size
        self.font.config(family=family, size=size)
        self.update_font_metrics()
        self.redraw()

    def set_theme(self, theme: Theme):
        """Apply a new theme"""
        self.apply_theme(theme)

    def toggle_line_numbers(self):
        """Toggle line number display"""
        self.show_line_numbers = not self.show_line_numbers
        self.update_font_metrics()
        self.redraw()

    def clear_all(self):
        """Clear all content from canvas"""
        self.lines = [""]
        self.line_attributes = [{}]
        self.cursor_line = 0
        self.cursor_col = 0
        self.graphics_objects.clear()
        self.redraw()

    def clear_screen(self):
        """Clear the screen (alias for clear_all for compatibility)"""
        self.clear_all()

    def clear_text(self):
        """Clear only text content"""
        self.lines = [""]
        self.line_attributes = [{}]
        self.cursor_line = 0
        self.cursor_col = 0
        self.redraw()

    def redraw(self):
        """Redraw the entire canvas with current content (output-only)"""
        self.delete("all")
        # Don't clear graphics_objects here - we'll recreate them

        # Draw background
        self.create_rectangle(
            0,
            0,
            self.canvas_width,
            self.canvas_height,
            fill=self.current_theme.background,
            outline="",
        )

        x_offset = self.line_number_width if self.show_line_numbers else 0

        # Draw each line
        for line_num, line_text in enumerate(self.lines):
            y = line_num * self.char_height
            if self.show_line_numbers:
                line_num_text = f"{line_num + 1:4d} "
                self.create_text(
                    5,
                    y,
                    text=line_num_text,
                    font=self.font,
                    fill=self.current_theme.panel_fg,
                    anchor="nw",
                )
            self._draw_line_text(line_text, x_offset, y, line_num)

        # Do NOT draw cursor or input prompt

        # Recreate graphics on top
        self._redraw_graphics()

    def _insert_text_at_line(
        self,
        text: str,
        line_num: int,
        color: Optional[Union[str, int]] = None,
        style: str = "normal",
    ):
        """Insert text at specific line"""
        while len(self.lines) <= line_num:
            self.lines.append("")
            self.line_attributes.append({})

        if isinstance(color, int):
            color = self._get_color_from_index(color)

        self.lines[line_num] = text
        if color or style != "normal":
            self.line_attributes[line_num] = {
                "segments": [
                    {
                        "start": 0,
                        "end": len(text),
                        "color": color or self.current_theme.foreground,
                        "style": style,
                    }
                ]
            }

    def _get_color_from_index(self, index: int) -> str:
        """Convert color index to actual color"""
        palette = [
            "#000000",
            "#000080",
            "#008000",
            "#008080",
            "#800000",
            "#800080",
            "#808000",
            "#c0c0c0",
            "#808080",
            "#0000ff",
            "#00ff00",
            "#00ffff",
            "#ff0000",
            "#ff00ff",
            "#ffff00",
            "#ffffff",
        ]
        if 0 <= index < len(palette):
            return palette[index]
        return self.current_theme.foreground

    def _redraw_graphics(self):
        """Recreate all graphics objects"""
        self.graphics_objects.clear()
        for cmd in self.graphics_commands:
            if cmd["type"] == "line":
                obj_id = self.create_line(
                    cmd["x1"],
                    cmd["y1"],
                    cmd["x2"],
                    cmd["y2"],
                    fill=cmd["color"],
                    width=cmd["width"],
                    **cmd.get("kwargs", {}),
                )
            elif cmd["type"] == "rectangle":
                obj_id = self.create_rectangle(
                    cmd["x1"],
                    cmd["y1"],
                    cmd["x2"],
                    cmd["y2"],
                    outline=cmd["color"],
                    fill=cmd["fill_color"],
                    width=cmd["width"],
                    **cmd.get("kwargs", {}),
                )
            elif cmd["type"] == "circle":
                obj_id = self.create_oval(
                    cmd["x1"],
                    cmd["y1"],
                    cmd["x2"],
                    cmd["y2"],
                    outline=cmd["color"],
                    fill=cmd["fill_color"],
                    width=cmd["width"],
                    **cmd.get("kwargs", {}),
                )
            elif cmd["type"] == "text":
                obj_id = self.create_text(
                    cmd["x"],
                    cmd["y"],
                    text=cmd["text"],
                    fill=cmd["color"],
                    font=self.font,
                    **cmd.get("kwargs", {}),
                )
            elif cmd["type"] == "polygon":
                obj_id = self.create_polygon(
                    cmd["points"],
                    outline=cmd["color"],
                    fill=cmd["fill_color"],
                    width=cmd["width"],
                    **cmd.get("kwargs", {}),
                )
            self.graphics_objects.append(obj_id)

    def _draw_line_text(self, text: str, x_offset: int, y: int, line_num: int):
        """Draw a single line of text with formatting"""
        attrs = (
            self.line_attributes[line_num]
            if line_num < len(self.line_attributes)
            else {}
        )

        if "segments" in attrs and attrs["segments"]:
            for segment in attrs["segments"]:
                start = segment["start"]
                end = min(segment["end"], len(text))
                if start < end:
                    segment_text = text[start:end]
                    x = x_offset + start * self.char_width
                    color = segment.get("color", self.current_theme.foreground)
                    self.create_text(
                        x,
                        y,
                        text=segment_text,
                        font=self.font,
                        fill=color,
                        anchor="nw",
                    )
        else:
            color = attrs.get("color", self.current_theme.foreground)
            self.create_text(
                x_offset, y, text=text, font=self.font, fill=color, anchor="nw"
            )

    def prompt_input(self, prompt: str = "", callback=None):
        """Set up input prompt in the output console"""
        self.input_mode = True
        self.input_callback = callback
        self.input_buffer = ""
        # Show prompt
        if prompt:
            self.write_text(prompt)
        # The cursor will be shown in redraw() when input_mode is True
        self.redraw()

    def _on_key_press(self, event):
        """Handle key press events"""
        key = event.keysym
        char = event.char

        # Handle special keys first
        if key == "Return":
            if self.input_mode:
                if self.input_callback:
                    self.input_callback(self.input_buffer)
                self.input_mode = False
                self.write_text("\n")
                self.redraw()
                return "break"
            else:
                # Insert newline in text editor mode
                self._insert_newline()
                return "break"

        elif key == "BackSpace":
            if self.input_mode:
                if self.input_buffer:
                    self.input_buffer = self.input_buffer[:-1]
                    if self.cursor_col > 0:
                        self.cursor_col -= 1
                        current_line = self.lines[self.cursor_line]
                        self.lines[self.cursor_line] = current_line[:-1]
                    self.redraw()
                return "break"
            else:
                # Delete character in text editor mode
                self._delete_character()
                return "break"

        elif key == "Delete":
            self._delete_character(forward=True)
            return "break"

        elif key == "Left":
            self._move_cursor_left()
            return "break"

        elif key == "Right":
            self._move_cursor_right()
            return "break"

        elif key == "Up":
            self._move_cursor_up()
            return "break"

        elif key == "Down":
            self._move_cursor_down()
            return "break"

        elif key == "Home":
            self.cursor_col = 0
            self.redraw()
            return "break"

        elif key == "End":
            if self.cursor_line < len(self.lines):
                self.cursor_col = len(self.lines[self.cursor_line])
            self.redraw()
            return "break"

        elif key == "Tab":
            if not self.input_mode:
                self._insert_text("\t")
                return "break"

        # Handle printable characters
        elif char and char.isprintable():
            if self.input_mode:
                self.input_buffer += char
                self._append_text(char)
                return "break"
            else:
                # Insert character in text editor mode
                self._insert_text(char)
                return "break"

        return "break"

    def _insert_text(self, text: str):
        """Insert text at cursor position in text editor mode"""
        if self.cursor_line >= len(self.lines):
            self.lines.extend([""] * (self.cursor_line - len(self.lines) + 1))
            self.line_attributes.extend(
                [{}] * (self.cursor_line - len(self.line_attributes) + 1)
            )

        current_line = self.lines[self.cursor_line]
        before = current_line[:self.cursor_col]
        after = current_line[self.cursor_col:]
        self.lines[self.cursor_line] = before + text + after
        self.cursor_col += len(text)
        self.redraw()

    def _insert_newline(self):
        """Insert a newline at cursor position"""
        if self.cursor_line >= len(self.lines):
            self.lines.extend([""] * (self.cursor_line - len(self.lines) + 1))
            self.line_attributes.extend(
                [{}] * (self.cursor_line - len(self.line_attributes) + 1)
            )

        current_line = self.lines[self.cursor_line]
        before = current_line[:self.cursor_col]
        after = current_line[self.cursor_col:]

        self.lines[self.cursor_line] = before
        self.lines.insert(self.cursor_line + 1, after)
        self.line_attributes.insert(self.cursor_line + 1, {})

        self.cursor_line += 1
        self.cursor_col = 0
        self.redraw()

    def _delete_character(self, forward: bool = False):
        """Delete character at cursor position (or after cursor if forward=True)"""
        if self.cursor_line >= len(self.lines):
            return

        current_line = self.lines[self.cursor_line]
        if forward:
            # Delete character after cursor
            if self.cursor_col < len(current_line):
                self.lines[self.cursor_line] = (
                    current_line[: self.cursor_col]
                    + current_line[self.cursor_col + 1:]
                )
            elif self.cursor_line < len(self.lines) - 1:
                # Join with next line
                next_line = self.lines[self.cursor_line + 1]
                self.lines[self.cursor_line] = current_line + next_line
                del self.lines[self.cursor_line + 1]
                del self.line_attributes[self.cursor_line + 1]
        else:
            # Delete character before cursor
            if self.cursor_col > 0:
                self.lines[self.cursor_line] = (
                    current_line[: self.cursor_col - 1]
                    + current_line[self.cursor_col:]
                )
                self.cursor_col -= 1
            elif self.cursor_line > 0:
                # Join with previous line
                prev_line = self.lines[self.cursor_line - 1]
                prev_col = len(prev_line)
                self.lines[self.cursor_line - 1] = prev_line + current_line
                del self.lines[self.cursor_line]
                del self.line_attributes[self.cursor_line]
                self.cursor_line -= 1
                self.cursor_col = prev_col

        self.redraw()

    def _move_cursor_right(self):
        """Move cursor right"""
        if self.cursor_col < len(self.lines[self.cursor_line]):
            self.cursor_col += 1
        elif self.cursor_line < len(self.lines) - 1:
            self.cursor_line += 1
            self.cursor_col = 0
        self.redraw()

    def _move_cursor_up(self):
        """Move cursor up"""
        if self.cursor_line > 0:
            self.cursor_line -= 1
            self.cursor_col = min(
                self.cursor_col, len(self.lines[self.cursor_line])
            )
        self.redraw()

    def _move_cursor_down(self):
        """Move cursor down"""
        if self.cursor_line < len(self.lines) - 1:
            self.cursor_line += 1
            self.cursor_col = min(
                self.cursor_col, len(self.lines[self.cursor_line])
            )
        self.redraw()

    def _on_mouse_click(self, event):
        """Handle mouse click events"""
        x_offset = self.line_number_width if self.show_line_numbers else 0

        # safe char width/height
        cw = getattr(self, "char_width", 1) or 1
        ch = getattr(self, "char_height", 1) or 1

        # compute column and line indices
        raw_x = event.x - x_offset
        col = max(0, raw_x // cw)
        line_index = max(0, event.y // ch)

        # ensure at least one line exists
        if not self.lines:
            self.lines = [""]
            self.line_attributes = [{}]

        # if click below existing lines, extend lines so cursor can move there
        if line_index >= len(self.lines):
            add_count = line_index - len(self.lines) + 1
            self.lines.extend([""] * add_count)
            self.line_attributes.extend([{}] * add_count)

        # set cursor (allow column beyond end of line)
        self.cursor_line = min(line_index, len(self.lines) - 1)
        self.cursor_col = max(0, col)

        self.redraw()

        # Ensure canvas gets focus when clicked
        self.focus_set()

    def _on_resize(self, event):
        """Handle canvas resize"""
        self.canvas_width = event.width
        self.canvas_height = event.height
        self.update_font_metrics()
        self.redraw()

    def _on_focus_in(self, event):
        """Handle focus in event"""
        # Avoid re-setting focus inside the focus-in handler which can
        # trigger repeated focus events and cause the UI to hang.
        try:
            current = self.focus_get()
            if current is not self:
                # Only set focus if it's not already this widget
                self.focus_set()
        except Exception:
            # If focus_get isn't available or fails, don't block
            pass

        # Start the cursor blink timer when we receive focus
        self.start_cursor_blink()

    def _on_focus_out(self, event):
        """Handle focus out event"""
        self.stop_cursor_blink()
        self.cursor_visible = False
        self.redraw()

    # Graphics methods (enhanced)
    def draw_line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        color: Optional[str] = None,
        width: int = 1,
        **kwargs,
    ):
        """Draw a line"""
        color = color or self.current_theme.accent
        line_id = self.create_line(
            x1, y1, x2, y2, fill=color, width=width, **kwargs
        )
        self.graphics_objects.append(line_id)
        self.graphics_commands.append(
            {
                "type": "line",
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "color": color,
                "width": width,
                "kwargs": kwargs,
            }
        )
        return line_id

    def draw_rectangle(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        filled: bool = False,
        color: Optional[str] = None,
        width: int = 1,
        **kwargs,
    ):
        """Draw a rectangle"""
        color = color or self.current_theme.accent
        fill_color = color if filled else ""
        rect_id = self.create_rectangle(
            x1,
            y1,
            x2,
            y2,
            outline=color,
            fill=fill_color,
            width=width,
            **kwargs,
        )
        self.graphics_objects.append(rect_id)
        self.graphics_commands.append(
            {
                "type": "rectangle",
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "color": color,
                "fill_color": fill_color,
                "width": width,
                "kwargs": kwargs,
            }
        )
        return rect_id

    def draw_circle(
        self,
        center_x: float,
        center_y: float,
        radius: float,
        filled: bool = False,
        color: Optional[str] = None,
        width: int = 1,
        **kwargs,
    ):
        """Draw a circle"""
        color = color or self.current_theme.accent
        x1 = center_x - radius
        y1 = center_y - radius
        x2 = center_x + radius
        y2 = center_y + radius
        fill_color = color if filled else ""
        circle_id = self.create_oval(
            x1,
            y1,
            x2,
            y2,
            outline=color,
            fill=fill_color,
            width=width,
            **kwargs,
        )
        self.graphics_objects.append(circle_id)
        self.graphics_commands.append(
            {
                "type": "circle",
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "color": color,
                "fill_color": fill_color,
                "width": width,
                "kwargs": kwargs,
            }
        )
        return circle_id

    def draw_polygon(
        self, points, filled=False, color=None, width=1, **kwargs
    ):
        """Draw a polygon"""
        color = color or self.current_theme.accent
        fill_color = color if filled else ""
        polygon_id = self.create_polygon(
            points, outline=color, fill=fill_color, width=width, **kwargs
        )
        self.graphics_objects.append(polygon_id)
        self.graphics_commands.append(
            {
                "type": "polygon",
                "points": points,
                "color": color,
                "fill_color": fill_color,
                "width": width,
                "kwargs": kwargs,
            }
        )
        return polygon_id

    def draw_text(
        self,
        x: float,
        y: float,
        text: str,
        color: Optional[str] = None,
        **kwargs,
    ):
        """Draw text at graphics coordinates"""
        color = color or self.current_theme.foreground
        text_id = self.create_text(
            x, y, text=text, fill=color, font=self.font, **kwargs
        )
        self.graphics_objects.append(text_id)
        self.graphics_commands.append(
            {
                "type": "text",
                "x": x,
                "y": y,
                "text": text,
                "color": color,
                "kwargs": kwargs,
            }
        )
        return text_id

    # Legacy compatibility methods
    def set_cursor(self, x, y):
        """Legacy cursor positioning"""
        self.cursor_col = x
        self.cursor_line = y

    def set_text_color(self, color):
        """Legacy text color setting"""
        pass

    def set_bg_color(self, color):
        """Legacy background color setting"""
        pass

    def get_mode_info(self):
        """Get current canvas mode information"""
        return {
            "name": "Time Warp Unified Canvas",
            "width": self.canvas_width,
            "height": self.canvas_height,
            "text_cols": self.cols,
            "text_rows": self.rows,
            "theme": self.current_theme.name,
            "font_family": self.font_family,
            "font_size": self.font_size,
            "type": "modern_unified",
        }

    def get_palette(self):
        """Get color palette (legacy compatibility)"""
        return [
            "#000000",
            "#000080",
            "#008000",
            "#008080",
            "#800000",
            "#800080",
            "#808000",
            "#c0c0c0",
            "#808080",
            "#0000ff",
            "#00ff00",
            "#00ffff",
            "#ff0000",
            "#ff00ff",
            "#ffff00",
            "#ffffff",
        ]

    def set_screen_mode(self, mode):
        """Legacy screen mode setting (no-op)"""
        pass
