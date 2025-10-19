"""
Code Formatter Plugin for Time_Warp IDE
Provides automatic code formatting and beautification
"""

import tkinter as tk
from tkinter import messagebox
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
    """Code formatter plugin implementation"""

    def __init__(self, ide_instance):
        super().__init__(ide_instance)
        self.name = "Code Formatter"
        self.version = "1.2.0"
        self.author = "Time_Warp Development Team"
        self.description = "Automatic code formatting and beautification for PILOT, BASIC, and Logo programs"
        self.menu_items = []

    def activate(self):
        """Activate the plugin - add menu items and functionality"""
        try:
            self.add_menu_items()
            if hasattr(self.ide, "status_label"):
                self.ide.status_label.config(text="Code Formatter plugin activated!")
            print(f"✅ {self.name} activated successfully")
        except Exception as e:
            print(f"❌ Error activating {self.name}: {e}")

    def deactivate(self):
        """Deactivate the plugin - remove menu items"""
        try:
            self.remove_menu_items()
            if hasattr(self.ide, "status_label"):
                self.ide.status_label.config(text="Code Formatter plugin deactivated")
            print(f"🔌 {self.name} deactivated")
        except Exception as e:
            print(f"❌ Error deactivating {self.name}: {e}")

    def add_menu_items(self):
        """Add plugin-specific menu items"""
        try:
            # Add to Edit menu if it exists
            if hasattr(self.ide, "menubar"):
                # Find the Edit menu
                edit_menu = None
                for i in range(self.ide.menubar.index("end") + 1):
                    try:
                        if self.ide.menubar.entryconfig(i, "label")[4][1] == "Edit":
                            edit_menu = self.ide.menubar.nametowidget(
                                self.ide.menubar.entryconfig(i, "menu")[4][1]
                            )
                            break
                    except:
                        continue

                if edit_menu:
                    # Add separator
                    edit_menu.add_separator()

                    # Add formatting options
                    edit_menu.add_command(
                        label="🎨 Format Code", command=self.format_current_code
                    )
                    edit_menu.add_command(
                        label="📐 Indent Code", command=self.indent_code
                    )
                    edit_menu.add_command(
                        label="🧹 Clean Whitespace", command=self.clean_whitespace
                    )

                    self.menu_items = [
                        "🎨 Format Code",
                        "📐 Indent Code",
                        "🧹 Clean Whitespace",
                    ]

        except Exception as e:
            print(f"Error adding menu items: {e}")

    def remove_menu_items(self):
        """Remove plugin menu items"""
        try:
            # In a full implementation, we would track and remove specific menu items
            self.menu_items = []
        except Exception as e:
            print(f"Error removing menu items: {e}")

    def format_current_code(self):
        """Format the current code in the editor"""
        try:
            if not hasattr(self.ide, "editor"):
                messagebox.showwarning("No Editor", "No editor found to format")
                return

            # Get current code
            current_code = self.ide.editor.get("1.0", tk.END)

            if not current_code.strip():
                messagebox.showinfo("No Code", "No code to format")
                return

            # Detect language and format accordingly
            formatted_code = self.format_code(current_code)

            if formatted_code != current_code:
                # Replace editor content
                self.ide.editor.delete("1.0", tk.END)
                self.ide.editor.insert("1.0", formatted_code)
                messagebox.showinfo(
                    "Code Formatted", "Code has been formatted successfully!"
                )
            else:
                messagebox.showinfo(
                    "Already Formatted", "Code is already properly formatted"
                )

        except Exception as e:
            messagebox.showerror("Format Error", f"Could not format code: {e}")

    def indent_code(self):
        """Fix indentation in the current code"""
        try:
            if not hasattr(self.ide, "editor"):
                messagebox.showwarning("No Editor", "No editor found")
                return

            current_code = self.ide.editor.get("1.0", tk.END)
            indented_code = self.fix_indentation(current_code)

            if indented_code != current_code:
                self.ide.editor.delete("1.0", tk.END)
                self.ide.editor.insert("1.0", indented_code)
                messagebox.showinfo(
                    "Indentation Fixed", "Code indentation has been corrected!"
                )
            else:
                messagebox.showinfo(
                    "Already Indented", "Code indentation is already correct"
                )

        except Exception as e:
            messagebox.showerror("Indent Error", f"Could not fix indentation: {e}")

    def clean_whitespace(self):
        """Clean unnecessary whitespace"""
        try:
            if not hasattr(self.ide, "editor"):
                messagebox.showwarning("No Editor", "No editor found")
                return

            current_code = self.ide.editor.get("1.0", tk.END)
            cleaned_code = self.clean_code_whitespace(current_code)

            if cleaned_code != current_code:
                self.ide.editor.delete("1.0", tk.END)
                self.ide.editor.insert("1.0", cleaned_code)
                messagebox.showinfo(
                    "Whitespace Cleaned", "Unnecessary whitespace has been removed!"
                )
            else:
                messagebox.showinfo("Already Clean", "Code whitespace is already clean")

        except Exception as e:
            messagebox.showerror("Clean Error", f"Could not clean whitespace: {e}")

    def format_code(self, code):
        """Format code based on detected language"""
        # Detect language
        if self.is_pilot_code(code):
            return self.format_pilot_code(code)
        elif self.is_basic_code(code):
            return self.format_basic_code(code)
        elif self.is_logo_code(code):
            return self.format_logo_code(code)
        else:
            return self.format_generic_code(code)

    def is_pilot_code(self, code):
        """Check if code is PILOT"""
        pilot_commands = ["T:", "A:", "Y:", "N:", "J:", "M:", "C:", "U:", "E:"]
        lines = code.split("\n")
        pilot_count = sum(
            1
            for line in lines
            if any(line.strip().startswith(cmd) for cmd in pilot_commands)
        )
        return pilot_count > len(lines) * 0.3  # 30% of lines are PILOT commands

    def is_basic_code(self, code):
        """Check if code is BASIC"""
        basic_keywords = [
            "PRINT",
            "INPUT",
            "LET",
            "GOTO",
            "GOSUB",
            "IF",
            "THEN",
            "FOR",
            "NEXT",
            "REM",
        ]
        upper_code = code.upper()
        return any(keyword in upper_code for keyword in basic_keywords)

    def is_logo_code(self, code):
        """Check if code is Logo"""
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
        ]
        upper_code = code.upper()
        return any(cmd in upper_code for cmd in logo_commands)

    def format_pilot_code(self, code):
        """Format PILOT code"""
        lines = code.split("\n")
        formatted_lines = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                formatted_lines.append("")
                continue

            # PILOT commands should be uppercase
            if ":" in stripped and len(stripped) > 2:
                cmd = stripped[:2].upper()
                rest = stripped[2:]
                formatted_lines.append(f"{cmd}{rest}")
            else:
                formatted_lines.append(stripped)

        return "\n".join(formatted_lines)

    def format_basic_code(self, code):
        """Format BASIC code"""
        lines = code.split("\n")
        formatted_lines = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                formatted_lines.append("")
                continue

            # BASIC keywords should be uppercase
            words = stripped.split()
            formatted_words = []

            for word in words:
                # Check if it's a BASIC keyword
                if word.upper() in [
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
                ]:
                    formatted_words.append(word.upper())
                else:
                    formatted_words.append(word)

            formatted_lines.append(" ".join(formatted_words))

        return "\n".join(formatted_lines)

    def format_logo_code(self, code):
        """Format Logo code"""
        lines = code.split("\n")
        formatted_lines = []
        indent_level = 0

        for line in lines:
            stripped = line.strip()
            if not stripped:
                formatted_lines.append("")
                continue

            # Decrease indent for closing brackets
            if stripped.startswith("]"):
                indent_level = max(0, indent_level - 1)

            # Apply indentation
            indented_line = "  " * indent_level + stripped
            formatted_lines.append(indented_line)

            # Increase indent for opening brackets or REPEAT
            if "REPEAT" in stripped.upper() or stripped.endswith("["):
                indent_level += 1

        return "\n".join(formatted_lines)

    def format_generic_code(self, code):
        """Format generic code"""
        lines = code.split("\n")
        formatted_lines = []

        for line in lines:
            # Just clean up basic whitespace
            stripped = line.rstrip()
            formatted_lines.append(stripped)

        return "\n".join(formatted_lines)

    def fix_indentation(self, code):
        """Fix indentation issues"""
        lines = code.split("\n")
        fixed_lines = []

        for line in lines:
            # Remove leading/trailing whitespace and normalize
            stripped = line.strip()
            if stripped:
                fixed_lines.append(stripped)
            else:
                fixed_lines.append("")

        return "\n".join(fixed_lines)

    def clean_code_whitespace(self, code):
        """Clean unnecessary whitespace"""
        # Remove trailing whitespace
        lines = code.split("\n")
        cleaned_lines = [line.rstrip() for line in lines]

        # Remove empty lines at the end
        while cleaned_lines and not cleaned_lines[-1]:
            cleaned_lines.pop()

        # Normalize multiple consecutive empty lines to single empty line
        normalized_lines = []
        prev_empty = False

        for line in cleaned_lines:
            if not line.strip():
                if not prev_empty:
                    normalized_lines.append("")
                    prev_empty = True
            else:
                normalized_lines.append(line)
                prev_empty = False

        return "\n".join(normalized_lines) + "\n" if normalized_lines else ""

    def get_info(self):
        """Get detailed plugin information"""
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "features": [
                "Auto-detect PILOT, BASIC, and Logo code",
                "Format code according to language conventions",
                "Fix indentation issues",
                "Clean unnecessary whitespace",
                "Normalize keyword capitalization",
            ],
            "permissions": ["editor", "filesystem", "menu"],
        }
