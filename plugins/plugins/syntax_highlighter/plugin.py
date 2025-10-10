"""
Enhanced Syntax Highlighter Plugin for Time_Warp IDE
Provides advanced syntax highlighting with customizable colors
"""

import tkinter as tk
from tkinter import messagebox, colorchooser
import sys
import os

# Add the parent directory to path to import the base plugin class
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from plugins import TimeWarpPlugin as BaseTimeWarpPlugin
except ImportError:
    # Fallback base class
    class BaseTimeWarpPlugin:
        def __init__(self, ide_instance):
            self.ide = ide_instance
            self.name = "Base Plugin"
            self.version = "1.0.0"
            self.author = "Unknown"
            self.description = "Base plugin class"

        def activate(self):
            pass

        def deactivate(self):
            pass

        def get_info(self):
            return {
                "name": self.name,
                "version": self.version,
                "author": self.author,
                "description": self.description,
            }


class TimeWarpPlugin(BaseTimeWarpPlugin):
    """Enhanced syntax highlighter plugin implementation"""

    def __init__(self, ide_instance):
        super().__init__(ide_instance)
        self.name = "Syntax Highlighter"
        self.version = "1.1.0"
        self.author = "Time_Warp Development Team"
        self.description = "Enhanced syntax highlighting for PILOT, BASIC, Logo, and other supported languages"
        self.menu_items = []

        # Syntax highlighting colors
        self.highlight_colors = {
            "pilot_commands": "#FF6B35",  # Orange for PILOT commands
            "basic_keywords": "#4A90E2",  # Blue for BASIC keywords
            "logo_commands": "#7ED321",  # Green for Logo commands
            "strings": "#D0021B",  # Red for strings
            "comments": "#9B9B9B",  # Gray for comments
            "numbers": "#9013FE",  # Purple for numbers
            "variables": "#F5A623",  # Yellow for variables
        }

    def activate(self):
        """Activate the plugin - add menu items and functionality"""
        try:
            self.add_menu_items()
            self.enable_syntax_highlighting()
            if hasattr(self.ide, "status_label"):
                self.ide.status_label.config(
                    text="Syntax Highlighter plugin activated!"
                )
            print(f"✅ {self.name} activated successfully")
        except Exception as e:
            print(f"❌ Error activating {self.name}: {e}")

    def deactivate(self):
        """Deactivate the plugin - remove menu items"""
        try:
            self.remove_menu_items()
            self.disable_syntax_highlighting()
            if hasattr(self.ide, "status_label"):
                self.ide.status_label.config(
                    text="Syntax Highlighter plugin deactivated"
                )
            print(f"🔌 {self.name} deactivated")
        except Exception as e:
            print(f"❌ Error deactivating {self.name}: {e}")

    def add_menu_items(self):
        """Add plugin-specific menu items"""
        try:
            # Add to View menu if it exists
            if hasattr(self.ide, "menubar"):
                # Find the View menu
                view_menu = None
                for i in range(self.ide.menubar.index("end") + 1):
                    try:
                        if self.ide.menubar.entryconfig(i, "label")[4][1] == "View":
                            view_menu = self.ide.menubar.nametowidget(
                                self.ide.menubar.entryconfig(i, "menu")[4][1]
                            )
                            break
                    except Exception:
                        continue

                if view_menu:
                    # Add separator
                    view_menu.add_separator()

                    # Add highlighting options
                    view_menu.add_command(
                        label="🎨 Toggle Syntax Highlighting",
                        command=self.toggle_highlighting,
                    )
                    view_menu.add_command(
                        label="🌈 Customize Colors", command=self.customize_colors
                    )
                    view_menu.add_command(
                        label="🔄 Refresh Highlighting",
                        command=self.refresh_highlighting,
                    )

                    self.menu_items = [
                        "🎨 Toggle Syntax Highlighting",
                        "🌈 Customize Colors",
                        "🔄 Refresh Highlighting",
                    ]

        except Exception as e:
            print(f"Error adding menu items: {e}")

    def remove_menu_items(self):
        """Remove plugin menu items"""
        try:
            self.menu_items = []
        except Exception as e:
            print(f"Error removing menu items: {e}")

    def enable_syntax_highlighting(self):
        """Enable syntax highlighting in the editor"""
        try:
            if hasattr(self.ide, "editor"):
                # Configure text tags for syntax highlighting
                self.configure_syntax_tags()

                # Bind events for real-time highlighting
                self.ide.editor.bind("<KeyRelease>", self.on_text_change)
                self.ide.editor.bind("<Button-1>", self.on_text_change)

                # Initial highlighting
                self.highlight_syntax()

        except Exception as e:
            print(f"Error enabling syntax highlighting: {e}")

    def disable_syntax_highlighting(self):
        """Disable syntax highlighting"""
        try:
            if hasattr(self.ide, "editor"):
                # Remove all syntax tags
                for tag in [
                    "pilot_cmd",
                    "basic_kw",
                    "logo_cmd",
                    "string",
                    "comment",
                    "number",
                    "variable",
                ]:
                    self.ide.editor.tag_delete(tag)

                # Unbind events
                self.ide.editor.unbind("<KeyRelease>")
                self.ide.editor.unbind("<Button-1>")

        except Exception as e:
            print(f"Error disabling syntax highlighting: {e}")

    def configure_syntax_tags(self):
        """Configure text tags for syntax highlighting"""
        if not hasattr(self.ide, "editor"):
            return

        try:
            # Configure tags with colors
            self.ide.editor.tag_config(
                "pilot_cmd",
                foreground=self.highlight_colors["pilot_commands"],
                font=("Consolas", 10, "bold"),
            )
            self.ide.editor.tag_config(
                "basic_kw",
                foreground=self.highlight_colors["basic_keywords"],
                font=("Consolas", 10, "bold"),
            )
            self.ide.editor.tag_config(
                "logo_cmd",
                foreground=self.highlight_colors["logo_commands"],
                font=("Consolas", 10, "bold"),
            )
            self.ide.editor.tag_config(
                "string", foreground=self.highlight_colors["strings"]
            )
            self.ide.editor.tag_config(
                "comment",
                foreground=self.highlight_colors["comments"],
                font=("Consolas", 10, "italic"),
            )
            self.ide.editor.tag_config(
                "number", foreground=self.highlight_colors["numbers"]
            )
            self.ide.editor.tag_config(
                "variable", foreground=self.highlight_colors["variables"]
            )

        except Exception as e:
            print(f"Error configuring syntax tags: {e}")

    def highlight_syntax(self):
        """Apply syntax highlighting to the current editor content"""
        if not hasattr(self.ide, "editor"):
            return

        try:
            content = self.ide.editor.get("1.0", tk.END)

            # Clear existing tags
            for tag in [
                "pilot_cmd",
                "basic_kw",
                "logo_cmd",
                "string",
                "comment",
                "number",
                "variable",
            ]:
                self.ide.editor.tag_remove(tag, "1.0", tk.END)

            lines = content.split("\n")

            for line_num, line in enumerate(lines, 1):
                line_start = f"{line_num}.0"

                # Highlight PILOT commands
                if line.strip().startswith(
                    ("T:", "A:", "Y:", "N:", "J:", "M:", "C:", "U:", "E:")
                ):
                    cmd_end = f"{line_num}.2"
                    self.ide.editor.tag_add("pilot_cmd", line_start, cmd_end)

                # Highlight BASIC keywords
                basic_keywords = [
                    "PRINT",
                    "INPUT",
                    "LET",
                    "GOTO",
                    "GOSUB",
                    "IF",
                    "THEN",
                    "ELSE",
                    "FOR",
                    "NEXT",
                    "REM",
                    "DIM",
                    "END",
                ]
                words = line.split()
                col = 0
                for word in words:
                    if word.upper() in basic_keywords:
                        word_start = f"{line_num}.{col}"
                        word_end = f"{line_num}.{col + len(word)}"
                        self.ide.editor.tag_add("basic_kw", word_start, word_end)
                    col += len(word) + 1

                # Highlight Logo commands
                logo_commands = [
                    "FD",
                    "FORWARD",
                    "BK",
                    "BACK",
                    "LT",
                    "LEFT",
                    "RT",
                    "RIGHT",
                    "PU",
                    "PD",
                    "REPEAT",
                    "TO",
                    "END",
                ]
                col = 0
                for word in words:
                    if word.upper() in logo_commands:
                        word_start = f"{line_num}.{col}"
                        word_end = f"{line_num}.{col + len(word)}"
                        self.ide.editor.tag_add("logo_cmd", word_start, word_end)
                    col += len(word) + 1

                # Highlight strings (simple quotes)
                in_string = False
                string_start = 0
                for i, char in enumerate(line):
                    if char in ['"', "'"]:
                        if not in_string:
                            in_string = True
                            string_start = i
                        else:
                            in_string = False
                            str_start = f"{line_num}.{string_start}"
                            str_end = f"{line_num}.{i + 1}"
                            self.ide.editor.tag_add("string", str_start, str_end)

                # Highlight comments (REM or lines starting with #, //)
                if line.strip().startswith(("REM", "#", "//")):
                    line_end = f"{line_num}.{len(line)}"
                    self.ide.editor.tag_add("comment", line_start, line_end)

                # Highlight numbers
                import re

                for match in re.finditer(r"\b\d+\.?\d*\b", line):
                    num_start = f"{line_num}.{match.start()}"
                    num_end = f"{line_num}.{match.end()}"
                    self.ide.editor.tag_add("number", num_start, num_end)

        except Exception as e:
            print(f"Error highlighting syntax: {e}")

    def on_text_change(self, event=None):
        """Handle text change events for real-time highlighting"""
        # Delay highlighting to avoid performance issues
        if hasattr(self.ide, "editor"):
            self.ide.editor.after(100, self.highlight_syntax)

    def toggle_highlighting(self):
        """Toggle syntax highlighting on/off"""
        try:
            # Simple toggle - in a full implementation, we'd track state
            if hasattr(self.ide, "editor"):
                # Check if highlighting is currently active
                tags = self.ide.editor.tag_names()
                if "pilot_cmd" in tags:
                    self.disable_syntax_highlighting()
                    messagebox.showinfo(
                        "Syntax Highlighting", "Syntax highlighting disabled"
                    )
                else:
                    self.enable_syntax_highlighting()
                    messagebox.showinfo(
                        "Syntax Highlighting", "Syntax highlighting enabled"
                    )

        except Exception as e:
            messagebox.showerror("Error", f"Could not toggle syntax highlighting: {e}")

    def customize_colors(self):
        """Open color customization dialog"""
        try:
            dialog = tk.Toplevel(self.ide.root)
            dialog.title("🌈 Customize Syntax Colors")
            dialog.geometry("400x500")
            dialog.transient(self.ide.root)
            dialog.grab_set()

            ttk_available = True
            try:
                from tkinter import ttk
            except ImportError:
                ttk_available = False

            # Color selection for each category
            row = 0
            color_vars = {}

            for category, current_color in self.highlight_colors.items():
                if ttk_available:
                    ttk.Label(
                        dialog, text=category.replace("_", " ").title() + ":"
                    ).grid(row=row, column=0, sticky="w", padx=10, pady=5)
                else:
                    tk.Label(
                        dialog, text=category.replace("_", " ").title() + ":"
                    ).grid(row=row, column=0, sticky="w", padx=10, pady=5)

                color_vars[category] = tk.StringVar(value=current_color)
                color_button = tk.Button(
                    dialog,
                    text="Choose Color",
                    bg=current_color,
                    command=lambda cat=category: self.choose_color(
                        color_vars[cat], dialog
                    ),
                )
                color_button.grid(row=row, column=1, padx=10, pady=5)

                row += 1

            # Buttons
            button_frame = tk.Frame(dialog)
            button_frame.grid(row=row, column=0, columnspan=2, pady=20)

            def apply_colors():
                for category, var in color_vars.items():
                    self.highlight_colors[category] = var.get()
                self.configure_syntax_tags()
                self.highlight_syntax()
                messagebox.showinfo(
                    "Colors Applied", "Syntax highlighting colors updated!"
                )
                dialog.destroy()

            tk.Button(button_frame, text="✅ Apply", command=apply_colors).pack(
                side=tk.LEFT, padx=5
            )
            tk.Button(button_frame, text="❌ Cancel", command=dialog.destroy).pack(
                side=tk.LEFT, padx=5
            )

        except Exception as e:
            messagebox.showerror("Error", f"Could not open color customization: {e}")

    def choose_color(self, color_var, parent):
        """Open color chooser dialog"""
        try:
            color = colorchooser.askcolor(parent=parent)[1]
            if color:
                color_var.set(color)
        except Exception as e:
            print(f"Error choosing color: {e}")

    def refresh_highlighting(self):
        """Refresh syntax highlighting"""
        try:
            self.highlight_syntax()
            messagebox.showinfo(
                "Highlighting Refreshed", "Syntax highlighting has been refreshed!"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Could not refresh highlighting: {e}")

    def get_info(self):
        """Get detailed plugin information"""
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "features": [
                "Real-time syntax highlighting",
                "Support for PILOT, BASIC, and Logo languages",
                "Customizable color schemes",
                "Keyword highlighting",
                "String and comment detection",
                "Number highlighting",
                "Toggle highlighting on/off",
            ],
            "permissions": ["editor", "menu"],
        }
