"""
Unified Canvas System for Time_Warp IDE

Implements GW BASIC screen modes with unified text and graphics rendering.
Supports keyboard input prompts and multiple display modes.
"""

import tkinter as tk
import tkinter.font as tkfont


class UnifiedCanvas(tk.Canvas):
    """
    A completely rewritten UnifiedCanvas class for text and graphics rendering.
    Ensures proper text rendering, cursor positioning, and CR/LF handling.
    """

    def __init__(self, parent, rows=25, cols=80, font_family="Courier", font_size=12, **kwargs):
        super().__init__(parent, **kwargs)

        # Canvas configuration
        self.rows = rows
        self.cols = cols
        self.font_family = font_family
        self.font_size = font_size

        # Store background color from kwargs or default to black
        self.bg_color = kwargs.get('bg', 'black')

        # Initialize font and character dimensions
        self.font = tkfont.Font(family=self.font_family, size=self.font_size)
        self.char_width = self.font.measure("W")
        self.char_height = self.font.metrics("linespace")

        # Initialize screen buffer
        self.screen_buffer = [[" " for _ in range(self.cols)] for _ in range(self.rows)]
        self.cursor_x = 0
        self.cursor_y = 0

        # Configure canvas size
        self.config(width=self.cols * self.char_width, height=self.rows * self.char_height)

        # Bind events
        self.bind("<Key>", self._on_key_press)
        self.focus_set()

    def clear_screen(self):
        """Clear the entire screen and reset the cursor."""
        self.screen_buffer = [[" " for _ in range(self.cols)] for _ in range(self.rows)]
        self.cursor_x = 0
        self.cursor_y = 0
        self.redraw()

    def clear_text(self):
        """Clear all text from the canvas."""
        self.clear_screen()

    def clear_graphics(self):
        """Clear all graphics from the canvas."""
        # For now, just clear the screen since graphics are integrated
        self.clear_screen()

    def set_cursor(self, x, y):
        """Set cursor position."""
        self.cursor_x = x
        self.cursor_y = y

    def set_text_color(self, color):
        """Set text color (placeholder for compatibility)."""
        pass

    def set_bg_color(self, color):
        """Set background color (placeholder for compatibility)."""
        pass

    def get_mode_info(self):
        """Get current mode information."""
        return {
            "name": "Unified Canvas",
            "width": self.cols * self.char_width,
            "height": self.rows * self.char_height,
            "text_cols": self.cols,
            "text_rows": self.rows,
            "colors": 16,
            "type": "unified"
        }

    def get_palette(self):
        """Get current color palette."""
        return ["black", "blue", "green", "cyan", "red", "magenta", "brown", "lightgray",
                "darkgray", "lightblue", "lightgreen", "lightcyan", "lightred", "lightmagenta",
                "yellow", "white"]

    def write_text(self, text, color=None):
        """Write text to the canvas at the current cursor position with optional color."""
        if color is None:
            color = "black"  # Default color
        elif isinstance(color, int):
            # Map integer color to a hex code (e.g., 12 -> "#FF00FF")
            palette = ["black", "blue", "green", "cyan", "red", "magenta", "brown", "lightgray",
                       "darkgray", "lightblue", "lightgreen", "lightcyan", "lightred", "lightmagenta",
                       "yellow", "white"]
            color = palette[color % len(palette)]

        for char in text:
            if char == "\n":
                self.cursor_x = 0
                self.cursor_y += 1
            elif char == "\r":
                self.cursor_x = 0
            else:
                if self.cursor_x < self.cols and self.cursor_y < self.rows:
                    self.screen_buffer[self.cursor_y][self.cursor_x] = char
                    self.cursor_x += 1

            # Handle scrolling if cursor goes out of bounds
            if self.cursor_x >= self.cols:
                self.cursor_x = 0
                self.cursor_y += 1
            if self.cursor_y >= self.rows:
                self.scroll_up()
                self.cursor_y = self.rows - 1

        self.redraw(color=color)

    def redraw(self, color="black"):
        """Redraw the entire canvas based on the screen buffer with the specified color."""
        self.delete("all")

        # Fill the background with the configured background color
        self.create_rectangle(
            0, 0, self.cols * self.char_width, self.rows * self.char_height,
            fill=self.bg_color, outline=self.bg_color, tags="background"
        )

        # Render each character in the buffer
        for row in range(self.rows):
            for col in range(self.cols):
                char = self.screen_buffer[row][col]
                if char.strip():  # Ensure non-empty characters are rendered
                    x = col * self.char_width
                    y = row * self.char_height
                    self.create_text(
                        x, y, text=char, font=self.font, fill=color, anchor="nw"
                    )

    def scroll_up(self):
        """Scroll the screen up by one line."""
        self.screen_buffer.pop(0)
        self.screen_buffer.append([" " for _ in range(self.cols)])

    def _on_key_press(self, event):
        """Handle key press events for input."""
        if hasattr(self, 'input_active') and self.input_active:
            # Handle input mode
            key = event.keysym
            char = event.char

            if key == "Return":
                # Submit input
                if hasattr(self, 'input_callback') and self.input_callback:
                    self.input_callback(self.input_buffer)
                self.input_active = False
                # Move to next line
                self.write_text("\n")
                return "break"

            elif key == "BackSpace":
                if self.input_buffer:
                    self.input_buffer = self.input_buffer[:-1]
                    # Move cursor back
                    if self.cursor_x > 0:
                        self.cursor_x -= 1
                        self.screen_buffer[self.cursor_y][self.cursor_x] = ' '
                    elif self.cursor_y > 0:
                        self.cursor_y -= 1
                        self.cursor_x = self.cols - 1
                        self.screen_buffer[self.cursor_y][self.cursor_x] = ' '
                    self.redraw()
                return "break"

            elif char and char.isprintable():
                self.input_buffer += char
                self.write_text(char)
                return "break"

            return "break"
        else:
            # Handle normal text input
            if event.keysym == "Return":
                self.write_text("\n")
            elif event.keysym == "BackSpace":
                if self.cursor_x > 0:
                    self.cursor_x -= 1
                    self.screen_buffer[self.cursor_y][self.cursor_x] = " "
                elif self.cursor_y > 0:
                    self.cursor_y -= 1
                    self.cursor_x = self.cols - 1
                    self.screen_buffer[self.cursor_y][self.cursor_x] = " "
                self.redraw()
            elif event.char.isprintable():
                self.write_text(event.char)

    def prompt_input(self, prompt_text, callback):
        """Display input prompt and wait for user input"""
        self.input_prompt = prompt_text if prompt_text else ""
        self.input_callback = callback
        self.input_buffer = ""
        self.input_active = True

        # Display prompt
        if self.input_prompt:
            self.write_text(f"{self.input_prompt} ")

        # Ensure cursor is below the prompt
        self.cursor_x = 0
        self.cursor_y += 1
        if self.cursor_y >= self.rows:
            self.scroll_up()
            self.cursor_y = self.rows - 1

        # Focus the canvas for input
        self.focus_set()

    # Alias for compatibility
    _clear_screen = clear_screen
