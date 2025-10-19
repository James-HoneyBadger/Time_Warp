"""
Unified Canvas System for Time_Warp IDE

Implements GW BASIC screen modes with unified text and graphics rendering.
Supports keyboard input prompts and multiple display modes.
"""

import tkinter as tk
from tkinter import font
import math


class UnifiedCanvas(tk.Canvas):
    """
    Unified canvas that handles both text and graphics rendering
    with support for GW BASIC screen modes and keyboard input.
    """

    # GW BASIC Color Palettes
    CGA_PALETTE_0 = [
        "#000000", "#0000AA", "#00AA00", "#00AAAA",  # Black, Blue, Green, Cyan
        "#AA0000", "#AA00AA", "#AA5500", "#AAAAAA",  # Red, Magenta, Brown, Light Gray
        "#555555", "#5555FF", "#55FF55", "#55FFFF",  # Dark Gray, Light Blue, Light Green, Light Cyan
        "#FF5555", "#FF55FF", "#FFFF55", "#FFFFFF"   # Light Red, Light Magenta, Yellow, White
    ]

    CGA_PALETTE_1 = [
        "#000000", "#0000AA", "#00AA00", "#00AAAA",  # Black, Blue, Green, Cyan
        "#AA0000", "#AA00AA", "#AAAA00", "#AAAAAA",  # Red, Magenta, Yellow, Light Gray
        "#555555", "#5555FF", "#55FF55", "#55FFFF",  # Dark Gray, Light Blue, Light Green, Light Cyan
        "#FF5555", "#FF55FF", "#FFFF55", "#FFFFFF"   # Light Red, Light Magenta, Yellow, White
    ]

    EGA_PALETTE = [
        # Standard 16 EGA colors (0-15)
        "#000000", "#0000AA", "#00AA00", "#00AAAA",  # 0-3: Black, Blue, Green, Cyan
        "#AA0000", "#AA00AA", "#AA5500", "#AAAAAA",  # 4-7: Red, Magenta, Brown, Light Gray
        "#555555", "#5555FF", "#55FF55", "#55FFFF",  # 8-11: Dark Gray, Light Blue, Light Green, Light Cyan
        "#FF5555", "#FF55FF", "#FFFF55", "#FFFFFF",  # 12-15: Light Red, Light Magenta, Yellow, White
        # Extended EGA colors (16-63) - grayscale and additional colors
        "#000000", "#101010", "#202020", "#303030",  # 16-19: Very dark grays
        "#404040", "#505050", "#606060", "#707070",  # 20-23: Dark grays
        "#808080", "#909090", "#A0A0A0", "#B0B0B0",  # 24-27: Medium grays
        "#C0C0C0", "#D0D0D0", "#E0E0E0", "#F0F0F0",  # 28-31: Light grays
        # Additional colors for full 64-color palette
        "#000080", "#008000", "#008080", "#800000",  # 32-35: Dark variations
        "#800080", "#808000", "#C0C0C0", "#808080",  # 36-39: More colors
        "#0000FF", "#00FF00", "#00FFFF", "#FF0000",  # 40-43: Bright colors
        "#FF00FF", "#FFFF00", "#FFFFFF", "#000000",  # 44-47: More bright colors
        "#000040", "#004000", "#004040", "#400000",  # 48-51: Very dark colors
        "#400040", "#404000", "#606060", "#404040",  # 52-55: Dark variations
        "#0000C0", "#00C000", "#00C0C0", "#C00000",  # 56-59: Medium bright
        "#C000C0", "#C0C000", "#E0E0E0", "#A0A0A0"   # 60-63: Light variations
    ]

    # Screen mode configurations - Authentic GW-BASIC specifications
    SCREEN_MODES = {
        0: {
            "name": "Text Mode (40/80 columns)",
            "width": 640, "height": 200,  # Default to 80-column size
            "text_cols": 80, "text_rows": 25,
            "char_width": 8, "char_height": 8,  # 8x8 character box (8x14 with EGA)
            "colors": 16, "palette": CGA_PALETTE_0,
            "type": "text",
            "attribute_range": "0-15",  # 16 colors for 2 attributes (foreground/background)
            "memory_pages": 1,
            "page_size": "2K-4K"  # 2K for 40-col, 4K for 80-col
        },
        1: {
            "name": "320x200 Graphics (4 colors)",
            "width": 320, "height": 200,
            "colors": 4, "palette": CGA_PALETTE_0[:4],  # Only first 4 colors
            "type": "graphics",
            "attribute_range": "0-3",
            "bits_per_pixel": 2,
            "memory_pages": 1,
            "page_size": "16K"
        },
        2: {
            "name": "640x200 Graphics (2 colors)",
            "width": 640, "height": 200,
            "colors": 2, "palette": CGA_PALETTE_0[:2],  # Black and white
            "type": "graphics",
            "attribute_range": "0-1",
            "bits_per_pixel": 1,
            "memory_pages": 1,
            "page_size": "16K"
        },
        7: {
            "name": "EGA 320x200 Graphics (16 colors)",
            "width": 320, "height": 200,
            "colors": 16, "palette": EGA_PALETTE[:16],
            "type": "graphics",
            "attribute_range": "0-15",
            "bits_per_pixel": 4,
            "memory_pages": "2-4",  # Depends on EGA memory (64K=2, 128K=3, 256K=4)
            "page_size": "32K",
            "ega_required": True
        },
        8: {
            "name": "EGA 640x200 Graphics (16 colors)",
            "width": 640, "height": 200,
            "colors": 16, "palette": EGA_PALETTE[:16],
            "type": "graphics",
            "attribute_range": "0-15",
            "bits_per_pixel": 4,
            "memory_pages": "1-4",  # Depends on EGA memory (64K=1, 128K=2, 256K=4)
            "page_size": "64K",
            "ega_required": True
        },
        9: {
            "name": "EGA 640x350 Graphics (16/64 colors)",
            "width": 640, "height": 350,
            "colors": 64, "palette": EGA_PALETTE,  # Full 64-color palette
            "type": "graphics",
            "attribute_range": "0-15 (64K) / 0-63 (128K+)",
            "bits_per_pixel": "2-4",  # 2 bits (64K) or 4 bits (128K+)
            "memory_pages": "1-2",  # 2 pages with 256K
            "page_size": "128K",
            "ega_required": True
        },
        10: {
            "name": "EGA Monochrome 640x350 Graphics (9 pseudo-colors)",
            "width": 720, "height": 350,  # Note: 720 width for MDA
            "colors": 9, "palette": [
                "#000000", "#FFFFFF", "#000000", "#FFFFFF",  # Off, On, Blink off-to-on
                "#000000", "#FFFFFF", "#000000", "#FFFFFF",  # Blink off-to-high, On
                "#FFFFFF"  # High intensity
            ],
            "type": "graphics",
            "attribute_range": "0-3",
            "bits_per_pixel": 2,
            "memory_pages": "1-2",  # 2 pages with 256K
            "page_size": "128K",
            "ega_required": True,
            "monochrome": True
        },
        11: {
            "name": "XGA Turtle Graphics (1024x768, 256 colors)",
            "width": 1024, "height": 768,
            "colors": 256, "palette": [
                # Standard 16 EGA colors (0-15)
                "#000000", "#0000AA", "#00AA00", "#00AAAA", "#AA0000", "#AA00AA", "#AA5500", "#AAAAAA",
                "#555555", "#5555FF", "#55FF55", "#55FFFF", "#FF5555", "#FF55FF", "#FFFF55", "#FFFFFF",
                # Extended colors (16-255) - full RGB spectrum
                *[f"#{r:02X}{g:02X}{b:02X}" for r in range(0, 256, 16)
                  for g in range(0, 256, 16) for b in range(0, 256, 16)][16:256]
            ],
            "type": "turtle",
            "attribute_range": "0-255",
            "bits_per_pixel": 8,
            "memory_pages": 1,
            "page_size": "768K",  # 1024x768x1 bytes
            "turtle_optimized": True,
            "high_resolution": True
        }
    }

    def __init__(self, parent, mode=2, text_cols=None, **kwargs):
        # Extract font parameters before passing to Canvas
        self.font_family = kwargs.pop('font_family', 'Courier')
        self.font_size = kwargs.pop('font_size', 12)

        # Extract mode and text_cols parameters before passing to Canvas
        self.current_mode = mode
        self.text_cols_override = text_cols
        super().__init__(parent, **kwargs)
        self.mode_config = self.SCREEN_MODES[self.current_mode].copy()

        # Initialize mode config first
        self.mode_config = self.SCREEN_MODES[self.current_mode].copy()
        if self.current_mode == 0 and self.text_cols_override:
            self.mode_config["text_cols"] = self.text_cols_override
            self.mode_config["width"] = self.text_cols_override * 8

        # Text rendering state - fixed grid based on screen mode
        self.rows = self.mode_config.get("text_rows", 25)
        self.cols = self.mode_config.get("text_cols", 80)
        self.screen_buffer = [[' ' for _ in range(self.cols)] for _ in range(self.rows)]
        self.screen_colors = [[15 for _ in range(self.cols)] for _ in range(self.rows)]  # Default white
        self.cursor_x = 0
        self.cursor_y = 0
        self.text_color = 15  # White (bright)
        self.bg_color = 0    # Black
        self.text_items = []  # Canvas text item IDs

        # Graphics rendering state
        self.graphics_items = []
        self.pen_color = 15  # White
        self.fill_color = 0  # Black
        self.pen_down = True

        # Input handling
        self.input_prompt = ""
        self.input_callback = None
        self.input_buffer = ""
        self.input_active = False
        self.input_line_items = []  # Track items for current input line
        self.cursor_visible = False
        self.cursor_item = None
        self.cursor_blink_job = None

        # Font setup
        self.set_font(self.font_family, self.font_size)

        # Bind events
        self.bind("<Key>", self._on_key_press)
        self.bind("<Button-1>", self._on_mouse_click)
        self.bind("<Configure>", self._on_resize)  # Handle window resize
        self.focus_set()

        # Initialize canvas
        self._update_canvas_size()
        self._clear_screen()

    def _setup_font(self):
        """Setup font for text rendering"""
        import tkinter.font as tkfont
        self.font = tkfont.Font(family=self.font_family, size=self.font_size, weight="normal")

    def set_font(self, family="Courier", size=12):
        """Set the font for text rendering"""
        self.font_family = family
        self.font_size = size
        self._setup_font()
        # Redraw the screen with new font
        self._redraw_screen()

    def _update_canvas_size(self):
        """Update canvas size based on current screen mode"""
        # Calculate canvas size based on character grid and font metrics
        char_width = self.font.measure("W")
        char_height = self.font.metrics("linespace")

        canvas_width = self.cols * char_width
        canvas_height = self.rows * char_height

        self.config(width=canvas_width, height=canvas_height)

    def set_screen_mode(self, mode, text_cols=None):
        """Set the screen mode

        Args:
            mode: Screen mode number (0-11)
            text_cols: For mode 0, specify 40 or 80 columns (default: 80)
        """
        if mode not in self.SCREEN_MODES:
            raise ValueError(f"Invalid screen mode: {mode}")

        self.current_mode = mode
        self.mode_config = self.SCREEN_MODES[mode].copy()

        # Handle mode 0 text column selection (40 or 80 columns)
        if mode == 0:
            if text_cols in [40, 80]:
                self.mode_config["text_cols"] = text_cols
                # Adjust width based on columns
                self.mode_config["width"] = text_cols * 8  # 8 pixels per character
            elif text_cols is not None:
                raise ValueError("Mode 0 supports only 40 or 80 columns")

        # Update grid dimensions
        self.rows = self.mode_config.get("text_rows", 25)
        self.cols = self.mode_config.get("text_cols", 80)

        # Recreate screen buffers with new dimensions
        default_color = min(15, len(self.mode_config["palette"]) - 1)
        self.screen_buffer = [[' ' for _ in range(self.cols)] for _ in range(self.rows)]
        self.screen_colors = [[default_color for _ in range(self.cols)] for _ in range(self.rows)]

        # Update canvas size for new mode
        self._update_canvas_size()

        # Clear everything and redraw
        self._clear_screen()

        # Reset cursor position
        self.cursor_x = 0
        self.cursor_y = 0

        # Set default colors based on mode type
        if self.mode_config["type"] == "text":
            self.text_color = 7  # Light gray for text modes
            self.bg_color = 0   # Black background
        else:
            self.text_color = 15  # White for graphics modes
            self.bg_color = 0    # Black background

        self.pen_color = 15   # White pen
        self.fill_color = 0   # Black fill

    def _clear_screen(self):
        """Clear the entire screen"""
        self.delete("all")
        self.text_items = []
        self.graphics_items = []

        # Reset screen buffers
        default_color = min(15, len(self.mode_config["palette"]) - 1)
        self.screen_buffer = [[' ' for _ in range(self.cols)] for _ in range(self.rows)]
        self.screen_colors = [[default_color for _ in range(self.cols)] for _ in range(self.rows)]

        # Fill background
        canvas_width = self.winfo_width() or (self.cols * self.font.measure("W"))
        canvas_height = self.winfo_height() or (self.rows * self.font.metrics("linespace"))

        bg_color = self.mode_config["palette"][self.bg_color]
        self.create_rectangle(0, 0, canvas_width, canvas_height,
                            fill=bg_color, outline=bg_color, tags="background")

        # If input was active, recreate the cursor
        if hasattr(self, 'input_active') and self.input_active:
            self.cursor_item = None  # Reset cursor item so it gets recreated
            self._update_cursor_position()

    def _get_char_size(self):
        """Get character width and height"""
        width = self.font.measure("W")  # Use 'W' as widest character
        height = self.font.metrics("linespace")
        return width, height

    def write_text(self, text, x=None, y=None, color=None):
        """Write text at specified position or current cursor"""
        if x is None:
            x = self.cursor_x
        if y is None:
            y = self.cursor_y
        if color is None:
            color = self.text_color

        # Ensure color is within valid range for current mode
        max_color = len(self.mode_config["palette"]) - 1
        if color > max_color:
            color = max_color  # Use highest available color

        if self.mode_config["type"] == "text":
            self._write_text_mode(text, x, y, color)
        else:
            self._write_graphics_mode(text, x, y, color)

    def _write_text_mode(self, text, x, y, color):
        """Write text in text mode to the fixed grid"""
        # Handle newlines
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if i > 0:
                # Move to next line
                y += 1
                x = 0

                # If we've reached the bottom row, scroll up
                if y >= self.rows:
                    self.scroll_up()
                    y = self.rows - 1

            # Write each character to the screen buffer
            for char in line:
                if x < self.cols:
                    self.screen_buffer[y][x] = char
                    self.screen_colors[y][x] = color
                    x += 1
                else:
                    # Line wrap
                    y += 1
                    x = 0
                    if y >= self.rows:
                        self.scroll_up()
                        y = self.rows - 1
                    if x < self.cols:
                        self.screen_buffer[y][x] = char
                        self.screen_colors[y][x] = color
                        x += 1

        # Update cursor position
        self.cursor_x = x
        self.cursor_y = y

        # Redraw the screen
        self._redraw_screen()

    def _write_graphics_mode(self, text, x, y, color):
        """Write text in graphics mode"""
        text_color = self.mode_config["palette"][color]
        item_id = self.create_text(x, y,
                                 text=text,
                                 font=self.font,
                                 fill=text_color,
                                 anchor="nw",
                                 tags="graphics_text")
        self.graphics_items.append(item_id)

    def _redraw_screen(self):
        """Redraw the entire screen from the buffer"""
        # Clear all text items
        for item_id in self.text_items:
            self.delete(item_id)
        self.text_items = []

        char_width, char_height = self._get_char_size()

        # Draw each character from the buffer
        for row in range(self.rows):
            for col in range(self.cols):
                char = self.screen_buffer[row][col]
                color = self.screen_colors[row][col]

                # Ensure color is within valid range for current mode
                max_color = len(self.mode_config["palette"]) - 1
                if color > max_color:
                    color = max_color

                if char != ' ':  # Only draw non-space characters for efficiency
                    x = col * char_width
                    y = row * char_height

                    text_color = self.mode_config["palette"][color]
                    item_id = self.create_text(x, y,
                                             text=char,
                                             font=self.font,
                                             fill=text_color,
                                             anchor="nw",
                                             tags="text")
                    self.text_items.append(item_id)

    def scroll_up(self):
        """Scroll the screen up by one line (traditional terminal scroll)"""
        # Move all lines up
        for row in range(self.rows - 1):
            self.screen_buffer[row] = self.screen_buffer[row + 1][:]
            self.screen_colors[row] = self.screen_colors[row + 1][:]

        # Clear the bottom line
        default_color = min(15, len(self.mode_config["palette"]) - 1)
        self.screen_buffer[self.rows - 1] = [' ' for _ in range(self.cols)]
        self.screen_colors[self.rows - 1] = [default_color for _ in range(self.cols)]

        # Redraw the screen
        self._redraw_screen()

    def set_cursor(self, x, y):
        """Set cursor position"""
        self.cursor_x = x
        self.cursor_y = y

    def set_text_color(self, color):
        """Set text color"""
        max_color = len(self.mode_config["palette"]) - 1
        if 0 <= color <= max_color:
            self.text_color = color
        else:
            self.text_color = max_color  # Use highest available color

    def set_bg_color(self, color):
        """Set background color"""
        if 0 <= color < len(self.mode_config["palette"]):
            self.bg_color = color
            # Update background
            bg_color = self.mode_config["palette"][color]
            self.itemconfig("background", fill=bg_color, outline=bg_color)

    def clear_text(self):
        """Clear all text and reset cursor"""
        default_color = min(15, len(self.mode_config["palette"]) - 1)
        self.screen_buffer = [[' ' for _ in range(self.cols)] for _ in range(self.rows)]
        self.screen_colors = [[default_color for _ in range(self.cols)] for _ in range(self.rows)]
        self.cursor_x = 0
        self.cursor_y = 0
        self._redraw_screen()

    def clear_graphics(self):
        """Clear all graphics items"""
        for item_id in self.graphics_items:
            self.delete(item_id)
        self.graphics_items = []

    # Graphics functions
    def draw_pixel(self, x, y, color=None):
        """Draw a single pixel"""
        if color is None:
            color = self.pen_color
        pixel_color = self.mode_config["palette"][color]
        item_id = self.create_rectangle(x, y, x+1, y+1,
                                      fill=pixel_color,
                                      outline=pixel_color,
                                      tags="pixel")
        self.graphics_items.append(item_id)

    def draw_line(self, x1, y1, x2, y2, color=None):
        """Draw a line"""
        if color is None:
            color = self.pen_color
        line_color = self.mode_config["palette"][color]
        item_id = self.create_line(x1, y1, x2, y2,
                                 fill=line_color,
                                 width=1,
                                 tags="line")
        self.graphics_items.append(item_id)

    def draw_rectangle(self, x1, y1, x2, y2, color=None, filled=False):
        """Draw a rectangle"""
        if color is None:
            color = self.pen_color
        rect_color = self.mode_config["palette"][color]

        if filled:
            fill_color = rect_color
            outline_color = rect_color
        else:
            fill_color = ""
            outline_color = rect_color

        item_id = self.create_rectangle(x1, y1, x2, y2,
                                      fill=fill_color,
                                      outline=outline_color,
                                      tags="rectangle")
        self.graphics_items.append(item_id)

    def draw_circle(self, x, y, radius, color=None, filled=False):
        """Draw a circle"""
        if color is None:
            color = self.pen_color
        circle_color = self.mode_config["palette"][color]

        x1 = x - radius
        y1 = y - radius
        x2 = x + radius
        y2 = y + radius

        if filled:
            fill_color = circle_color
            outline_color = circle_color
        else:
            fill_color = ""
            outline_color = circle_color

        item_id = self.create_oval(x1, y1, x2, y2,
                                 fill=fill_color,
                                 outline=outline_color,
                                 tags="circle")
        self.graphics_items.append(item_id)

    # Input handling
    def prompt_input(self, prompt_text, callback):
        """Display input prompt and wait for user input"""
        self.input_prompt = prompt_text if prompt_text else ""
        self.input_callback = callback
        self.input_buffer = ""
        self.input_active = True

        # Display prompt
        if self.input_prompt:
            # Use highest available color for prompt text
            prompt_color = min(15, len(self.mode_config["palette"]) - 1)
            self.write_text(f"{self.input_prompt} ", color=prompt_color)

        # Start cursor blinking
        self._start_cursor_blink()

    def _on_key_press(self, event):
        """Handle key press events"""
        if not self.input_active:
            return

        key = event.keysym
        char = event.char

        if key == "Return":
            # Stop cursor blinking
            self._stop_cursor_blink()
            # Hide cursor
            self._hide_cursor()

            # If we're on the last row, scroll up before submitting
            if self.cursor_y >= self.rows - 1:
                self.scroll_up()
                self.cursor_y = self.rows - 1  # Move cursor to the new bottom line

            # Submit input
            if self.input_callback:
                self.input_callback(self.input_buffer)
            self.input_active = False

            # Move to next line after input
            self.cursor_x = 0
            self.cursor_y += 1
            if self.cursor_y >= self.rows:
                self.scroll_up()
                self.cursor_y = self.rows - 1

            return "break"

        elif key == "BackSpace":
            if self.input_buffer:
                self.input_buffer = self.input_buffer[:-1]
                # Move cursor back
                if self.cursor_x > 0:
                    self.cursor_x -= 1
                    # Clear the character from screen buffer
                    self.screen_buffer[self.cursor_y][self.cursor_x] = ' '
                    self._redraw_screen()
                # Update cursor position
                self._update_cursor_position()
            return "break"

        elif char and char.isprintable():
            self.input_buffer += char
            # Write character to screen buffer
            if self.cursor_x < self.cols:
                self.screen_buffer[self.cursor_y][self.cursor_x] = char
                # Use highest available color for input text
                input_color = min(15, len(self.mode_config["palette"]) - 1)
                self.screen_colors[self.cursor_y][self.cursor_x] = input_color
                self.cursor_x += 1
                self._redraw_screen()
            # Update cursor position
            self._update_cursor_position()
            return "break"

        # For any other keys, prevent default handling
        return "break"

    def _redisplay_input(self):
        """Redisplay the input prompt and current buffer"""
        # Only update cursor position - the text is already displayed correctly
        # by the individual character additions in _write_text_mode
        self._update_cursor_position()

    def _clear_current_input_line(self):
        """Clear the current input line"""
        # Delete all items from the current input line
        for item_id in self.input_line_items:
            try:
                self.delete(item_id)
                if item_id in self.text_items:
                    self.text_items.remove(item_id)
            except tk.TclError:
                pass  # Item might already be deleted
        self.input_line_items = []

        # Also hide cursor if visible
        self._hide_cursor()

        # Reset cursor to input start position
        self.cursor_x = self.input_start_x
        self.cursor_y = self.input_start_y

    def _on_resize(self, event):
        """Handle canvas resize events"""
        # Update canvas size based on new dimensions
        self._update_canvas_size()
        # Redraw everything
        self._redraw_screen()

    # Turtle graphics compatibility
    def turtle_forward(self, distance):
        """Move turtle forward (for compatibility)"""
        # This would need turtle state tracking
        pass

    def turtle_turn(self, angle):
        """Turn turtle (for compatibility)"""
        # This would need turtle state tracking
        pass

    def _start_cursor_blink(self):
        """Start the cursor blinking"""
        self.cursor_visible = True
        self._update_cursor_position()
        self._blink_cursor()

    def _stop_cursor_blink(self):
        """Stop the cursor blinking"""
        if self.cursor_blink_job:
            self.after_cancel(self.cursor_blink_job)
            self.cursor_blink_job = None

    def _blink_cursor(self):
        """Toggle cursor visibility for blinking effect"""
        if not self.input_active:
            return

        if self.cursor_visible:
            self._show_cursor()
        else:
            self._hide_cursor()

        self.cursor_visible = not self.cursor_visible
        self.cursor_blink_job = self.after(500, self._blink_cursor)  # Blink every 500ms

    def _update_cursor_position(self):
        """Update the cursor position"""
        if not self.input_active:
            return

        char_width, char_height = self._get_char_size()

        # Convert cursor position to pixel coordinates
        pixel_x = self.cursor_x * char_width
        pixel_y = self.cursor_y * char_height

        # Store cursor position for blinking
        self.cursor_pos = (pixel_x, pixel_y)

        # If cursor is currently visible, reposition it
        if self.cursor_item and self.cursor_visible:
            self.coords(self.cursor_item, pixel_x, pixel_y + char_height - 2, pixel_x + char_width, pixel_y + char_height)

    def _show_cursor(self):
        """Show the cursor (underscore)"""
        if not self.input_active or not hasattr(self, 'cursor_pos'):
            return

        pixel_x, pixel_y = self.cursor_pos
        char_width, char_height = self._get_char_size()

        # Use the highest available color for the cursor
        cursor_color_index = min(15, len(self.mode_config["palette"]) - 1)
        cursor_color = self.mode_config["palette"][cursor_color_index]

        if self.cursor_item:
            self.coords(self.cursor_item, pixel_x, pixel_y + char_height - 2, pixel_x + char_width, pixel_y + char_height)
            self.itemconfig(self.cursor_item, state="normal")
        else:
            # Create cursor as a thin line at the bottom of the character cell
            self.cursor_item = self.create_rectangle(
                pixel_x, pixel_y + char_height - 2, pixel_x + char_width, pixel_y + char_height,
                fill=cursor_color,
                outline=cursor_color,
                tags="cursor"
            )

    def _hide_cursor(self):
        """Hide the cursor"""
        if self.cursor_item:
            self.itemconfig(self.cursor_item, state="hidden")

    def _on_mouse_click(self, event):
        """Handle mouse click events"""
        # Set focus to canvas for keyboard input
        self.focus_set()

    # Utility methods
    def get_mode_info(self):
        """Get current mode information"""
        return self.mode_config.copy()

        """Get current color palette"""
    def get_palette(self):
        """Get current color palette"""
        return self.mode_config["palette"].copy()
