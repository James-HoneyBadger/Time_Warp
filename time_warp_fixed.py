#!/usr/bin/env python3

# Set pygame environment variable to suppress AVX2 warning
import os
import sys

os.environ['PYGAME_DETECT_AVX2'] = '1'

# Suppress pygame AVX2 warning
import warnings

warnings.filterwarnings("ignore", message=".*avx2.*", category=RuntimeWarning)

"""
Time_Warp IDE - Simple Educational Programming Environment

A minimal Tkinter-based IDE for running multi-language programs through the Time_Warp interpreter.
Supports Time Warp, PILOT, BASIC, Logo, Pascal, and Prolog execution.

Features:
- Simple text editor with Courier font
- One-click program execution
- Integrated interpreter with 6 language support
- Turtle graphics for visual languages
- Educational error messages

Usage:
    python Time_Warp.py

The IDE provides a basic text editing interface where users can write and execute
programs in multiple programming languages with immediate visual feedback.
"""

# Check and setup environment before importing other modules
def check_environment():
    """Check if environment is properly set up, set it up if needed"""
    import subprocess
    import sys
    from pathlib import Path

    # Check if requirements.py exists
    requirements_script = Path(__file__).parent / "requirements.py"
    if not requirements_script.exists():
        print("⚠️  requirements.py not found, skipping environment check")
        return True

    # Run requirements check
    try:
        print("🔍 Checking environment requirements...")
        result = subprocess.run([sys.executable, str(requirements_script), "--check"],
                              capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            print("✅ Environment is properly configured")
            # Activate virtual environment in current process
            activate_venv_in_process()
            return True
        else:
            print("🔧 Environment needs setup...")
            # Run full setup
            result = subprocess.run([sys.executable, str(requirements_script)],
                                  timeout=600)  # 10 minute timeout for setup
            if result.returncode == 0:
                # Activate virtual environment in current process after setup
                activate_venv_in_process()
                return True
            return False

    except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
        print(f"⚠️  Environment check failed: {e}")
        print("Continuing with startup...")
        return True
    except Exception as e:
        print(f"⚠️  Unexpected error during environment check: {e}")
        return True

def activate_venv_in_process():
    """Activate virtual environment in the current process"""
    import os
    import sys
    from pathlib import Path

    project_root = Path(__file__).parent
    venv_path = project_root / ".venv"

    if not venv_path.exists():
        return False

    # Get platform-specific paths
    if os.name == 'nt':  # Windows
        python_exe = venv_path / "Scripts" / "python.exe"
        site_packages = venv_path / "Lib" / "site-packages"
    else:  # Unix-like systems
        python_exe = venv_path / "bin" / "python"
        site_packages = venv_path / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"

    if not python_exe.exists():
        return False

    # Add venv site-packages to Python path
    if str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))

    # Update environment variables
    os.environ['VIRTUAL_ENV'] = str(venv_path)
    os.environ['PATH'] = str(venv_path / "bin") + os.pathsep + os.environ.get('PATH', '')

    return True

# Run environment check before importing other modules
if not check_environment():
    print("❌ Environment setup failed. Please check the errors above.")
    sys.exit(1)

import json
import os
import re
# Now import other modules after environment is verified
import tkinter as tk
from tkinter import messagebox, ttk

from core.interpreter import Time_WarpInterpreter
from unified_canvas import Theme, UnifiedCanvas

# Import compiler system
try:
    from core.compiler import Time_WarpCompiler
    COMPILER_AVAILABLE = True
except ImportError:
    COMPILER_AVAILABLE = False
    Time_WarpCompiler = None

# Import advanced editor features
try:
    from src.timewarp.gui.editor.features import (AdvancedSyntaxHighlighter,
                                                  AutoCompletionEngine,
                                                  CodeFoldingSystem,
                                                  RealTimeSyntaxChecker)
    ADVANCED_EDITOR_AVAILABLE = True
except ImportError:
    ADVANCED_EDITOR_AVAILABLE = False


class EnhancedCodeEditor(tk.Frame):
    """Enhanced code editor with syntax highlighting, auto-completion, and advanced features"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # Create main frame
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill="both", expand=True)

        # Create line numbers
        self.line_numbers = tk.Text(
            self.main_frame,
            width=4,
            padx=3,
            pady=3,
            takefocus=0,
            border=0,
            background="#f0f0f0",
            foreground="#666666",
            font=("Consolas", 10),
            state="disabled"
        )
        self.line_numbers.pack(side="left", fill="y")

        # Create main text widget
        self.text_widget = tk.Text(
            self.main_frame,
            wrap="none",
            font=("Consolas", 11),
            undo=True,
            padx=8,
            pady=8,
            bg="#ffffff",
            relief="flat",
            insertbackground="black"
        )
        self.text_widget.pack(side="left", fill="both", expand=True)

        # Create horizontal scrollbar
        self.h_scrollbar = tk.Scrollbar(self, orient="horizontal", command=self.text_widget.xview)
        self.h_scrollbar.pack(side="bottom", fill="x")
        self.text_widget.config(xscrollcommand=self.h_scrollbar.set)

        # Create vertical scrollbar
        self.v_scrollbar = tk.Scrollbar(self.main_frame, orient="vertical", command=self._on_scroll)
        self.v_scrollbar.pack(side="right", fill="y")

        # Initialize advanced features if available
        self.syntax_highlighter = None
        self.auto_completion = None
        self.syntax_checker = None
        self.code_folding = None

        if ADVANCED_EDITOR_AVAILABLE:
            self._init_advanced_features()

        # Bind events
        self.text_widget.bind("<KeyRelease>", self._on_key_release)
        self.text_widget.bind("<Tab>", self._handle_tab)
        self.text_widget.bind("<Shift-Tab>", self._handle_shift_tab)
        self.text_widget.bind("<Control-slash>", self._toggle_comment)
        self.text_widget.bind("<Control-f>", self._find_replace)
        self.text_widget.bind("<F3>", self._find_next)

        # Update line numbers on scroll and text changes
        self.text_widget.bind("<MouseWheel>", self._update_line_numbers)
        self.text_widget.bind("<Button-4>", self._update_line_numbers)  # Linux scroll up
        self.text_widget.bind("<Button-5>", self._update_line_numbers)  # Linux scroll down

        # Line numbers visibility flag
        self.line_numbers_visible = True


    def _init_advanced_features(self):
        """Initialize advanced editor features"""
        try:
            # Syntax highlighting
            self.syntax_highlighter = AdvancedSyntaxHighlighter(self.text_widget)
            self.text_widget.bind("<KeyRelease>", self.syntax_highlighter.highlight_syntax, add=True)

            # Auto-completion
            self.auto_completion = AutoCompletionEngine(self.text_widget)
            self.text_widget.bind("<Control-space>", self.auto_completion.show_completions)

            # Syntax checking
            self.syntax_checker = RealTimeSyntaxChecker(self.text_widget)
            self.text_widget.bind("<KeyRelease>", self.syntax_checker.check_syntax, add=True)

            # Code folding
            self.code_folding = CodeFoldingSystem(self.text_widget)

        except Exception as e:
            print(f"Warning: Could not initialize advanced editor features: {e}")

    def _on_scroll(self, *args):
        """Handle scroll events"""
        self.text_widget.yview(*args)
        self.line_numbers.yview(*args)
        self._update_line_numbers()

    def _on_key_release(self, event):
        """Handle key release events"""
        # Update line numbers
        self._update_line_numbers()

        # Auto-indent on Enter
        if event.keysym == "Return":
            self._auto_indent()

    def _update_line_numbers(self, event=None):
        """Update line numbers display"""
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", tk.END)

        # Get the number of lines in the text widget
        text_content = self.text_widget.get("1.0", tk.END)
        lines = text_content.split("\n")

        # Add line numbers
        for i in range(1, len(lines)):
            self.line_numbers.insert(tk.END, f"{i}\n")

        self.line_numbers.config(state="disabled")

        # Sync scrolling
        self.line_numbers.yview_moveto(self.text_widget.yview()[0])

    def _auto_indent(self):
        """Auto-indent new lines"""
        # Get current line
        cursor_pos = self.text_widget.index(tk.INSERT)
        line_num = int(cursor_pos.split(".")[0])

        if line_num > 1:
            # Get previous line's indentation
            prev_line = self.text_widget.get(f"{line_num-1}.0", f"{line_num-1}.end")
            indent = ""
            for char in prev_line:
                if char in " \t":
                    indent += char
                else:
                    break

            # Check if previous line ends with colon (Python/BASIC block start)
            if prev_line.rstrip().endswith(":"):
                if "\t" in indent:
                    indent += "\t"
                else:
                    indent += "    "

            # Insert indentation
            if indent:
                self.text_widget.insert(cursor_pos, indent)

    def _handle_tab(self, event):
        """Handle Tab key for indentation"""
        self.text_widget.insert(tk.INSERT, "    ")
        return "break"

    def _handle_shift_tab(self, event=None):
        """Handle Shift+Tab for unindentation"""
        cursor_pos = self.text_widget.index(tk.INSERT)
        line_start = f"{cursor_pos.split('.')[0]}.0"
        line_text = self.text_widget.get(line_start, cursor_pos)

        # Remove up to 4 spaces from start of line
        spaces_to_remove = 0
        for char in line_text:
            if char == " " and spaces_to_remove < 4:
                spaces_to_remove += 1
            else:
                break

        if spaces_to_remove > 0:
            remove_start = f"{cursor_pos.split('.')[0]}.{int(cursor_pos.split('.')[1]) - spaces_to_remove}"
            self.text_widget.delete(remove_start, cursor_pos)

        return "break"

    def _toggle_comment(self, event=None):
        """Toggle comments on selected lines or current line"""
        try:
            # Get selection or current line
            try:
                start_pos = self.text_widget.index(tk.SEL_FIRST)
                end_pos = self.text_widget.index(tk.SEL_LAST)
                start_line = int(start_pos.split(".")[0])
                end_line = int(end_pos.split(".")[0])
            except tk.TclError:
                # No selection, use current line
                cursor_pos = self.text_widget.index(tk.INSERT)
                start_line = end_line = int(cursor_pos.split(".")[0])

            # Process each line
            for line_num in range(start_line, end_line + 1):
                line_start = f"{line_num}.0"
                line_end = f"{line_num}.end"
                line_text = self.text_widget.get(line_start, line_end)

                # Detect language and comment style
                if line_text.strip().startswith("def ") or line_text.strip().startswith("class ") or "import " in line_text:
                    comment_char = "#"  # Python
                elif "::" in line_text or line_text.strip().startswith("REM"):
                    comment_char = "//"  # Time Warp style
                elif any(cmd in line_text.upper() for cmd in ["FORWARD", "PRINT", "REM"]):
                    comment_char = ";"  # Time Warp style
                else:
                    comment_char = "#"  # Default

                # Toggle comment
                if line_text.strip().startswith(comment_char):
                    # Uncomment
                    comment_start = line_text.find(comment_char)
                    self.text_widget.delete(f"{line_num}.{comment_start}", f"{line_num}.{comment_start + len(comment_char)}")
                else:
                    # Comment
                    self.text_widget.insert(line_start, comment_char)

        except Exception as e:
            print(f"Comment toggle error: {e}")

        return "break"

    def _find_replace(self, event):
        """Open find/replace dialog"""
        self._show_find_dialog()
        return "break"

    def _find_next(self, event):
        """Find next occurrence"""
        if hasattr(self, '_last_find_text') and self._last_find_text:
            self._find_text(self._last_find_text)
        return "break"

    def _show_find_dialog(self):
        """Show find/replace dialog"""
        dialog = tk.Toplevel(self)
        dialog.title("Find & Replace")
        dialog.geometry("400x150")
        dialog.transient(self.winfo_toplevel())

        # Find text
        tk.Label(dialog, text="Find:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        find_entry = tk.Entry(dialog, width=30)
        find_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5)

        # Replace text
        tk.Label(dialog, text="Replace:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        replace_entry = tk.Entry(dialog, width=30)
        replace_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5)

        # Buttons
        find_btn = tk.Button(dialog, text="Find", command=lambda: self._find_text(find_entry.get()))
        find_btn.grid(row=2, column=0, padx=5, pady=5)

        replace_btn = tk.Button(dialog, text="Replace", command=lambda: self._replace_text(find_entry.get(), replace_entry.get()))
        replace_btn.grid(row=2, column=1, padx=5, pady=5)

        replace_all_btn = tk.Button(dialog, text="Replace All", command=lambda: self._replace_all_text(find_entry.get(), replace_entry.get()))
        replace_all_btn.grid(row=2, column=2, padx=5, pady=5)

        find_entry.focus()

    def _find_text(self, text):
        """Find text in editor"""
        if not text:
            return

        self._last_find_text = text

        # Get current position
        start_pos = self.text_widget.index(tk.INSERT)

        # Search from current position
        pos = self.text_widget.search(text, start_pos, tk.END)
        if not pos:
            # Wrap around to beginning
            pos = self.text_widget.search(text, "1.0", tk.END)

        if pos:
            # Select the found text
            end_pos = f"{pos}+{len(text)}c"
            self.text_widget.tag_remove("sel", "1.0", tk.END)
            self.text_widget.tag_add("sel", pos, end_pos)
            self.text_widget.mark_set(tk.INSERT, end_pos)
            self.text_widget.see(pos)

    def _replace_text(self, find_text, replace_text):
        """Replace selected text"""
        try:
            self.text_widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text_widget.insert(tk.INSERT, replace_text)
            self._find_text(find_text)  # Find next occurrence
        except tk.TclError:
            pass  # No selection

    def _replace_all_text(self, find_text, replace_text):
        """Replace all occurrences"""
        if not find_text:
            return

        count = 0
        start_pos = "1.0"

        while True:
            pos = self.text_widget.search(find_text, start_pos, tk.END)
            if not pos:
                break

            end_pos = f"{pos}+{len(find_text)}c"
            self.text_widget.delete(pos, end_pos)
            self.text_widget.insert(pos, replace_text)
            start_pos = pos
            count += 1

        messagebox.showinfo("Replace All", f"Replaced {count} occurrences")

    # Delegate methods to text widget
    def get(self, *args, **kwargs):
        return self.text_widget.get(*args, **kwargs)

    def insert(self, *args, **kwargs):
        return self.text_widget.insert(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.text_widget.delete(*args, **kwargs)

    def index(self, *args, **kwargs):
        return self.text_widget.index(*args, **kwargs)

    def tag_add(self, *args, **kwargs):
        return self.text_widget.tag_add(*args, **kwargs)

    def tag_remove(self, *args, **kwargs):
        return self.text_widget.tag_remove(*args, **kwargs)

    def tag_configure(self, *args, **kwargs):
        return self.text_widget.tag_configure(*args, **kwargs)

    def bind(self, *args, **kwargs):
        return self.text_widget.bind(*args, **kwargs)

    def focus_set(self):
        return self.text_widget.focus_set()

    def focus(self):
        """Set focus to text widget"""
        return self.text_widget.focus_set()


class TimeWarpApp:
    """
    Main application class for the Time_Warp IDE.

    Creates a simple GUI with:
    - Text area for code editing
    - Run button for program execution
    - Integrated Time_Warp interpreter for multi-language support
    """

    def __init__(self, root):
        print("[DEBUG] Entered TimeWarpApp.__init__")
        self.root = root
        self.root.title("Time_Warp IDE v1.3.0")
        self.root.geometry("1000x700")  # Increased size for better content visibility
        self.root.minsize(800, 600)  # Set minimum size to prevent too small windows
        self.current_file = None
        self.selected_theme = "Spring"  # Start with light theme for contrast
        self.selected_font_family = "Consolas"  # Default monospace font
        self.selected_font_size = 11  # Default font size
        self.config_path = os.path.expanduser("~/.Time_Warp/config.json")
        self.interpreter = Time_WarpInterpreter()
        self.interpreter.ide_turtle_canvas = None  # Will be set later
        try:
            from plugins import PluginManager, PluginManagerDialog
            self.plugin_manager = PluginManager(self)
            self.plugin_manager_dialog = None
        except Exception as e:
            self.plugin_manager = None
            self.plugin_manager_dialog = None
        self.theme_manager = None
        try:
            from src.timewarp.utils.theme import ThemeManager, available_themes
            self.theme_manager = ThemeManager()
        except Exception:
            pass

        # Initialize compiler system
        self.compiler = None
        if COMPILER_AVAILABLE:
            try:
                self.compiler = Time_WarpCompiler()
                print("[DEBUG] Compiler system initialized successfully")
            except Exception as e:
                print(f"[WARNING] Could not initialize compiler system: {e}")
                self.compiler = None
        self.root.bind("<F5>", lambda e: self.run_program())
        self.root.bind("<Control-r>", lambda e: self.run_program())
        self.root.bind("<Control-c>", lambda e: self._copy_text())
        self.root.bind("<Control-v>", lambda e: self._paste_text())
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        print("[DEBUG] Calling _create_ui()")
        self._create_ui()
        print("[DEBUG] Calling _load_theme_config()")
        self._load_theme_config()
        self._load_font_config()
        print("[DEBUG] Finished TimeWarpApp.__init__")

    def new_file(self):
        # Clear any loaded program
        if hasattr(self.interpreter, 'program_lines'):
            self.interpreter.program_lines = []
        self.current_file = None
        self.unified_canvas.write_text("New program started. Previous program cleared.\n", color=10)
        self.status_label.config(text="🆕 New program started")

    def open_file(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(filetypes=[("All Files", "*.*"), ("Time Warp", "*.tw"), ("Python", "*.py"), ("Text", "*.txt")])
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Store the current file path
                self.current_file = file_path

                # Check if this looks like a line-numbered BASIC program
                lines = content.strip().split('\n')
                is_line_numbered_program = False

                for line in lines:
                    line = line.strip()
                    if line and line[0].isdigit():
                        # Check if it has a space after the line number
                        parts = line.split(None, 1)
                        if len(parts) == 2 and parts[0].isdigit():
                            is_line_numbered_program = True
                            break

                if is_line_numbered_program:
                    # Load as line-numbered program
                    self.interpreter.program_lines = []
                    for line in lines:
                        line = line.strip()
                        if line and line[0].isdigit():
                            try:
                                parts = line.split(None, 1)
                                if len(parts) == 2:
                                    line_num = int(parts[0])
                                    cmd = parts[1]
                                    # Insert in line number order
                                    insert_pos = 0
                                    for i, (existing_num, _) in enumerate(self.interpreter.program_lines):
                                        if existing_num > line_num:
                                            break
                                        insert_pos = i + 1
                                    self.interpreter.program_lines.insert(insert_pos, (line_num, cmd))
                            except (ValueError, IndexError):
                                continue

                    self.unified_canvas.write_text(f"Loaded program from {file_path}\n", color=10)
                    self.unified_canvas.write_text(f"{len(self.interpreter.program_lines)} lines loaded.\n", color=10)
                    self.status_label.config(text=f"📂 Loaded program: {file_path}")
                else:
                    # Display file content in canvas
                    self.unified_canvas.write_text(f"File: {file_path}\n", color=11)
                    self.unified_canvas.write_text("=" * 50 + "\n", color=11)
                    self.unified_canvas.write_text(content, color=15)
                    self.unified_canvas.write_text("\n" + "=" * 50 + "\n", color=11)
                    self.status_label.config(text=f"📂 Displayed file: {file_path}")

            except Exception as e:
                self.unified_canvas.write_text(f"Error loading file: {str(e)}\n", color=12)
                self.status_label.config(text=f"❌ Error loading file: {str(e)}")

    def save_file(self):
        import os
        if hasattr(self, "current_file") and self.current_file:
            file_path = self.current_file
        else:
            file_path = self.save_file_as()
            if not file_path:
                return

        try:
            # Check if we have a line-numbered program to save
            if hasattr(self.interpreter, 'program_lines') and self.interpreter.program_lines:
                # Save as line-numbered program
                with open(file_path, "w", encoding="utf-8") as f:
                    for line_num, cmd in self.interpreter.program_lines:
                        f.write(f"{line_num} {cmd}\n")
                self.unified_canvas.write_text(f"Program saved to {file_path}\n", color=10)
                self.status_label.config(text=f"💾 Saved program: {file_path}")
            else:
                # No program to save
                self.unified_canvas.write_text("No program loaded to save.\n", color=14)
                self.unified_canvas.write_text("Create a line-numbered program first.\n", color=14)
                self.status_label.config(text="❌ No program to save")
        except Exception as e:
            self.unified_canvas.write_text(f"Error saving file: {str(e)}\n", color=12)
            self.status_label.config(text=f"❌ Error saving file: {str(e)}")

    def save_file_as(self):
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("All Files", "*.*"), ("Time Warp", "*.tw"), ("Python", "*.py"), ("Text", "*.txt")])
        if file_path:
            try:
                # Check if we have a line-numbered program to save
                if hasattr(self.interpreter, 'program_lines') and self.interpreter.program_lines:
                    # Save as line-numbered program
                    with open(file_path, "w", encoding="utf-8") as f:
                        for line_num, cmd in self.interpreter.program_lines:
                            f.write(f"{line_num} {cmd}\n")
                    self.unified_canvas.write_text(f"Program saved as {file_path}\n", color=10)
                    self.status_label.config(text=f"💾 Saved program as: {file_path}")
                    self.current_file = file_path
                else:
                    # No program to save
                    self.unified_canvas.write_text("No program loaded to save.\n", color=14)
                    self.unified_canvas.write_text("Create a line-numbered program first.\n", color=14)
                    self.status_label.config(text="❌ No program to save")
            except Exception as e:
                self.unified_canvas.write_text(f"Error saving file: {str(e)}\n", color=12)
                self.status_label.config(text=f"❌ Error saving file: {str(e)}")
        return file_path if 'file_path' in locals() and file_path else None

    def clear_editor(self):
        """Clear editor is not needed in unified canvas mode"""
        self.unified_canvas.write_text("Code editor is integrated into unified canvas.\n")
        self.status_label.config(text="📝 Code editor is part of unified canvas.")

    def clear_output(self):
        # Clear text output from unified canvas
        self.unified_canvas.clear_text()
        self.status_label.config(text="🧹 Output cleared.")

    def clear_turtle(self):
        # Clear graphics from unified canvas
        self.unified_canvas.clear_graphics()
        if hasattr(self.interpreter, "turtle_graphics"):
            self.interpreter.turtle_graphics = None
        self.status_label.config(text="🧹 Graphics cleared.")

    def _toggle_line_numbers(self):
        """Line numbers not applicable in unified canvas mode"""
        self.unified_canvas.write_text("Line numbers are not applicable in unified canvas mode.\n")
        self.status_label.config(text="📏 Line numbers not available in unified canvas mode.")

    def _open_find_replace(self):
        """Find/Replace not available in unified canvas mode"""
        messagebox.showinfo("Find/Replace", "Find/Replace is not available in unified canvas mode.\nUse command line interface for text operations.")

    def _find_next(self):
        """Find Next not available in unified canvas mode"""
        messagebox.showinfo("Find Next", "Find Next is not available in unified canvas mode.\nUse command line interface for text operations.")

    def _toggle_comment(self):
        """Toggle comment not available in unified canvas mode"""
        messagebox.showinfo("Toggle Comment", "Comment toggle is not available in unified canvas mode.\nUse command line interface for editing.")

    def _copy_text(self):
        """Copy not available in unified canvas mode"""
        pass  # Clipboard operations not applicable in canvas mode

    def _paste_text(self):
        """Paste not available in unified canvas mode"""
        pass  # Clipboard operations not applicable in canvas mode

    def _increase_indent(self):
        """Indent not available in unified canvas mode"""
        pass

    def _decrease_indent(self):
        """Unindent not available in unified canvas mode"""
        pass

    def _undo(self):
        """Undo not available in unified canvas mode"""
        self.status_label.config(text="↩️ Undo not available in unified canvas mode.")

    def _redo(self):
        """Redo not available in unified canvas mode"""
        self.status_label.config(text="↪️ Redo not available in unified canvas mode.")

    def _cut_text(self):
        """Cut not available in unified canvas mode"""