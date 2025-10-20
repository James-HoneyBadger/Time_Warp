#!/usr/bin/env python3

# Set pygame environment variable to suppress AVX2 warning
import os
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
    import sys
    import subprocess
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
    import sys
    import os
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

# Now import other modules after environment is verified
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from core.interpreter import Time_WarpInterpreter
import os
import json
import re
from unified_canvas import UnifiedCanvas

# Import compiler system
try:
    from core.compiler import Time_WarpCompiler
    COMPILER_AVAILABLE = True
except ImportError:
    COMPILER_AVAILABLE = False
    Time_WarpCompiler = None

# Import advanced editor features
try:
    from src.timewarp.gui.editor.features import (
        AdvancedSyntaxHighlighter,
        AutoCompletionEngine,
        RealTimeSyntaxChecker,
        CodeFoldingSystem,
    )
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

    def request_input(self, prompt, input_type=str):
        """Show input prompt in output panel and enable entry field."""
        self._expected_input_type = input_type
        self.output_panel.config(state="normal")
        self.output_panel.insert("end", f"{prompt}")
        self.output_panel.see("end")
        self.output_panel.config(state="disabled")
        self.output_entry_var.set("")
        self.output_entry.config(state="normal")
        self.output_entry.focus_set()

    def _on_output_entry_submit(self, event=None):
        value = self.output_entry_var.get()
        input_type = self._expected_input_type or str
        try:
            typed_value = input_type(value)
        except Exception:
            self.output_panel.config(state="normal")
            self.output_panel.insert("end", f"\n❌ Invalid input type. Expected {input_type.__name__}.\n")
            self.output_panel.config(state="disabled")
            self.output_entry_var.set("")
            return
        self.output_entry.config(state="disabled")
        self.output_panel.config(state="normal")
        self.output_panel.insert("end", f"{typed_value}\n")
        self.output_panel.config(state="disabled")
        # Send input to interpreter
        if hasattr(self, "_input_callback") and self._input_callback:
            self._input_callback(typed_value)
        self._input_callback = None
        self._expected_input_type = None


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
        # Editor is no longer part of the unified canvas - this method may be deprecated
        self.status_label.config(text="🧹 Code editor cleared.")

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
        """Toggle line numbers visibility in the code editor"""
        if hasattr(self.editor, 'line_numbers_visible'):
            # Enhanced editor
            self.editor.line_numbers_visible = not self.editor.line_numbers_visible
            self.editor._update_line_numbers()
            status = "shown" if self.editor.line_numbers_visible else "hidden"
            self.status_label.config(text=f"📏 Line numbers {status}.")
        else:
            # Basic editor - line numbers not supported
            messagebox.showinfo("Line Numbers", "Line numbers are only available in enhanced editor mode.")

    def _open_find_replace(self):
        """Open find/replace dialog"""
        if hasattr(self.editor, '_show_find_dialog'):
            self.editor._show_find_dialog()
        else:
            messagebox.showinfo("Find/Replace", "Find/Replace is not available in basic editor mode.")

    def _find_next(self):
        """Find next occurrence"""
        if hasattr(self.editor, '_find_next'):
            self.editor._find_next()
        else:
            messagebox.showinfo("Find Next", "Find Next is not available in basic editor mode.")

    def _toggle_comment(self):
        """Toggle comment on current line/selection"""
        if hasattr(self.editor, '_toggle_comment'):
            self.editor._toggle_comment(event=None)
        else:
            messagebox.showinfo("Toggle Comment", "Comment toggle is not available in basic editor mode.")

    def _copy_text(self):
        """Copy selected text to clipboard"""
        try:
            if hasattr(self.editor, 'text_widget'):
                # Enhanced editor
                selected_text = self.editor.text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
                if selected_text:
                    self.root.clipboard_clear()
                    self.root.clipboard_append(selected_text)
            else:
                # Basic editor
                selected_text = self.editor.get(tk.SEL_FIRST, tk.SEL_LAST)
                if selected_text:
                    self.root.clipboard_clear()
                    self.root.clipboard_append(selected_text)
        except tk.TclError:
            # No text selected
            pass

    def _paste_text(self):
        """Paste text from clipboard"""
        try:
            clipboard_text = self.root.clipboard_get()
            if hasattr(self.editor, 'text_widget'):
                # Enhanced editor
                self.editor.text_widget.insert(tk.INSERT, clipboard_text)
            else:
                # Basic editor
                self.editor.insert(tk.INSERT, clipboard_text)
        except tk.TclError:
            # Clipboard empty or unavailable
            pass

    def _increase_indent(self):
        """Increase indentation"""
        if hasattr(self.editor, 'text_widget'):
            # Enhanced editor
            self.editor.text_widget.insert(tk.INSERT, "    ")
        else:
            # Basic editor
            self.editor.insert(tk.INSERT, "    ")

    def _decrease_indent(self):
        """Decrease indentation"""
        if hasattr(self.editor, '_handle_shift_tab'):
            self.editor._handle_shift_tab(event=None)
        else:
            messagebox.showinfo("Decrease Indent", "Indentation tools are not available in basic editor mode.")

    def _undo(self):
        """Undo last action"""
        try:
            if hasattr(self.editor, 'text_widget'):
                self.editor.text_widget.edit_undo()
            else:
                self.editor.edit_undo()
            self.status_label.config(text="↩️ Undo completed.")
        except tk.TclError:
            self.status_label.config(text="↩️ Nothing to undo.")

    def _redo(self):
        """Redo last undone action"""
        try:
            if hasattr(self.editor, 'text_widget'):
                self.editor.text_widget.edit_redo()
            else:
                self.editor.edit_redo()
            self.status_label.config(text="↪️ Redo completed.")
        except tk.TclError:
            self.status_label.config(text="↪️ Nothing to redo.")

    def _cut_text(self):
        """Cut selected text to clipboard"""
        try:
            if hasattr(self.editor, 'text_widget'):
                self.editor.text_widget.event_generate("<<Cut>>")
            else:
                self.editor.event_generate("<<Cut>>")
            self.status_label.config(text="✂️ Text cut to clipboard.")
        except tk.TclError:
            self.status_label.config(text="✂️ No text selected to cut.")

    def _clear_all(self):
        """Clear all content from unified canvas"""
        self.unified_canvas._clear_screen()
        self.status_label.config(text="🧹 All content cleared.")

    def _stop_program(self):
        """Stop currently running program"""
        # For now, just show a message since we don't have background execution
        self.status_label.config(text="🛑 Stop program - not implemented yet.")

    def _restart_interpreter(self):
        """Restart the interpreter"""
        try:
            # Reinitialize the interpreter
            self.interpreter = Time_WarpInterpreter()
            # Reset unified canvas reference
            self.interpreter.ide_unified_canvas = self.unified_canvas

            # Create compatibility layer for interpreter
            class UnifiedCanvasOutputHandler:
                def __init__(self, unified_canvas):
                    self.unified_canvas = unified_canvas

                def insert(self, position, text):
                    # Convert text output to unified canvas text rendering
                    if position == "end" or position == tk.END:
                        self.unified_canvas.write_text(text)
                        # Force canvas update
                        self.unified_canvas.update_idletasks()
                    else:
                        # For other positions, just append for now
                        self.unified_canvas.write_text(text)
                        # Force canvas update
                        self.unified_canvas.update_idletasks()

                def see(self, position):
                    # Unified canvas doesn't need scrolling, but we can implement if needed
                    pass

            # Reset output widget reference for interpreter logging
            self.interpreter.output_widget = UnifiedCanvasOutputHandler(self.unified_canvas)

            # Reset turtle canvas reference (unified canvas acts as turtle canvas too)
            self.interpreter.ide_turtle_canvas = self.unified_canvas

            self.unified_canvas.write_text("Interpreter restarted successfully.\n")
            self.status_label.config(text="🔄 Interpreter restarted.")
        except Exception as e:
            self.unified_canvas.write_text(f"Failed to restart interpreter: {str(e)}\n")
            self.status_label.config(text=f"🔄 Failed to restart interpreter: {str(e)}")

    def _set_language(self, language):
        """Set the current programming language"""
        self.current_language = language
        self.status_label.config(text=f"💻 Language set to {language.upper()}")

    def _open_settings(self):
        """Open settings dialog"""
        messagebox.showinfo("Settings", "⚙️ Settings dialog not implemented yet.\n\nUse Theme Selector and Font Settings instead.")

    def _show_system_info(self):
        """Show system information"""
        import platform
        import sys
        
        info = f"""📊 System Information:

Operating System: {platform.system()} {platform.release()}
Platform: {platform.platform()}
Python Version: {sys.version.split()[0]}
Architecture: {platform.machine()}

Time_Warp IDE v1.3.0
Available Languages: Time Warp, Pascal, Prolog"""
        
        messagebox.showinfo("System Info", info)

    def _generate_report(self):
        """Generate a system report"""
        import datetime
        
        report = f"""Time_Warp IDE System Report
Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is a placeholder for system diagnostics.
Full reporting functionality to be implemented."""
        
        # Save to file
        try:
            with open("system_report.txt", "w") as f:
                f.write(report)
            messagebox.showinfo("Report Generated", "📋 System report saved to 'system_report.txt'")
        except Exception as e:
            messagebox.showerror("Report Error", f"❌ Could not save report: {str(e)}")

    def _open_online_resources(self):
        """Open online resources"""
        import webbrowser
        try:
            webbrowser.open("https://github.com/pygame/pygame")
            self.status_label.config(text="🌐 Opened online resources.")
        except Exception as e:
            messagebox.showerror("Browser Error", f"❌ Could not open browser: {str(e)}")

    def _report_issue(self):
        """Report an issue"""
        import webbrowser
        try:
            webbrowser.open("https://github.com/pygame/pygame/issues")
            self.status_label.config(text="🆘 Opened issue reporting page.")
        except Exception as e:
            messagebox.showerror("Browser Error", f"❌ Could not open browser: {str(e)}")

    def _feature_request(self):
        """Submit a feature request"""
        import webbrowser
        try:
            webbrowser.open("https://github.com/pygame/pygame/discussions")
            self.status_label.config(text="💡 Opened feature request page.")
        except Exception as e:
            messagebox.showerror("Browser Error", f"❌ Could not open browser: {str(e)}")

    def _check_updates(self):
        """Check for updates"""
        messagebox.showinfo("Updates", "🔄 Update checking not implemented yet.\n\nPlease check GitHub for the latest releases.")

    def run_program(self):
        """
        Execute the program currently in the text area.
        Note: In unified canvas mode, code editing is handled externally.
        This method assumes code is available through some means.
        """
        # For now, show a message that code execution needs to be handled differently
        # In a full implementation, we'd need a way to get code from an external editor
        self.unified_canvas.write_text("Program execution requires code input.\n")
        self.unified_canvas.write_text("Please implement code input mechanism.\n")
        self.status_label.config(text="❌ Code input not implemented in unified canvas mode.")

    def show_about(self):
        """Show about dialog"""
        about_text = """Time_Warp IDE v1.3.0

An educational programming environment supporting multiple languages:
• Time Warp: Unified educational language combining PILOT, BASIC, and Logo features
• Pascal: Structured programming with educational focus
• Prolog: Logic programming and AI concepts
• Forth: Stack-based programming fundamentals
• Perl: Text processing and scripting
• Python: Full Python scripting with turtle graphics support
• JavaScript: Web programming fundamentals

Features:
• Multi-language code execution
• Turtle graphics support for visual programming
• Plugin system for extensibility
• Theme customization with 10+ built-in themes
• Educational error messages and syntax checking
• Font customization and advanced editor features

© 2025 Time_Warp Development Team"""
        messagebox.showinfo("About Time_Warp IDE", about_text)

    def show_documentation(self):
        """Show documentation"""
        import webbrowser
        try:
            # Try to open local documentation
            doc_path = "docs/README.md"
            if os.path.exists(doc_path):
                webbrowser.open(f"file://{os.path.abspath(doc_path)}")
            else:
                # Fallback to online documentation or show message
                messagebox.showinfo("Documentation", "📚 Documentation is available in the 'docs/' folder.\n\nCheck README.md for usage instructions.")
        except Exception as e:
            messagebox.showerror("Documentation Error", f"Could not open documentation:\n\n{str(e)}")

    def toggle_output_panel(self):
        """In unified canvas mode, output is always visible"""
        self.unified_canvas.write_text("Output panel is integrated into unified canvas.\n")
        self.status_label.config(text="📊 Output is always visible in unified canvas mode")

    def toggle_turtle_graphics(self):
        """In unified canvas mode, graphics are always visible"""
        self.unified_canvas.write_text("Graphics are integrated into unified canvas.\n")
        self.status_label.config(text="🐢 Graphics are always visible in unified canvas mode")

    def switch_to_editor(self):
        """In unified canvas mode, editing is handled externally"""
        self.unified_canvas.write_text("Code editing is handled externally.\n")
        self.unified_canvas.write_text("Please use external editor for code input.\n")
        self.status_label.config(text="📝 Code editing is external in unified canvas mode")

    def open_plugin_manager(self):
        """Open the plugin manager dialog"""
        if self.plugin_manager and hasattr(self.plugin_manager, "list_available_plugins"):
            if not self.plugin_manager_dialog:
                from plugins import PluginManagerDialog
                self.plugin_manager_dialog = PluginManagerDialog(self, self.plugin_manager)
            self.plugin_manager_dialog.show()
        else:
            messagebox.showerror("Plugin Manager", "❌ Plugin system not available.")

    def open_theme_selector(self):
        """Open theme selector dialog"""
        themes = [
            # Dark Themes
            "Dracula", "Monokai", "Solarized Dark", "Ocean", "Gruvbox Dark", "Nord",
            "One Dark", "Tokyo Night", "Gotham", "Material Dark",
            # Light Themes
            "Spring", "Sunset", "Candy", "Forest", "Solarized Light", "Gruvbox Light",
            "One Light", "GitHub Light", "Material Light", "Minimal"
        ]

        dialog = tk.Toplevel(self.root)
        dialog.title("🎨 Select Theme")
        dialog.geometry("500x450")
        dialog.transient(self.root)

        tk.Label(dialog, text="Choose a theme:", font=("Arial", 12, "bold")).pack(pady=10)

        # Create scrollable frame for themes
        canvas = tk.Canvas(dialog)
        scrollbar = tk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create buttons for each theme (3 columns)
        for i, theme in enumerate(themes):
            row = i // 3
            col = i % 3
            btn = tk.Button(
                scrollable_frame,
                text=theme,
                command=lambda t=theme: self._apply_theme_from_selector(t, dialog),
                font=("Arial", 10),
                width=15,
                height=2
            )
            btn.grid(row=row, column=col, padx=5, pady=5)

        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y")

        # Current theme indicator
        tk.Label(dialog, text=f"Current: {self.selected_theme}", font=("Arial", 10, "italic")).pack(pady=5)

        # Font selection button
        tk.Button(dialog, text="⚙️ Font Settings", command=lambda: self._open_font_settings(dialog),
                 font=("Arial", 11)).pack(pady=5)

        tk.Button(dialog, text="Close", command=dialog.destroy, font=("Arial", 11)).pack(pady=10)

    def _open_font_settings(self, parent_dialog):
        """Open font settings dialog"""
        font_dialog = tk.Toplevel(self.root)
        font_dialog.title("⚙️ Font Settings")
        font_dialog.geometry("400x300")
        # Use parent_dialog if provided, otherwise use root
        font_dialog.transient(parent_dialog if parent_dialog else self.root)

        tk.Label(font_dialog, text="Font Settings", font=("Arial", 14, "bold")).pack(pady=10)

        # Font family selection
        family_frame = tk.Frame(font_dialog)
        family_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(family_frame, text="Font Family:", font=("Arial", 11)).pack(anchor="w")
        self.font_family_var = tk.StringVar(value=self.selected_font_family)

        # Common monospace fonts
        font_families = ["Consolas", "Courier New", "Monaco", "Menlo", "DejaVu Sans Mono",
                        "Liberation Mono", "Source Code Pro", "Fira Code", "JetBrains Mono",
                        "Cascadia Code", "Roboto Mono", "Space Mono", "Ubuntu Mono"]

        family_combo = ttk.Combobox(family_frame, textvariable=self.font_family_var,
                                   values=font_families, state="readonly", width=25)
        family_combo.pack(pady=5)
        family_combo.bind("<<ComboboxSelected>>", self._preview_font)

        # Font size selection
        size_frame = tk.Frame(font_dialog)
        size_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(size_frame, text="Font Size:", font=("Arial", 11)).pack(anchor="w")
        self.font_size_var = tk.IntVar(value=self.selected_font_size)

        size_combo = ttk.Combobox(size_frame, textvariable=self.font_size_var,
                                 values=list(range(8, 25)), state="readonly", width=25)
        size_combo.pack(pady=5)
        size_combo.bind("<<ComboboxSelected>>", self._preview_font)

        # Preview area
        preview_frame = tk.Frame(font_dialog, relief="sunken", bd=1)
        preview_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(preview_frame, text="Preview:", font=("Arial", 10, "bold")).pack(anchor="w", padx=5, pady=2)
        self.font_preview = tk.Text(preview_frame, height=3, wrap="word", font=(self.selected_font_family, self.selected_font_size))
        self.font_preview.pack(fill="x", padx=5, pady=5)
        self.font_preview.insert("1.0", "The quick brown fox jumps over the lazy dog\n1234567890\nprint('Hello, World!')")
        self.font_preview.config(state="disabled")

        # Buttons
        button_frame = tk.Frame(font_dialog)
        button_frame.pack(fill="x", padx=20, pady=10)

        tk.Button(button_frame, text="Apply & Save", command=lambda: self._apply_font_settings(font_dialog),
                 font=("Arial", 11)).pack(side="left", padx=5)
        tk.Button(button_frame, text="Cancel", command=font_dialog.destroy,
                 font=("Arial", 11)).pack(side="right", padx=5)

    def _compile_to_executable(self):
        """Compile the current program to a standalone executable"""
        if not COMPILER_AVAILABLE or not self.compiler:
            messagebox.showerror("Compiler Unavailable", "❌ Compiler system is not available.\n\nPlease ensure the compiler module is properly installed.")
            return

        # Get code from editor
        if hasattr(self.editor, 'text_widget'):
            code = self.editor.text_widget.get("1.0", tk.END).strip()
        else:
            code = self.editor.get("1.0", tk.END).strip()

        if not code:
            messagebox.showwarning("No Code", "❌ Please enter a program to compile.\n\nThe code editor is empty.")
            return

        # Detect language
        language = self._detect_language_from_code(code)

        # Create compilation dialog
        compile_dialog = tk.Toplevel(self.root)
        compile_dialog.title("📦 Compile to Executable")
        compile_dialog.geometry("500x400")
        compile_dialog.transient(self.root)
        compile_dialog.grab_set()

        tk.Label(compile_dialog, text="Compile Program to Executable", font=("Arial", 16, "bold")).pack(pady=10)

        # Language info
        info_frame = tk.Frame(compile_dialog)
        info_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(info_frame, text=f"Detected Language: {language.upper()}", font=("Arial", 11, "bold")).pack(anchor="w")
        tk.Label(info_frame, text=f"Code Length: {len(code)} characters", font=("Arial", 10)).pack(anchor="w")

        # Output options
        output_frame = tk.Frame(compile_dialog)
        output_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(output_frame, text="Output Options:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))

        # Output filename
        name_frame = tk.Frame(output_frame)
        name_frame.pack(fill="x", pady=2)
        tk.Label(name_frame, text="Executable Name:", font=("Arial", 10)).pack(side="left")
        output_name_var = tk.StringVar(value=f"program_{language}")
        tk.Entry(name_frame, textvariable=output_name_var, width=30).pack(side="right")

        # Output directory
        dir_frame = tk.Frame(output_frame)
        dir_frame.pack(fill="x", pady=2)
        tk.Label(dir_frame, text="Output Directory:", font=("Arial", 10)).pack(side="left")
        output_dir_var = tk.StringVar(value=os.getcwd())
        tk.Entry(dir_frame, textvariable=output_dir_var, width=30).pack(side="right")

        # Browse button for directory
        def browse_directory():
            from tkinter import filedialog
            directory = filedialog.askdirectory(initialdir=output_dir_var.get())
            if directory:
                output_dir_var.set(directory)

        tk.Button(dir_frame, text="Browse...", command=browse_directory).pack(side="right", padx=(5, 0))

        # Compiler backend selection
        backend_frame = tk.Frame(compile_dialog)
        backend_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(backend_frame, text="Compiler Backend:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))

        backend_var = tk.StringVar(value="auto")
        backends = [("Auto (Recommended)", "auto")]
        if hasattr(self.compiler, 'get_available_backends'):
            available_backends = self.compiler.get_available_backends()
            backends.extend([(f"{b.title()} Compiler", b) for b in available_backends])

        for text, value in backends:
            tk.Radiobutton(backend_frame, text=text, variable=backend_var, value=value).pack(anchor="w")

        # Progress and status
        progress_frame = tk.Frame(compile_dialog)
        progress_frame.pack(fill="x", padx=20, pady=10)

        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_frame, variable=progress_var, maximum=100)
        progress_bar.pack(fill="x", pady=5)

        status_label = tk.Label(progress_frame, text="Ready to compile...", font=("Arial", 10))
        status_label.pack(anchor="w")

        # Buttons
        button_frame = tk.Frame(compile_dialog)
        button_frame.pack(fill="x", padx=20, pady=10)

        def start_compilation():
            """Start the compilation process"""
            output_name = output_name_var.get().strip()
            output_dir = output_dir_var.get().strip()
            backend = backend_var.get()

            if not output_name:
                messagebox.showerror("Invalid Name", "❌ Please enter a valid executable name.")
                return

            if not output_dir or not os.path.isdir(output_dir):
                messagebox.showerror("Invalid Directory", "❌ Please select a valid output directory.")
                return

            # Create output path
            output_path = os.path.join(output_dir, output_name)

            # Disable buttons during compilation
            compile_btn.config(state="disabled")
            cancel_btn.config(text="Close")

            try:
                status_label.config(text="🔄 Initializing compilation...")
                progress_var.set(10)

                status_label.config(text="📦 Compiling executable...")
                progress_var.set(30)

                # Perform compilation
                result = self.compiler.compile_to_executable(code, language, output_path)

                progress_var.set(80)

                if result['success']:
                    status_label.config(text="✅ Compilation completed successfully!")
                    progress_var.set(100)

                    # Show success message with details
                    executable_path = result.get('executable', output_path)
                    size = result.get('size', 0)
                    compiler_used = result.get('compiler', 'Unknown')

                    messagebox.showinfo("Compilation Successful",
                                      f"✅ Executable compiled successfully!\n\n"
                                      f"📁 Location: {executable_path}\n"
                                      f"💻 Language: {language.upper()}\n"
                                      f"🛠️ Compiler: {compiler_used}\n"
                                      f"📏 Size: {size} bytes\n\n"
                                      f"You can run it anytime with: ./{os.path.basename(executable_path)}\n"
                                      f"Or choose 'Yes' below to run it now and see the output in the IDE.")

                    # Ask if user wants to run the executable
                    if messagebox.askyesno("Run Executable", "Would you like to run the compiled executable now?\n\nThe output will be displayed in the IDE's Output panel."):
                        try:
                            import subprocess
                            # Run the executable and capture output
                            result = subprocess.run(
                                [executable_path],
                                cwd=output_dir,
                                capture_output=True,
                                text=True,
                                timeout=30  # 30 second timeout
                            )

                            # Display output in unified canvas
                            output_text = f"🚀 Executable Output ({language.upper()}):\n\n"
                            output_text += result.stdout
                            if result.stderr:
                                output_text += f"\n❌ Errors:\n{result.stderr}"
                            output_text += f"\n✅ Exit code: {result.returncode}"
                            self.unified_canvas.write_text(output_text)

                            status_label.config(text="🚀 Executable completed!")
                        except subprocess.TimeoutExpired:
                            messagebox.showerror("Timeout", "❌ Executable timed out after 30 seconds.")
                            status_label.config(text="⏰ Executable timed out.")
                        except Exception as e:
                            messagebox.showerror("Launch Error", f"❌ Could not launch executable: {str(e)}")
                            status_label.config(text="❌ Launch failed.")

                else:
                    status_label.config(text="❌ Compilation failed.")
                    progress_var.set(0)
                    error_msg = result.get('error', 'Unknown error occurred')
                    details = result.get('details', '')
                    messagebox.showerror("Compilation Failed", f"❌ Compilation failed:\n\n{error_msg}\n\n{details}")

            except Exception as e:
                status_label.config(text="❌ Compilation error.")
                progress_var.set(0)
                messagebox.showerror("Compilation Error", f"❌ An error occurred during compilation:\n\n{str(e)}")

            finally:
                compile_btn.config(state="normal")
                cancel_btn.config(text="Cancel")

        def cancel_compilation():
            """Cancel compilation or close dialog"""
            if compile_btn.cget("state") == "disabled":
                # Compilation in progress, can't cancel easily
                if messagebox.askyesno("Cancel Compilation", "Compilation is in progress. Are you sure you want to cancel?"):
                    compile_dialog.destroy()
            else:
                compile_dialog.destroy()

        compile_btn = tk.Button(button_frame, text="📦 Compile", command=start_compilation,
                               font=("Arial", 11, "bold"), bg="#4CAF50", fg="white")
        compile_btn.pack(side="left", padx=5)

        cancel_btn = tk.Button(button_frame, text="Cancel", command=cancel_compilation, font=("Arial", 11))
        cancel_btn.pack(side="right", padx=5)

    def _preview_font(self, event=None):
        """Preview font changes"""
        try:
            family = self.font_family_var.get()
            size = self.font_size_var.get()
            self.font_preview.config(font=(family, size))
        except:
            pass

    def _apply_font_settings(self, dialog):
        """Apply font settings"""
        self.selected_font_family = self.font_family_var.get()
        self.selected_font_size = self.font_size_var.get()
        self._apply_font_to_ui()
        self._save_font_config()
        self.status_label.config(text=f"⚙️ Font '{self.selected_font_family}' ({self.selected_font_size}pt) applied.")
        dialog.destroy()

    def _apply_font_to_ui(self):
        """Apply selected font to all UI elements"""
        # Update unified canvas font
        if hasattr(self, 'unified_canvas'):
            self.unified_canvas.set_font(self.selected_font_family, self.selected_font_size)

        # Update editor fonts
        if hasattr(self.editor, 'text_widget'):
            # Enhanced editor
            self.editor.text_widget.config(font=(self.selected_font_family, self.selected_font_size))
        else:
            # Basic editor
            self.editor.config(font=(self.selected_font_family, self.selected_font_size))

        # Update line numbers font (if enhanced editor)
        if hasattr(self.editor, 'line_numbers'):
            self.editor.line_numbers.config(font=(self.selected_font_family, self.selected_font_size - 2))

    def _save_font_config(self):
        """Save font configuration"""
        config = {
            "font_family": self.selected_font_family,
            "font_size": self.selected_font_size
        }
        try:
            import json
            import os
            config_dir = os.path.expanduser("~/.Time_Warp")
            os.makedirs(config_dir, exist_ok=True)
            with open(os.path.join(config_dir, "font_config.json"), "w") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save font config: {e}")

    def _load_font_config(self):
        """Load font configuration"""
        try:
            import json
            import os
            config_file = os.path.expanduser("~/.Time_Warp/font_config.json")
            if os.path.exists(config_file):
                with open(config_file, "r") as f:
                    config = json.load(f)
                self.selected_font_family = config.get("font_family", "Consolas")
                self.selected_font_size = config.get("font_size", 11)
        except Exception as e:
            print(f"Warning: Could not load font config: {e}")

    def _apply_theme_from_selector(self, theme_name, dialog):
        """Apply theme from selector and close dialog"""
        self.selected_theme = theme_name
        self._save_theme_config(theme_name)
        self._apply_theme_stub(theme_name)
        self.status_label.config(text=f"🎨 Theme '{theme_name}' applied.")
        dialog.destroy()

    def _apply_theme_stub(self, theme_name):
        """Apply theme colors to UI elements for unified canvas interface"""
        # Comprehensive theme collection
        theme_colors = {
            # Dark Themes
            "Dracula": {"bg": "#282a36", "fg": "#f8f8f2", "panel_bg": "#44475a", "panel_fg": "#f8f8f2", "accent": "#bd93f9"},
            "Monokai": {"bg": "#272822", "fg": "#f8f8f2", "panel_bg": "#49483e", "panel_fg": "#f8f8f2", "accent": "#fd971f"},
            "Solarized Dark": {"bg": "#002b36", "fg": "#839496", "panel_bg": "#073642", "panel_fg": "#93a1a1", "accent": "#268bd2"},
            "Ocean": {"bg": "#223447", "fg": "#c3eaff", "panel_bg": "#2a415d", "panel_fg": "#c3eaff", "accent": "#4fc3f7"},
            "Gruvbox Dark": {"bg": "#282828", "fg": "#ebdbb2", "panel_bg": "#3c3836", "panel_fg": "#ebdbb2", "accent": "#fabd2f"},
            "Nord": {"bg": "#2e3440", "fg": "#d8dee9", "panel_bg": "#3b4252", "panel_fg": "#d8dee9", "accent": "#88c0d0"},
            "One Dark": {"bg": "#282c34", "fg": "#abb2bf", "panel_bg": "#21252b", "panel_fg": "#abb2bf", "accent": "#61afef"},
            "Tokyo Night": {"bg": "#1a1b26", "fg": "#c0caf5", "panel_bg": "#16161e", "panel_fg": "#c0caf5", "accent": "#bb9af7"},
            "Gotham": {"bg": "#0a0f14", "fg": "#98d1ce", "panel_bg": "#0a0f14", "panel_fg": "#98d1ce", "accent": "#d26937"},
            "Material Dark": {"bg": "#263238", "fg": "#eeffff", "panel_bg": "#37474f", "panel_fg": "#eeffff", "accent": "#00bcd4"},

            # Light Themes
            "Spring": {"bg": "#f0fff0", "fg": "#228b22", "panel_bg": "#e0ffe0", "panel_fg": "#228b22", "accent": "#32cd32"},
            "Sunset": {"bg": "#fff5e6", "fg": "#ff4500", "panel_bg": "#ffe4b5", "panel_fg": "#ff4500", "accent": "#ff6347"},
            "Candy": {"bg": "#fff0fa", "fg": "#d72660", "panel_bg": "#ffe0f7", "panel_fg": "#d72660", "accent": "#ff69b4"},
            "Forest": {"bg": "#e6ffe6", "fg": "#006400", "panel_bg": "#cceccc", "panel_fg": "#006400", "accent": "#228b22"},
            "Solarized Light": {"bg": "#fdf6e3", "fg": "#586e75", "panel_bg": "#eee8d5", "panel_fg": "#586e75", "accent": "#268bd2"},
            "Gruvbox Light": {"bg": "#fbf1c7", "fg": "#3c3836", "panel_bg": "#ebdbb2", "panel_fg": "#3c3836", "accent": "#d79921"},
            "One Light": {"bg": "#fafafa", "fg": "#383a42", "panel_bg": "#f0f0f0", "panel_fg": "#383a42", "accent": "#4078f2"},
            "GitHub Light": {"bg": "#ffffff", "fg": "#24292f", "panel_bg": "#f6f8fa", "panel_fg": "#24292f", "accent": "#0969da"},
            "Material Light": {"bg": "#fafafa", "fg": "#212121", "panel_bg": "#ffffff", "panel_fg": "#212121", "accent": "#1976d2"},
            "Minimal": {"bg": "#ffffff", "fg": "#000000", "panel_bg": "#f5f5f5", "panel_fg": "#000000", "accent": "#666666"},
        }

        colors = theme_colors.get(theme_name, theme_colors["Dracula"])

        # Apply theme to main window and frames
        self.root.config(bg=colors["bg"])
        self.main_frame.config(bg=colors["bg"])

        # Apply theme to unified canvas
        # Note: UnifiedCanvas handles its own theming based on screen mode

        # Apply theme to status bar
        self.status_label.config(bg=colors["panel_bg"], fg=colors["panel_fg"])

        # Update menu colors (limited Tkinter support)
        try:
            self.menubar.config(bg=colors["panel_bg"], fg=colors["panel_fg"])
        except:
            pass

        # Force UI update
        self.root.update_idletasks()

    def _save_theme_config(self, theme_name):
        """Save theme configuration to file"""
        try:
            config_dir = os.path.expanduser("~/.Time_Warp")
            os.makedirs(config_dir, exist_ok=True)
            config_file = os.path.join(config_dir, "config.json")
            config = {}
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
            config['theme'] = theme_name
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            # Silently fail if we can't save config
            pass

    def _load_theme_config(self):
        """Load theme configuration from file"""
        try:
            config_file = os.path.expanduser("~/.Time_Warp/config.json")
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    content = f.read().strip()
                    if content:  # Only parse if file is not empty
                        config = json.loads(content)
                        saved_theme = config.get('theme', 'Dracula')
                        if saved_theme in ["Dracula", "Monokai", "Solarized Dark", "Ocean", "Spring", "Sunset", "Candy", "Forest"]:
                            self.selected_theme = saved_theme
        except Exception as e:
            # Silently fail if we can't load config, use default
            pass

    def run_tests(self):
        """Run test suite and display results in unified canvas"""
        import subprocess
        import sys
        try:
            result = subprocess.run([sys.executable, "scripts/run_tests.py"], capture_output=True, text=True)
            output = result.stdout + "\n" + result.stderr
            # Show in unified canvas
            self.unified_canvas.write_text("🧪 Test Results:\n\n" + output)
            # Also show summary in messagebox
            messagebox.showinfo("Test Results", f"🧪 Test run complete:\n\n{output[:1000]}")
        except Exception as e:
            self.unified_canvas.write_text(f"❌ Could not run tests:\n\n{str(e)}")
            messagebox.showerror("Test Error", f"❌ Could not run tests:\n\n{str(e)}")

    def on_closing(self):
        """Handle window close event."""
        try:
            # Check if the root window still exists before showing dialog
            if self.root.winfo_exists():
                if messagebox.askokcancel("Quit", "Do you want to quit Time_Warp IDE?"):
                    self.root.destroy()
            else:
                # Window already destroyed, just exit
                self.root.destroy()
        except tk.TclError:
            # Application is already being destroyed, just exit
            pass

    def _create_ui(self):
        print("[DEBUG] Entered TimeWarpApp._create_ui")
        # Create menu bar
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        # === FILE MENU === 📁
        file_menu = tk.Menu(self.menubar, tearoff=0)
        file_menu.add_command(label="📄 New File", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="📂 Open File...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="💾 Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="💾 Save As...", command=self.save_file_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="🚪 Exit", command=self.on_closing, accelerator="Ctrl+Q")
        self.menubar.add_cascade(label="📁 File", menu=file_menu)

        # === EDIT MENU === ✏️
        edit_menu = tk.Menu(self.menubar, tearoff=0)
        edit_menu.add_command(label="↩️ Undo", command=self._undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="↪️ Redo", command=self._redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="✂️ Cut", command=self._cut_text, accelerator="Ctrl+X")
        edit_menu.add_command(label="📋 Copy", command=self._copy_text, accelerator="Ctrl+C")
        edit_menu.add_command(label="📄 Paste", command=self._paste_text, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="🔍 Find/Replace...", command=self._open_find_replace, accelerator="Ctrl+F")
        edit_menu.add_command(label="🔍 Find Next", command=self._find_next, accelerator="F3")
        edit_menu.add_separator()
        edit_menu.add_command(label="💬 Toggle Comment", command=self._toggle_comment, accelerator="Ctrl+/")
        edit_menu.add_command(label="⬅️ Decrease Indent", command=self._decrease_indent, accelerator="Shift+Tab")
        edit_menu.add_command(label="➡️ Increase Indent", command=self._increase_indent, accelerator="Tab")
        self.menubar.add_cascade(label="✏️ Edit", menu=edit_menu)

        # === VIEW MENU === 👁️
        view_menu = tk.Menu(self.menubar, tearoff=0)
        view_menu.add_command(label="🔢 Toggle Line Numbers", command=self._toggle_line_numbers)
        view_menu.add_separator()
        view_menu.add_command(label="🧹 Clear All", command=self._clear_all)
        view_menu.add_command(label="📝 Clear Code Editor", command=self.clear_editor)
        view_menu.add_command(label="📊 Clear Output", command=self.clear_output)
        view_menu.add_command(label="🐢 Clear Turtle Graphics", command=self.clear_turtle)
        view_menu.add_separator()
        view_menu.add_command(label="📝 Switch to Code Editor", command=self.switch_to_editor)
        view_menu.add_command(label="📊 Switch to Output", command=self.toggle_output_panel)
        view_menu.add_command(label="🐢 Switch to Turtle Graphics", command=self.toggle_turtle_graphics)
        self.menubar.add_cascade(label="👁️ View", menu=view_menu)

        # === RUN MENU === ▶️
        run_menu = tk.Menu(self.menubar, tearoff=0)
        run_menu.add_command(label="🚀 Run Program", command=self.run_program, accelerator="F5")
        run_menu.add_command(label="🛑 Stop Program", command=self._stop_program, accelerator="Ctrl+Break")
        run_menu.add_separator()
        run_menu.add_command(label="🧪 Run Tests", command=self.run_tests)
        run_menu.add_command(label="📝 Check Syntax", command=self._check_syntax, accelerator="F7")
        run_menu.add_separator()
        run_menu.add_command(label="🔄 Restart Interpreter", command=self._restart_interpreter)
        self.menubar.add_cascade(label="▶️ Run", menu=run_menu)

        # === LANGUAGE MENU === 💻
        lang_menu = tk.Menu(self.menubar, tearoff=0)
        lang_menu.add_command(label="⏰ Time Warp", command=lambda: self._set_language("time_warp"))
        lang_menu.add_command(label=" Pascal", command=lambda: self._set_language("pascal"))
        lang_menu.add_command(label="🧠 Prolog", command=lambda: self._set_language("prolog"))
        lang_menu.add_separator()
        lang_menu.add_command(label="🔍 Auto-Detect", command=lambda: self._set_language("auto"))
        self.menubar.add_cascade(label="💻 Language", menu=lang_menu)

        # === TOOLS MENU === 🛠️
        tools_menu = tk.Menu(self.menubar, tearoff=0)
        tools_menu.add_command(label="🎨 Theme Selector...", command=self.open_theme_selector)
        tools_menu.add_command(label="🔤 Font Settings...", command=lambda: self._open_font_settings(None))
        tools_menu.add_separator()
        if COMPILER_AVAILABLE and self.compiler:
            tools_menu.add_command(label="📦 Compile to Executable...", command=self._compile_to_executable, accelerator="Ctrl+Shift+E")
            tools_menu.add_separator()
        tools_menu.add_command(label="📦 Plugin Manager", command=self.open_plugin_manager)
        tools_menu.add_command(label="⚙️ Settings...", command=self._open_settings)
        tools_menu.add_separator()

        # Developer Tools submenu
        dev_tools_menu = tk.Menu(tools_menu, tearoff=0)
        dev_tools_menu.add_command(label="📊 System Info", command=self._show_system_info)
        dev_tools_menu.add_command(label="🧪 Test Suite", command=self.run_tests)
        dev_tools_menu.add_command(label="📋 Generate Report", command=self._generate_report)
        tools_menu.add_cascade(label="🔧 Developer Tools", menu=dev_tools_menu)

        self.menubar.add_cascade(label="🛠️ Tools", menu=tools_menu)

        # === HELP MENU === ❓
        help_menu = tk.Menu(self.menubar, tearoff=0)
        help_menu.add_command(label="ℹ️ About Time_Warp IDE", command=self.show_about)
        help_menu.add_command(label="📚 Documentation", command=self.show_documentation)
        help_menu.add_command(label="🌐 Online Resources", command=self._open_online_resources)
        help_menu.add_separator()
        help_menu.add_command(label="🆘 Report Issue", command=self._report_issue)
        help_menu.add_command(label="💡 Feature Request", command=self._feature_request)
        help_menu.add_separator()
        help_menu.add_command(label="🔄 Check for Updates", command=self._check_updates)
        self.menubar.add_cascade(label="❓ Help", menu=help_menu)


        # --- Unified Canvas Layout ---
        # Main frame for padding and layout
        self.main_frame = tk.Frame(self.root, bg="black")
        self.main_frame.pack(expand=True, fill="both")

        # Create unified canvas instead of tabbed interface - fill entire window
        self.unified_canvas = UnifiedCanvas(self.main_frame, bg="black", relief="flat", bd=0,
                                          font_family=self.selected_font_family,
                                          font_size=self.selected_font_size)
        self.unified_canvas.pack(expand=True, fill="both", padx=0, pady=0)

        # Make sure the main frame and root allow resizing
        self.root.resizable(True, True)
        self.main_frame.pack_propagate(False)  # Don't shrink to fit contents

        # Set unified canvas reference for interpreter
        self.interpreter.ide_unified_canvas = self.unified_canvas

        # Create compatibility layer for interpreter
        class UnifiedCanvasOutputHandler:
            def __init__(self, unified_canvas):
                self.unified_canvas = unified_canvas

            def insert(self, position, text):
                # Convert text output to unified canvas text rendering
                # Command output should always start on a new line by default
                if position == "end" or position == tk.END:
                    # Always start command output on a new line
                    self.unified_canvas.write_text("\n")
                    self.unified_canvas.write_text(text)
                    # Force canvas update
                    self.unified_canvas.update_idletasks()
                else:
                    # For other positions, just append for now
                    self.unified_canvas.write_text(text)
                    # Force canvas update
                    self.unified_canvas.update_idletasks()

            def see(self, position):
                # Unified canvas doesn't need scrolling, but we can implement if needed
                pass

            def request_input(self, prompt, input_type=str):
                """Show input prompt in unified canvas and enable input handling."""
                def input_callback(input_value):
                    try:
                        typed_value = input_type(input_value)
                        # Display the input value
                        self.unified_canvas.write_text(f"{typed_value}\n", color=7)
                        # Send input to interpreter
                        if hasattr(self, "_input_callback") and self._input_callback:
                            self._input_callback(typed_value)
                    except ValueError:
                        # Invalid input type, reprompt
                        self.unified_canvas.write_text(f"\n❌ Invalid input type. Expected {input_type.__name__}.\n", color=4)
                        self.unified_canvas.prompt_input(prompt, lambda val: self._handle_input_callback(val, input_type))

                self.unified_canvas.prompt_input(prompt, input_callback)

            def _handle_input_callback(self, input_value, input_type):
                """Handle input callback with type conversion"""
                try:
                    typed_value = input_type(input_value)
                    self.unified_canvas.write_text(f"{typed_value}\n", color=7)
                    if hasattr(self, "_input_callback") and self._input_callback:
                        self._input_callback(typed_value)
                except ValueError:
                    self.unified_canvas.write_text(f"\n❌ Invalid input type. Expected {input_type.__name__}.\n", color=4)
                    # Reprompt would go here if needed

        # Set output widget reference for interpreter logging
        self.interpreter.output_widget = UnifiedCanvasOutputHandler(self.unified_canvas)

        # Set turtle canvas reference (unified canvas acts as turtle canvas too)
        self.interpreter.ide_turtle_canvas = self.unified_canvas

        # Initialize the welcome screen
        # self._show_welcome_screen()  # Moved to after mainloop starts

        # Apply initial theme (but don't override the black background for welcome screen)
        # self._apply_theme_stub(self.selected_theme)

        # Track when to show OK prompt
        self.show_ok_prompt = True  # Show OK on initial run

        # Schedule welcome screen to show after GUI is fully initialized
        self.root.after(100, self._show_welcome_screen)

    def _show_welcome_screen(self):
        """Display the welcome screen with introduction text, memory info, and OK prompt"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            free_memory_kb = memory.available // 1024
            free_memory_mb = free_memory_kb // 1024
            memory_info = f"Free Memory: {free_memory_mb} MB ({free_memory_kb} KB)"
        except ImportError:
            memory_info = "Memory info unavailable (psutil not installed)"

        import platform

        # Clear canvas and set to unified mode
        self.unified_canvas._clear_screen()

        # Display welcome text
        welcome_text = f"""
Time_Warp IDE v1.3.0 - Educational Programming Environment
{platform.system()} {platform.release()} - {platform.machine()}

Supports: Time Warp, Pascal, Prolog

{memory_info}

Type HELP for commands, or start programming!

OK
"""

        self.unified_canvas.write_text(welcome_text, color=15)  # White text

        # Start input prompt
        self._start_command_input()

    def _start_command_input(self):
        """Start the command input loop"""
        def command_callback(command):
            """Handle user commands"""
            command = command.strip()
            if command:
                # Execute command without echoing it
                command_upper = command.upper()
                if command_upper == "HELP":
                    self._show_help()
                elif command_upper in ["CLS", "CLEAR"]:
                    self.unified_canvas._clear_screen()
                    # Reset cursor position after clearing
                    self.unified_canvas.cursor_x = 0
                    self.unified_canvas.cursor_y = 0
                    # Show OK prompt after CLS
                    self.show_ok_prompt = True
                elif command_upper in ["EXIT", "QUIT", "BYE"]:
                    self.on_closing()
                    return
                else:
                    # Try to execute as code
                    self._execute_command(command)

            # Schedule next prompt after canvas updates
            self.root.after(100, lambda: self._show_next_prompt(command_callback))

        # Start the input loop (cursor should already be positioned after welcome OK)
        self.unified_canvas.prompt_input("", command_callback)

    def _show_next_prompt(self, callback):
        """Show the next OK prompt and restart input"""
        if self.show_ok_prompt:
            self.unified_canvas.write_text("OK\n", color=15)
            self.show_ok_prompt = False  # Reset flag
        # Note: cursor positioning is now handled by prompt_input method
        self.unified_canvas.prompt_input("", callback)

    def _show_help(self):
        """Show help information"""
        help_text = """
Available Commands:
  HELP     - Show this help
  CLS      - Clear screen
  EXIT     - Quit the IDE

File Operations:
  Use File menu to Load/Save programs
  Line-numbered programs are stored in memory
  RUN executes stored program
  LIST shows stored program
  NEW clears stored program

Languages: Time_Warp programming language

Examples:
  PRINT "Hello, World!"
  10 PRINT "BASIC LINE"
  FORWARD 100
  T:Hello World!
  ? "Hello"  (shortcut for PRINT)

OK
"""
        self.unified_canvas.write_text(help_text, color=15)

    def _execute_command(self, command):
        """Execute a programming command"""
        try:
            # Handle special commands first
            command_upper = command.strip().upper()
            
            if command_upper == "RUN":
                # Execute the stored program
                if self.interpreter.program_lines:
                    program_text = "\n".join([f"{line_num} {cmd}" for line_num, cmd in self.interpreter.program_lines])
                    result = self.interpreter.run_program(program_text, language='time_warp', show_completion=True)
                    return
                else:
                    self.unified_canvas.write_text("No program loaded. Enter line-numbered commands first.\n", color=14)
                    return
            elif command_upper == "LIST":
                # List the stored program
                if self.interpreter.program_lines:
                    # Clear screen for listing
                    self.unified_canvas._clear_screen()
                    self.unified_canvas.write_text("Program:\n", color=15)
                    for line_num, cmd in self.interpreter.program_lines:
                        self.unified_canvas.write_text(f"{line_num} {cmd}\n", color=15)
                else:
                    self.unified_canvas.write_text("No program loaded.\n", color=14)
                return
            elif command_upper.startswith("NEW"):
                # Clear the stored program
                self.interpreter.program_lines = []
                self.unified_canvas.write_text("Program cleared.\n", color=15)
                return

            # Check if this is a line-numbered program line BEFORE language detection
            command_stripped = command.strip()
            if command_stripped and command_stripped[0].isdigit():
                # This is a program line with line number - store it, don't execute
                try:
                    # Parse line number and command
                    parts = command_stripped.split(None, 1)  # Split on first whitespace
                    line_num = int(parts[0])
                    cmd = parts[1] if len(parts) > 1 else ""
                    
                    if cmd:  # Must have a command after the line number
                        # Update or add the line
                        existing_index = None
                        for i, (existing_num, _) in enumerate(self.interpreter.program_lines):
                            if existing_num == line_num:
                                existing_index = i
                                break

                        if existing_index is not None:
                            self.interpreter.program_lines[existing_index] = (line_num, cmd)
                        else:
                            # Insert in line number order
                            insert_pos = 0
                            for i, (existing_num, _) in enumerate(self.interpreter.program_lines):
                                if existing_num > line_num:
                                    break
                                insert_pos = i + 1
                            self.interpreter.program_lines.insert(insert_pos, (line_num, cmd))

                        # Line stored silently - no message needed
                        return
                    else:
                        # Invalid line number format - no command after line number
                        self.unified_canvas.write_text("Invalid line number format - missing command.\n", color=12)
                        return
                except (ValueError, IndexError):
                    # Invalid line number format
                    self.unified_canvas.write_text("Invalid line number format.\n", color=12)
                    return

            # Execute as Time_Warp command
            result = self.interpreter.time_warp_executor.execute_command(command)
        except Exception as e:
            self.unified_canvas.write_text(f"Error: {str(e)}\n", color=12)

    def _check_syntax(self):
        """Check syntax of code - requires external code input in unified canvas mode"""
        self.unified_canvas.write_text("Syntax check requires code input.\n")
        self.unified_canvas.write_text("Please implement code input mechanism.\n")
        # Update status label if it exists (for compatibility)
        if hasattr(self, 'status_label') and self.status_label:
            self.status_label.config(text="❌ Syntax check not available in unified canvas mode.")

    def _detect_language_from_code(self, code):
        """Detect programming language from code content"""
        lines = code.strip().split('\n')
        if not lines:
            return 'pilot'

        # Get first 10 lines for analysis
        first_lines = '\n'.join(lines[:10]).lower()
        all_code = code.lower()

        # Check file extension first if we have a current file
        if hasattr(self, 'current_file') and self.current_file:
            import os
            _, ext = os.path.splitext(self.current_file.lower())
            ext_map = {
                '.pas': 'pascal',
                '.plg': 'prolog',
                '.logo': 'logo',
                '.bas': 'basic',
                '.pilot': 'pilot',
                '.tw': 'time_warp'
            }
            if ext in ext_map:
                return ext_map[ext]

        # Time_Warp detection - check for unified language patterns FIRST to avoid conflicts
        # with established language syntax
        time_warp_commands = [
            "FORWARD", "BACK", "LEFT", "RIGHT", "PENUP", "PENDOWN", "CLEARSCREEN", "HOME",
            "SETXY", "SETCOLOR", "SETPENSIZE", "CIRCLE", "DOT", "RECT", "TEXT",
            "SHOWTURTLE", "HIDETURTLE", "REPEAT", "DEFINE", "CALL", "SIN", "COS", "TAN",
            "SQRT", "ABS", "INT", "RND", "LEN", "MID", "LEFT", "RIGHT", "UPPER", "LOWER",
            "SORT", "FIND", "SUM", "AVG", "MIN", "MAX", "LINE", "BOX", "TRIANGLE", "ELLIPSE",
            "FILL", "BEEP", "PLAY", "SOUND", "NOTE", "PLAYNOTE", "SETSOUND", "OPEN", "CLOSE",
            "READ", "WRITE", "EOF", "LET", "PRINT", "INPUT", "GOTO", "IF", "THEN", "FOR", "TO", "NEXT"
        ]

        # Check for single immediate commands first (PRINT, INPUT, LET, variable assignments)
        immediate_commands = ["PRINT", "INPUT", "LET"]
        for cmd in immediate_commands:
            if re.search(r'\b' + re.escape(cmd) + r'\b', all_code.upper()):
                return 'time_warp'

        # Check for exact word matches to avoid substring conflicts
        time_warp_score = 0
        for cmd in time_warp_commands:
            # Use word boundaries to match whole words only
            if re.search(r'\b' + re.escape(cmd) + r'\b', all_code.upper()):
                time_warp_score += 1
        
        # If any Time_Warp commands are found, treat as Time_Warp
        if time_warp_score >= 1:
            return 'time_warp'
        
        # Check for variable assignment patterns (var = expr) - only if no other language detected
        # and the assignment looks like Time_Warp syntax (simple variable names)
        if "=" in code and not code.upper().startswith(("IF", "FOR", "WHILE", "LET")):
            # Must look like a variable assignment: identifier = expression
            parts = code.split("=", 1)
            if len(parts) == 2:
                var_part = parts[0].strip()
                expr_part = parts[1].strip()
                # Variable name must be valid identifier, not start with digit, and expression must exist
                # Also check that this doesn't look like other language syntax
                if (var_part.replace("_", "").isalnum() and not var_part[0].isdigit() 
                    and var_part and expr_part and not any(char in expr_part for char in ['(', ')', '{', '}', ';', ':'])):
                    return 'time_warp'

        # Default to Time_Warp for immediate commands instead of PILOT
        return 'time_warp'

    def _validate_syntax(self, code, language):
        """Validate syntax for the given language"""
        errors = []
        lines = code.split('\n')

        if language == 'basic':
            errors = self._validate_basic_syntax(lines)
        elif language == 'logo':
            errors = self._validate_logo_syntax(lines)
        elif language == 'pilot':
            errors = self._validate_pilot_syntax(lines)
        elif language == 'pascal':
            errors = self._validate_pascal_syntax(code)
        elif language == 'prolog':
            errors = self._validate_prolog_syntax(code)
        else:
            # For unsupported languages, just check for basic structure
            errors = self._validate_generic_syntax(lines)

        return errors

    def _validate_basic_syntax(self, lines):
        """Validate BASIC syntax"""
        errors = []

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.upper().startswith('REM'):
                continue

            # Check for line numbers (optional in this BASIC)
            parts = line.split(None, 1)
            if parts and parts[0].isdigit():
                command = parts[1] if len(parts) > 1 else ""
            else:
                command = line

            # Check for unmatched quotes
            if command.count('"') % 2 != 0:
                errors.append({
                    'line': i,
                    'message': "Unmatched quotes"
                })

            # Check for THEN without IF
            if 'THEN' in command.upper() and 'IF' not in command.upper():
                errors.append({
                    'line': i,
                    'message': "THEN without IF"
                })

        return errors

    def _validate_logo_syntax(self, lines):
        """Validate Logo syntax"""
        errors = []

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            # Check for unmatched brackets in REPEAT
            if 'REPEAT' in line.upper():
                open_brackets = line.count('[')
                close_brackets = line.count(']')
                if open_brackets != close_brackets:
                    errors.append({
                        'line': i,
                        'message': f"Unmatched brackets in REPEAT: {open_brackets} opening, {close_brackets} closing"
                    })

        return errors

    def _validate_pilot_syntax(self, lines):
        """Validate PILOT syntax"""
        errors = []
        valid_commands = ['T:', 'A:', 'J:', 'Y:', 'N:', 'C:', 'R:', 'D:', 'E:', 'U:']

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            # Check if line starts with valid PILOT command
            if len(line) >= 2 and line[1] == ':':
                command = line[:2].upper()
                if command not in valid_commands:
                    errors.append({
                        'line': i,
                        'message': f"Unknown PILOT command: {command}"
                    })

        return errors

    def _validate_pascal_syntax(self, code):
        """Validate Pascal syntax (basic checks)"""
        errors = []
        lines = code.split('\n')

        for i, line in enumerate(lines, 1):
            line = line.strip().upper()
            if not line or line.startswith('{') or line.startswith('(*'):
                continue

            # Check for unmatched braces
            open_braces = line.count('(')
            close_braces = line.count(')')
            if open_braces != close_braces:
                errors.append({
                    'line': i,
                    'message': f"Unmatched parentheses: {open_braces} opening, {close_braces} closing"
                })

            # Check for semicolons (basic check)
            if line and not line.endswith(';') and not any(line.endswith(x) for x in ['BEGIN', 'END', 'THEN', 'ELSE', 'DO']):
                if not line.startswith(('PROGRAM', 'VAR', 'CONST', 'PROCEDURE', 'FUNCTION', 'BEGIN', 'END')):
                    errors.append({
                        'line': i,
                        'message': "Missing semicolon"
                    })

        return errors

    def _validate_prolog_syntax(self, code):
        """Validate Prolog syntax (basic checks)"""
        errors = []
        lines = code.split('\n')

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('%'):
                continue

            # Check for unmatched parentheses
            open_parens = line.count('(')
            close_parens = line.count(')')
            if open_parens != close_parens:
                errors.append({
                    'line': i,
                    'message': f"Unmatched parentheses: {open_parens} opening, {close_parens} closing"
                })

            # Check for missing period at end
            if line and not line.endswith('.'):
                errors.append({
                    'line': i,
                    'message': "Missing period at end of clause"
                })

        return errors

    def _validate_generic_syntax(self, lines):
        """Generic syntax validation for unsupported languages"""
        errors = []

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            # Check for unmatched quotes
            if line.count('"') % 2 != 0:
                errors.append({
                    'line': i,
                    'message': "Unmatched quotes"
                })

            # Check for unmatched parentheses
            open_parens = line.count('(')
            close_parens = line.count(')')
            if open_parens != close_parens:
                errors.append({
                    'line': i,
                    'message': f"Unmatched parentheses: {open_parens} opening, {close_parens} closing"
                })

        return errors


def main():
    print("[DEBUG] Entered main()")
    import sys
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test" and len(sys.argv) >= 4:
            # Run in test mode: python Time_Warp.py --test test_file language
            test_file = sys.argv[2]
            language = sys.argv[3]
            interpreter = Time_WarpInterpreter()
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    code = f.read()
                print(f"Testing {language} code from {test_file}")
                interpreter.run_program(code, language=language.lower())
                print("Test completed successfully")
                return
            except Exception as e:
                print(f"Test failed: {e}")
                sys.exit(1)
        elif sys.argv[1] == "--help":
            print("Time_Warp IDE v1.3.0")
            print("Usage:")
            print("  python Time_Warp.py                    # Start GUI")
            print("  python Time_Warp.py --test file lang    # Run test file")
            print("  python Time_Warp.py --help              # Show this help")
            return
    print("[DEBUG] Instantiating TimeWarpApp and starting mainloop")
    root = tk.Tk()
    app = TimeWarpApp(root)
    root.mainloop()
    print("[DEBUG] Exited mainloop")

if __name__ == "__main__":
    main()


