# Set pygame env and suppress noisy warnings early
import os
import sys
import warnings

# Set pygame environment variable to suppress AVX2 warning
os.environ["PYGAME_DETECT_AVX2"] = "1"
# Suppress pygame AVX2 warning
warnings.filterwarnings("ignore", message=".*avx2.*", category=RuntimeWarning)


# UnifiedCanvasOutputHandler: compatibility wrapper for interpreter output
class UnifiedCanvasOutputHandler:
    """Thread-safe wrapper that schedules writes to the UnifiedCanvas.

    Writes are scheduled on the Tk mainloop to remain thread-safe.
    """

    def __init__(self, unified_canvas):
        self.unified_canvas = unified_canvas

    def insert(self, position, text):
    # Schedule writes on the canvas via the event loop to remain
    # thread-safe
        try:
            self.unified_canvas.after(
                0, lambda: self._do_insert(position, text)
            )
        except Exception:
            # Fallback: direct write (best-effort)
            try:
                self.unified_canvas.write_text(text)
            except Exception:
                print(text)

    def _do_insert(self, position, text):
        import tkinter as tk
        # Write the provided text directly. Normalization (ensuring a trailing
        # newline) is handled by the caller or the UI queue flusher so we avoid
        # inserting extra leading newlines here which could hide output.
        # Temporary debug logging: record insert attempts to /tmp/time_warp_ui.log
        try:
            with open(".diagnostics/time_warp_ui.log", "a", encoding="utf-8") as _lf:
                _lf.write(f"_do_insert called pos={position!r} text={text!r}\n")
        except Exception:
            pass

        # Write the provided text directly. Normalization is handled by caller.
        try:
            self.unified_canvas.write_text(str(text))
            try:
                self.unified_canvas.update_idletasks()
            except Exception:
                pass
            try:
                with open(".diagnostics/time_warp_ui.log", "a", encoding="utf-8") as _lf:
                    _lf.write("write_text succeeded\n")
            except Exception:
                pass
        except Exception as _write_err:
            # Best-effort fallback to print and log the error
            try:
                print(text)
            except Exception:
                pass
            try:
                with open(".diagnostics/time_warp_ui.log", "a", encoding="utf-8") as _lf:
                    _lf.write(f"write_text failed: {_write_err!r}\n")
            except Exception:
                pass

    def see(self, position):
        # Unified canvas doesn't need scrolling, but could be implemented
        pass

    def request_input(self, prompt, input_type=str):
        """Show input prompt in the unified canvas and enable input handling."""

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
                self.unified_canvas.write_text(
                    f"\n❌ Invalid input type. Expected {input_type.__name__}.\n",
                    color=4,
                )
                self.unified_canvas.prompt_input(
                    prompt,
                    lambda val: self._handle_input_callback(val, input_type),
                )

        self.unified_canvas.prompt_input(prompt, input_callback)


"""Time_Warp IDE - Simple Educational Programming Environment

A minimal Tkinter-based IDE for running multi-language programs with the
Time_Warp interpreter. Supports TW BASIC, Pascal, and Prolog execution.

Features:
- Simple text editor with Courier font
- One-click program execution
- Integrated interpreter with multiple language support
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
        result = subprocess.run(
            [sys.executable, str(requirements_script), "--check"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            print("✅ Environment is properly configured")
            # Activate virtual environment in current process
            activate_venv_in_process()
            return True
        else:
            print("🔧 Environment needs setup...")
            # Run full setup
            result = subprocess.run(
                [sys.executable, str(requirements_script)], timeout=600
            )  # 10 minute timeout for setup
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
    if os.name == "nt":  # Windows
        python_exe = venv_path / "Scripts" / "python.exe"
        site_packages = venv_path / "Lib" / "site-packages"
    else:  # Unix-like systems
        python_exe = venv_path / "bin" / "python"
        site_packages = (
            venv_path
            / "lib"
            / f"python{sys.version_info.major}.{sys.version_info.minor}"
            / "site-packages"
        )

    if not python_exe.exists():
        return False

    # Add venv site-packages to Python path
    if str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))

    # Update environment variables
    os.environ["VIRTUAL_ENV"] = str(venv_path)
    os.environ["PATH"] = (
        str(venv_path / "bin") + os.pathsep + os.environ.get("PATH", "")
    )

    return True


# Run environment check before importing other modules
if not check_environment():
    print("❌ Environment setup failed. Please check the errors above.")
    sys.exit(1)

# Check if we're in a headless environment
try:
    import tkinter as tk

    root = tk.Tk()
    root.withdraw()  # Hide the window immediately
    root.destroy()
    GUI_AVAILABLE = True
except tk.TclError:
    print("⚠️  GUI not available (headless environment detected)")
    print(
        "💡  Time_Warp IDE requires a graphical desktop environment to display the interface."
    )
    print(
        "💡  Please run this application on a system with X11, Wayland, or similar display server."
    )
    GUI_AVAILABLE = False

if not GUI_AVAILABLE:
    print("\n🔧 To run Time_Warp IDE:")
    print("   1. Use a graphical desktop environment")
    print(
        "   2. Connect via SSH with X11 forwarding: ssh -X username@hostname"
    )
    print("   3. Use VNC or similar remote desktop solution")
    print("   4. Run on a local machine with display")
    sys.exit(1)

import json
import os
import queue
import re
import threading
# Now import other modules after environment is verified
import tkinter as tk
from tkinter import messagebox, ttk

from core.languages import (TwBasicInterpreter, TwPascalInterpreter,
                            TwPrologInterpreter)
from unified_canvas import Theme, UnifiedCanvas

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
            state="disabled",
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
            insertbackground="black",
        )
        self.text_widget.pack(side="left", fill="both", expand=True)

        # Create horizontal scrollbar
        self.h_scrollbar = tk.Scrollbar(
            self, orient="horizontal", command=self.text_widget.xview
        )
        self.h_scrollbar.pack(side="bottom", fill="x")
        self.text_widget.config(xscrollcommand=self.h_scrollbar.set)

        # Create vertical scrollbar
        self.v_scrollbar = tk.Scrollbar(
            self.main_frame, orient="vertical", command=self._on_scroll
        )
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
        self.text_widget.bind(
            "<Button-4>", self._update_line_numbers
        )  # Linux scroll up
        self.text_widget.bind(
            "<Button-5>", self._update_line_numbers
        )  # Linux scroll down

        # Line numbers visibility flag
        self.line_numbers_visible = True

    def _init_advanced_features(self):
        """Initialize advanced editor features"""
        try:
            # Syntax highlighting
            self.syntax_highlighter = AdvancedSyntaxHighlighter(
                self.text_widget
            )
            self.text_widget.bind(
                "<KeyRelease>",
                self.syntax_highlighter.highlight_syntax,
                add=True,
            )

            # Auto-completion
            self.auto_completion = AutoCompletionEngine(self.text_widget)
            self.text_widget.bind(
                "<Control-space>", self.auto_completion.show_completions
            )

            # Syntax checking
            self.syntax_checker = RealTimeSyntaxChecker(self.text_widget)
            self.text_widget.bind(
                "<KeyRelease>", self.syntax_checker.check_syntax, add=True
            )

            # Code folding
            self.code_folding = CodeFoldingSystem(self.text_widget)

        except Exception as e:
            print(
                f"Warning: Could not initialize advanced editor features: {e}"
            )

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
            prev_line = self.text_widget.get(
                f"{line_num-1}.0", f"{line_num-1}.end"
            )
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
                if (
                    line_text.strip().startswith("def ")
                    or line_text.strip().startswith("class ")
                    or "import " in line_text
                ):
                    comment_char = "#"  # Python
                elif "::" in line_text or line_text.strip().startswith("REM"):
                    comment_char = "//"  # TW BASIC style
                elif any(
                    cmd in line_text.upper()
                    for cmd in ["FORWARD", "PRINT", "REM"]
                ):
                    comment_char = ";"  # TW BASIC style
                else:
                    comment_char = "#"  # Default

                # Toggle comment
                if line_text.strip().startswith(comment_char):
                    # Uncomment
                    comment_start = line_text.find(comment_char)
                    self.text_widget.delete(
                        f"{line_num}.{comment_start}",
                        f"{line_num}.{comment_start + len(comment_char)}",
                    )
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
        if hasattr(self, "_last_find_text") and self._last_find_text:
            self._find_text(self._last_find_text)
        return "break"

    def _show_find_dialog(self):
        """Show find/replace dialog"""
        dialog = tk.Toplevel(self)
        dialog.title("Find & Replace")
        dialog.geometry("400x150")
        dialog.transient(self.winfo_toplevel())

        # Find text
        tk.Label(dialog, text="Find:").grid(
            row=0, column=0, sticky="e", padx=5, pady=5
        )
        find_entry = tk.Entry(dialog, width=30)
        find_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5)

        # Replace text
        tk.Label(dialog, text="Replace:").grid(
            row=1, column=0, sticky="e", padx=5, pady=5
        )
        replace_entry = tk.Entry(dialog, width=30)
        replace_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5)

        # Buttons
        find_btn = tk.Button(
            dialog,
            text="Find",
            command=lambda: self._find_text(find_entry.get()),
        )
        find_btn.grid(row=2, column=0, padx=5, pady=5)

        replace_btn = tk.Button(
            dialog,
            text="Replace",
            command=lambda: self._replace_text(
                find_entry.get(), replace_entry.get()
            ),
        )
        replace_btn.grid(row=2, column=1, padx=5, pady=5)

        replace_all_btn = tk.Button(
            dialog,
            text="Replace All",
            command=lambda: self._replace_all_text(
                find_entry.get(), replace_entry.get()
            ),
        )
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
            self.output_panel.insert(
                "end",
                f"\n❌ Invalid input type. Expected {input_type.__name__}.\n",
            )
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
        self.root = root
        self.root.title("Time_Warp IDE v1.3.0")
        self.root.geometry(
            "1000x700"
        )  # Increased size for better content visibility
        self.root.minsize(
            800, 600
        )  # Set minimum size to prevent too small windows
        self.current_file = None
        self.selected_theme = "Spring"  # Start with light theme for contrast
        self.selected_font_family = "Consolas"  # Default monospace font
        self.selected_font_size = 11  # Default font size
        self.config_path = os.path.expanduser("~/.Time_Warp/config.json")
        # Instantiate the three interpreters
        self.tw_basic = TwBasicInterpreter()
        self.pascal = TwPascalInterpreter()
        self.prolog = TwPrologInterpreter()
        self.current_language = "tw_basic"
        # Plugin manager (optional)
        try:
            from plugins import PluginManager, PluginManagerDialog

            self.plugin_manager = PluginManager(self)
            self.plugin_manager_dialog = None
        except Exception:
            self.plugin_manager = None
            self.plugin_manager_dialog = None

        # Theme manager (optional)
        self.theme_manager = None
        try:
            from src.timewarp.utils.theme import ThemeManager, available_themes

            self.theme_manager = ThemeManager()
        except Exception:
            pass

        # Add status label at the bottom of the main window
        self.status_label = tk.Label(
            self.root,
            text="Ready.",
            anchor="w",
            bg="#222",
            fg="#fff",
            font=(self.selected_font_family, 10),
        )
        self.status_label.pack(side="bottom", fill="x")

        # Global keybindings
        self.root.bind("<F5>", lambda e: self.run_program())
        self.root.bind("<Control-r>", lambda e: self.run_program())
        self.root.bind("<Control-c>", lambda e: self._copy_text())
        self.root.bind("<Control-v>", lambda e: self._paste_text())
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Create UI and load configs
        self._create_ui()
        self._load_theme_config()
        self._load_font_config()

    def get_current_interpreter(self):
        """Get the current interpreter based on selected language"""
        if self.current_language == "tw_basic":
            return self.tw_basic
        elif self.current_language == "pascal":
            return self.pascal
        elif self.current_language == "prolog":
            return self.prolog
        else:
            return self.tw_basic  # default
        # get_current_interpreter end

    def new_file(self):
        # Clear any loaded program
        current_interpreter = self.get_current_interpreter()
        if hasattr(current_interpreter, "program_lines"):
            current_interpreter.program_lines = []
        self.current_file = None
        self.unified_canvas.write_text(
            "New program started. Previous program cleared.\n", color=10
        )
        self.status_label.config(text="🆕 New program started")

    def open_file(self):
        from tkinter import filedialog

        file_path = filedialog.askopenfilename(
            filetypes=[
                ("All Files", "*.*"),
                ("TW BASIC", "*.tw"),
                ("Python", "*.py"),
                ("Text", "*.txt"),
            ]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Store the current file path
                self.current_file = file_path

                # Load file content into Code Editor
                self.code_editor.text_widget.delete("1.0", tk.END)
                self.code_editor.text_widget.insert("1.0", content)
                self.status_label.config(text=f"📂 Loaded file: {file_path}")
            except Exception as e:
                self.status_label.config(
                    text=f"❌ Error loading file: {str(e)}"
                )

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
            current_interpreter = self.get_current_interpreter()
            if (
                hasattr(current_interpreter, "program_lines")
                and current_interpreter.program_lines
            ):
                # Save as line-numbered program
                with open(file_path, "w", encoding="utf-8") as f:
                    for line_num, cmd in current_interpreter.program_lines:
                        f.write(f"{line_num} {cmd}\n")
                self.unified_canvas.write_text(
                    f"Program saved to {file_path}\n", color=10
                )
                self.status_label.config(text=f"💾 Saved program: {file_path}")
            else:
                # No program to save
                self.unified_canvas.write_text(
                    "No program loaded to save.\n", color=14
                )
                self.unified_canvas.write_text(
                    "Create a line-numbered program first.\n", color=14
                )
                self.status_label.config(text="❌ No program to save")
        except Exception as e:
            self.unified_canvas.write_text(
                f"Error saving file: {str(e)}\n", color=12
            )
            self.status_label.config(text=f"❌ Error saving file: {str(e)}")

    def save_file_as(self):
        from tkinter import filedialog

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("All Files", "*.*"),
                ("TW BASIC", "*.tw"),
                ("Python", "*.py"),
                ("Text", "*.txt"),
            ],
        )
        if file_path:
            try:
                # Check if we have a line-numbered program to save
                current_interpreter = self.get_current_interpreter()
                if (
                    hasattr(current_interpreter, "program_lines")
                    and current_interpreter.program_lines
                ):
                    # Save as line-numbered program
                    with open(file_path, "w", encoding="utf-8") as f:
                        for line_num, cmd in current_interpreter.program_lines:
                            f.write(f"{line_num} {cmd}\n")
                    self.unified_canvas.write_text(
                        f"Program saved as {file_path}\n", color=10
                    )
                    self.status_label.config(
                        text=f"💾 Saved program as: {file_path}"
                    )
                    self.current_file = file_path
                else:
                    # No program to save
                    self.unified_canvas.write_text(
                        "No program loaded to save.\n", color=14
                    )
                    self.unified_canvas.write_text(
                        "Create a line-numbered program first.\n", color=14
                    )
                    self.status_label.config(text="❌ No program to save")
            except Exception as e:
                self.unified_canvas.write_text(
                    f"Error saving file: {str(e)}\n", color=12
                )
                self.status_label.config(
                    text=f"❌ Error saving file: {str(e)}"
                )
        return file_path if "file_path" in locals() and file_path else None

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
        current_interpreter = self.get_current_interpreter()
        if hasattr(current_interpreter, "turtle_graphics"):
            current_interpreter.turtle_graphics = None
        self.status_label.config(text="🧹 Graphics cleared.")

    def _toggle_line_numbers(self):
        """Toggle line numbers visibility in the code editor"""
        if hasattr(self.editor, "line_numbers_visible"):
            # Enhanced editor
            self.editor.line_numbers_visible = (
                not self.editor.line_numbers_visible
            )
            self.editor._update_line_numbers()
            status = "shown" if self.editor.line_numbers_visible else "hidden"
            self.status_label.config(text=f"📏 Line numbers {status}.")
        else:
            # Basic editor - line numbers not supported
            messagebox.showinfo(
                "Line Numbers",
                "Line numbers are only available in enhanced editor mode.",
            )

    def _open_find_replace(self):
        """Open find/replace dialog"""
        if hasattr(self.editor, "_show_find_dialog"):
            self.editor._show_find_dialog()
        else:
            messagebox.showinfo(
                "Find/Replace",
                "Find/Replace is not available in basic editor mode.",
            )

    def _find_next(self):
        """Find next occurrence"""
        if hasattr(self.editor, "_find_next"):
            self.editor._find_next()
        else:
            messagebox.showinfo(
                "Find Next", "Find Next is not available in basic editor mode."
            )

    def _toggle_comment(self):
        """Toggle comment on current line/selection"""
        if hasattr(self.editor, "_toggle_comment"):
            self.editor._toggle_comment(event=None)
        else:
            messagebox.showinfo(
                "Toggle Comment",
                "Comment toggle is not available in basic editor mode.",
            )

    def _copy_text(self):
        """Copy selected text to clipboard"""
        try:
            if hasattr(self.editor, "text_widget"):
                # Enhanced editor
                selected_text = self.editor.text_widget.get(
                    tk.SEL_FIRST, tk.SEL_LAST
                )
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
            if hasattr(self.editor, "text_widget"):
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
        if hasattr(self.editor, "text_widget"):
            # Enhanced editor
            self.editor.text_widget.insert(tk.INSERT, "    ")
        else:
            # Basic editor
            self.editor.insert(tk.INSERT, "    ")

    def _decrease_indent(self):
        """Decrease indentation"""
        if hasattr(self.editor, "_handle_shift_tab"):
            self.editor._handle_shift_tab(event=None)
        else:
            messagebox.showinfo(
                "Decrease Indent",
                "Indentation tools are not available in basic editor mode.",
            )

    def _undo(self):
        """Undo last action"""
        try:
            if hasattr(self.editor, "text_widget"):
                self.editor.text_widget.edit_undo()
            else:
                self.editor.edit_undo()
            self.status_label.config(text="↩️ Undo completed.")
        except tk.TclError:
            self.status_label.config(text="↩️ Nothing to undo.")

    def _redo(self):
        """Redo last undone action"""
        try:
            if hasattr(self.editor, "text_widget"):
                self.editor.text_widget.edit_redo()
            else:
                self.editor.edit_redo()
            self.status_label.config(text="↪️ Redo completed.")
        except tk.TclError:
            self.status_label.config(text="↪️ Nothing to redo.")

    def _cut_text(self):
        """Cut selected text to clipboard"""
        try:
            if hasattr(self.editor, "text_widget"):
                self.editor.text_widget.event_generate("<<Cut>>")
            else:
                self.editor.event_generate("<<Cut>>")
            self.status_label.config(text="✂️ Text cut to clipboard.")
        except tk.TclError:
            self.status_label.config(text="✂️ No text selected to cut.")

    def _clear_all(self):
        """Clear all content from unified canvas"""
        self.unified_canvas.clear_screen()
        self.status_label.config(text="🧹 All content cleared.")

    def _stop_program(self):
        """Stop currently running program"""
        # For now, just show a message since we don't have background execution
        self.status_label.config(text="🛑 Stop program - not implemented yet.")

    def _restart_interpreter(self):
        """Restart the interpreter"""
        try:
            # Reinitialize the current interpreter
            current_interpreter = self.get_current_interpreter()
            # Reset unified canvas reference
            if hasattr(current_interpreter, "ide_unified_canvas"):
                current_interpreter.ide_unified_canvas = self.unified_canvas

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
            if hasattr(current_interpreter, "output_widget"):
                current_interpreter.output_widget = UnifiedCanvasOutputHandler(
                    self.unified_canvas
                )

            # Reset turtle canvas reference (unified canvas acts as turtle canvas too)
            if hasattr(current_interpreter, "ide_turtle_canvas"):
                current_interpreter.ide_turtle_canvas = self.unified_canvas

            self.unified_canvas.write_text(
                "Interpreter restarted successfully.\n"
            )
            self.status_label.config(text="🔄 Interpreter restarted.")
        except Exception as e:
            self.unified_canvas.write_text(
                f"Failed to restart interpreter: {str(e)}\n"
            )
            self.status_label.config(
                text=f"🔄 Failed to restart interpreter: {str(e)}"
            )

    def _set_language(self, language):
        """Set the current programming language"""
        valid_languages = ["tw_basic", "pascal", "prolog"]
        if language not in valid_languages:
            language = "tw_basic"
        self.current_language = language
        if language == "tw_basic":
            label = "TW BASIC"
        elif language == "pascal":
            label = "Pascal"
        elif language == "prolog":
            label = "Prolog"
        self.status_label.config(text=f"💻 Language set to: {label}")

    def _open_settings(self):
        """Open settings dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("⚙️ Settings")
        dialog.geometry("400x300")
        dialog.transient(self.root)

        tk.Label(dialog, text="Font Family:").pack(pady=5)
        font_var = tk.StringVar(value=self.selected_font_family)
        font_entry = tk.Entry(dialog, textvariable=font_var)
        font_entry.pack(pady=5)

        tk.Label(dialog, text="Font Size:").pack(pady=5)
        size_var = tk.IntVar(value=self.selected_font_size)
        size_entry = tk.Entry(dialog, textvariable=size_var)
        size_entry.pack(pady=5)

        def save_settings():
            self.selected_font_family = font_var.get()
            self.selected_font_size = size_var.get()
            self.unified_canvas.set_font(
                self.selected_font_family, self.selected_font_size
            )
            dialog.destroy()
            self.status_label.config(text="⚙️ Settings updated.")

        tk.Button(dialog, text="Save", command=save_settings).pack(pady=20)

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
Available Languages: TW BASIC, Pascal, Prolog"""
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
            messagebox.showinfo(
                "Report Generated",
                "📋 System report saved to 'system_report.txt'",
            )
        except Exception as e:
            messagebox.showerror(
                "Report Error", f"❌ Could not save report: {str(e)}"
            )

    def _open_online_resources(self):
        """Open online resources"""
        import webbrowser

        try:
            webbrowser.open("https://github.com/pygame/pygame")
            self.status_label.config(text="🌐 Opened online resources.")
        except Exception as e:
            messagebox.showerror(
                "Browser Error", f"❌ Could not open browser: {str(e)}"
            )

    def _report_issue(self):
        """Report an issue"""
        import webbrowser

        try:
            webbrowser.open("https://github.com/pygame/pygame/issues")
            self.status_label.config(text="🆘 Opened issue reporting page.")
        except Exception as e:
            messagebox.showerror(
                "Browser Error", f"❌ Could not open browser: {str(e)}"
            )

    def _feature_request(self):
        """Submit a feature request"""
        import webbrowser

        try:
            webbrowser.open("https://github.com/pygame/pygame/discussions")
            self.status_label.config(text="💡 Opened feature request page.")
        except Exception as e:
            messagebox.showerror(
                "Browser Error", f"❌ Could not open browser: {str(e)}"
            )

    def _check_updates(self):
        """Check for updates"""
        messagebox.showinfo(
            "Updates",
            "🔄 Update checking not implemented yet.\n\nPlease check GitHub for the latest releases.",
        )

    def run_program(self):
        """
        Execute the program currently in the code editor.
        """
        code = self.code_editor.text_widget.get("1.0", tk.END).strip()
        self.notebook.select(self.output_frame)
        self.unified_canvas.clear_all()
        if not code:
            self.unified_canvas.write_text("❌ No code entered.\n")
            self.unified_canvas.redraw()
            self.status_label.config(text="❌ No code to execute.")
            return
        try:

            def _run_in_thread(func, *fargs, **fkwargs):
                def _target():
                    try:
                        func(*fargs, **fkwargs)
                        # Ensure UI updates happen on main thread
                        try:
                            self.root.after(
                                0, lambda: self.unified_canvas.redraw()
                            )
                            self.root.after(
                                0,
                                lambda: self.status_label.config(
                                    text="🚀 Program executed."
                                ),
                            )
                        except Exception:
                            pass
                    except Exception as e:
                        try:
                            err_text = f"❌ Error: {e}\n"
                            err_status = f"❌ Execution error: {e}"
                            self.root.after(0, lambda err_text=err_text: self.unified_canvas.write_text(err_text))
                            self.root.after(0, lambda err_status=err_status: self.status_label.config(text=err_status))
                        except Exception:
                            pass

                t = threading.Thread(target=_target, daemon=True)
                t.start()

            # Cancel welcome screen if still pending to avoid races with program output
            try:
                if (
                    hasattr(self, "_welcome_after_id")
                    and self._welcome_after_id
                ):
                    try:
                        self.root.after_cancel(self._welcome_after_id)
                    except Exception:
                        pass
                    self._welcome_after_id = None
            except Exception:
                pass

            if self.current_language == "tw_basic":
                # Set up graphics integration
                self.tw_basic.ide_unified_canvas = self.unified_canvas
                self.tw_basic.ide_turtle_canvas = self.unified_canvas

                # Enqueue outputs so the UI poller flushes them on the main thread
                def _tw_basic_callback(text):
                    try:
                        # Enqueue a normalized tuple: (text, color)
                        self._ui_output_queue.put((str(text), 10))
                    except Exception:
                        try:
                            self._ui_output_queue.put((str(text), None))
                        except Exception:
                            pass

                self.tw_basic.set_output_callback(_tw_basic_callback)
                # Run interpreter execution off the Tk main thread
                _run_in_thread(self.tw_basic.execute_command, code)
            elif self.current_language == "pascal":
                # Set up graphics integration
                self.pascal.ide_unified_canvas = self.unified_canvas
                self.pascal.ide_turtle_canvas = self.unified_canvas
                self.pascal.set_output_callback(
                    lambda text: self._ui_output_queue.put(
                        (str(text) + "\n", 10)
                    )
                )
                _run_in_thread(self.pascal.execute_command, code)
            elif self.current_language == "prolog":
                # Set up graphics integration
                self.prolog.ide_unified_canvas = self.unified_canvas
                self.prolog.ide_turtle_canvas = self.unified_canvas
                self.prolog.set_output_callback(
                    lambda text: self._ui_output_queue.put(
                        (str(text) + "\n", 10)
                    )
                )
                _run_in_thread(self.prolog.execute_command, code)
            self.unified_canvas.redraw()
            self.status_label.config(text="🚀 Program executed.")
        except Exception as e:
            self.unified_canvas.write_text(f"❌ Error: {str(e)}\n")
            self.unified_canvas.redraw()
            self.status_label.config(text=f"❌ Execution error: {str(e)}")

    def show_about(self):
        """Show about dialog"""
        about_text = """Time_Warp IDE v1.3.0

An educational programming environment supporting multiple languages:
• TW BASIC: Unified educational language (BASIC, PILOT, Logo features)
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
                messagebox.showinfo(
                    "Documentation",
                    "📚 Documentation is available in the 'docs/' folder.\n\nCheck README.md for usage instructions.",
                )
        except Exception as e:
            messagebox.showerror(
                "Documentation Error",
                f"Could not open documentation:\n\n{str(e)}",
            )

    def toggle_output_panel(self):
        """In unified canvas mode, output is always visible"""
        self.unified_canvas.write_text(
            "Output panel is integrated into unified canvas.\n"
        )
        self.status_label.config(
            text="📊 Output is always visible in unified canvas mode"
        )

    def toggle_turtle_graphics(self):
        """In unified canvas mode, graphics are always visible"""
        self.unified_canvas.write_text(
            "Graphics are integrated into unified canvas.\n"
        )
        self.status_label.config(
            text="🐢 Graphics are always visible in unified canvas mode"
        )

    def switch_to_editor(self):
        """In unified canvas mode, editing is handled externally"""
        self.unified_canvas.write_text("Code editing is handled externally.\n")
        self.unified_canvas.write_text(
            "Please use external editor for code input.\n"
        )
        self.status_label.config(
            text="📝 Code editing is external in unified canvas mode"
        )

    def open_plugin_manager(self):
        """Open the plugin manager dialog"""
        if self.plugin_manager and hasattr(
            self.plugin_manager, "list_available_plugins"
        ):
            if not self.plugin_manager_dialog:
                from plugins import PluginManagerDialog

                self.plugin_manager_dialog = PluginManagerDialog(
                    self, self.plugin_manager
                )
            self.plugin_manager_dialog.show()
        else:
            messagebox.showerror(
                "Plugin Manager", "❌ Plugin system not available."
            )

    def open_theme_selector(self):
        """Open theme selector dialog"""
        themes = [
            # Dark Themes
            "Dracula",
            "Monokai",
            "Solarized Dark",
            "Ocean",
            "Gruvbox Dark",
            "Nord",
            "One Dark",
            "Tokyo Night",
            "Gotham",
            "Material Dark",
            # Light Themes
            "Spring",
            "Sunset",
            "Candy",
            "Forest",
            "Solarized Light",
            "Gruvbox Light",
            "One Light",
            "GitHub Light",
            "Material Light",
            "Minimal",
        ]

        dialog = tk.Toplevel(self.root)
        dialog.title("🎨 Select Theme")
        dialog.geometry("500x450")
        dialog.transient(self.root)

        tk.Label(
            dialog, text="Choose a theme:", font=("Arial", 12, "bold")
        ).pack(pady=10)

        # Create scrollable frame for themes
        canvas = tk.Canvas(dialog)
        scrollbar = tk.Scrollbar(
            dialog, orient="vertical", command=canvas.yview
        )
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
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
                command=lambda t=theme: self._apply_theme_from_selector(
                    t, dialog
                ),
                font=("Arial", 10),
                width=15,
                height=2,
            )
            btn.grid(row=row, column=col, padx=5, pady=5)

        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y")

        # Current theme indicator
        tk.Label(
            dialog,
            text=f"Current: {self.selected_theme}",
            font=("Arial", 10, "italic"),
        ).pack(pady=5)

        # Font selection button
        tk.Button(
            dialog,
            text="⚙️ Font Settings",
            command=lambda: self._open_font_settings(dialog),
            font=("Arial", 11),
        ).pack(pady=5)

        tk.Button(
            dialog, text="Close", command=dialog.destroy, font=("Arial", 11)
        ).pack(pady=10)

    def _open_font_settings(self, parent_dialog):
        """Open font settings dialog"""
        font_dialog = tk.Toplevel(self.root)
        font_dialog.title("⚙️ Font Settings")
        font_dialog.geometry("400x300")
        # Use parent_dialog if provided, otherwise use root
        font_dialog.transient(parent_dialog if parent_dialog else self.root)

        tk.Label(
            font_dialog, text="Font Settings", font=("Arial", 14, "bold")
        ).pack(pady=10)

        # Font family selection
        family_frame = tk.Frame(font_dialog)
        family_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(family_frame, text="Font Family:", font=("Arial", 11)).pack(
            anchor="w"
        )
        self.font_family_var = tk.StringVar(value=self.selected_font_family)

        # Common monospace fonts
        font_families = [
            "Consolas",
            "Courier New",
            "Monaco",
            "Menlo",
            "DejaVu Sans Mono",
            "Liberation Mono",
            "Source Code Pro",
            "Fira Code",
            "JetBrains Mono",
            "Cascadia Code",
            "Roboto Mono",
            "Space Mono",
            "Ubuntu Mono",
        ]

        family_combo = ttk.Combobox(
            family_frame,
            textvariable=self.font_family_var,
            values=font_families,
            state="readonly",
            width=25,
        )
        family_combo.pack(pady=5)
        family_combo.bind("<<ComboboxSelected>>", self._preview_font)

        # Font size selection
        size_frame = tk.Frame(font_dialog)
        size_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(size_frame, text="Font Size:", font=("Arial", 11)).pack(
            anchor="w"
        )
        self.font_size_var = tk.IntVar(value=self.selected_font_size)

        size_combo = ttk.Combobox(
            size_frame,
            textvariable=self.font_size_var,
            values=list(range(8, 25)),
            state="readonly",
            width=25,
        )
        size_combo.pack(pady=5)
        size_combo.bind("<<ComboboxSelected>>", self._preview_font)

        # Preview area
        preview_frame = tk.Frame(font_dialog, relief="sunken", bd=1)
        preview_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(
            preview_frame, text="Preview:", font=("Arial", 10, "bold")
        ).pack(anchor="w", padx=5, pady=2)
        self.font_preview = tk.Text(
            preview_frame,
            height=3,
            wrap="word",
            font=(self.selected_font_family, self.selected_font_size),
        )
        self.font_preview.pack(fill="x", padx=5, pady=5)
        self.font_preview.insert(
            "1.0",
            "The quick brown fox jumps over the lazy dog\n1234567890\nprint('Hello, World!')",
        )
        self.font_preview.config(state="disabled")

        # Buttons
        button_frame = tk.Frame(font_dialog)
        button_frame.pack(fill="x", padx=20, pady=10)

        tk.Button(
            button_frame,
            text="Apply & Save",
            command=lambda: self._apply_font_settings(font_dialog),
            font=("Arial", 11),
        ).pack(side="left", padx=5)
        tk.Button(
            button_frame,
            text="Cancel",
            command=font_dialog.destroy,
            font=("Arial", 11),
        ).pack(side="right", padx=5)

    def _preview_font(self, event=None):
        """Preview font changes"""
        try:
            family = self.font_family_var.get()
            size = self.font_size_var.get()
            self.font_preview.config(font=(family, size))
        except Exception:
            pass

    def _apply_font_settings(self, dialog=None):
        """Apply font settings"""
        self.selected_font_family = self.font_family_var.get()
        self.selected_font_size = self.font_size_var.get()
        self._apply_font_to_ui()
        self._save_font_config()
        self.status_label.config(
            text=f"⚙️ Font '{self.selected_font_family}' ({self.selected_font_size}pt) applied."
        )
        # If called programmatically dialog may be None
        try:
            if dialog is not None:
                dialog.destroy()
        except Exception:
            pass

    def _apply_font_to_ui(self):
        """Apply selected font to all UI elements"""
        # Update unified canvas font
        if hasattr(self, "unified_canvas"):
            self.unified_canvas.set_font(
                self.selected_font_family, self.selected_font_size
            )

        # Update editor fonts
        if hasattr(self.editor, "text_widget"):
            # Enhanced editor
            self.editor.text_widget.config(
                font=(self.selected_font_family, self.selected_font_size)
            )
        else:
            # Basic editor
            self.editor.config(
                font=(self.selected_font_family, self.selected_font_size)
            )

        # Update line numbers font (if enhanced editor)
        if hasattr(self.editor, "line_numbers"):
            self.editor.line_numbers.config(
                font=(self.selected_font_family, self.selected_font_size - 2)
            )

    def _switch_to_editor_tab(self):
        """Toolbar action: switch to the code editor tab and focus it"""
        try:
            self.notebook.select(self.editor_frame)
            self.code_editor.focus_set()
            if hasattr(self, "status_label"):
                self.status_label.config(text="📝 Code Editor tab active.")
        except Exception:
            pass

    def _switch_to_output_tab(self):
        """Toolbar action: switch to the output console tab and focus it"""
        try:
            self.notebook.select(self.output_frame)
            self.unified_canvas.focus_set()
            if hasattr(self, "status_label"):
                self.status_label.config(text="📊 Output Console tab active.")
        except Exception:
            pass

    def _on_tab_changed(self, event=None):
        """Handler for notebook tab change events; update focus and status"""
        try:
            idx = self.notebook.index("current")
            # If index corresponds to editor_frame, focus editor; otherwise focus canvas
            if idx == self.notebook.index(self.editor_frame):
                try:
                    self.code_editor.focus_set()
                except Exception:
                    pass
                if hasattr(self, "status_label"):
                    self.status_label.config(text="📝 Code Editor tab active.")
            else:
                try:
                    self.unified_canvas.focus_set()
                except Exception:
                    pass
                if hasattr(self, "status_label"):
                    self.status_label.config(
                        text="📊 Output Console tab active."
                    )
        except Exception:
            pass

    def _save_font_config(self):
        """Save font configuration"""
        config = {
            "font_family": self.selected_font_family,
            "font_size": self.selected_font_size,
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
                self.selected_font_family = config.get(
                    "font_family", "Consolas"
                )
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
            "Dracula": {
                "bg": "#282a36",
                "fg": "#f8f8f2",
                "panel_bg": "#44475a",
                "panel_fg": "#f8f8f2",
                "accent": "#bd93f9",
            },
            "Monokai": {
                "bg": "#272822",
                "fg": "#f8f8f2",
                "panel_bg": "#49483e",
                "panel_fg": "#f8f8f2",
                "accent": "#fd971f",
            },
            "Solarized Dark": {
                "bg": "#002b36",
                "fg": "#839496",
                "panel_bg": "#073642",
                "panel_fg": "#93a1a1",
                "accent": "#268bd2",
            },
            "Ocean": {
                "bg": "#223447",
                "fg": "#c3eaff",
                "panel_bg": "#2a415d",
                "panel_fg": "#c3eaff",
                "accent": "#4fc3f7",
            },
            "Gruvbox Dark": {
                "bg": "#282828",
                "fg": "#ebdbb2",
                "panel_bg": "#3c3836",
                "panel_fg": "#ebdbb2",
                "accent": "#fabd2f",
            },
            "Nord": {
                "bg": "#2e3440",
                "fg": "#d8dee9",
                "panel_bg": "#3b4252",
                "panel_fg": "#d8dee9",
                "accent": "#88c0d0",
            },
            "One Dark": {
                "bg": "#282c34",
                "fg": "#abb2bf",
                "panel_bg": "#21252b",
                "panel_fg": "#abb2bf",
                "accent": "#61afef",
            },
            "Tokyo Night": {
                "bg": "#1a1b26",
                "fg": "#c0caf5",
                "panel_bg": "#16161e",
                "panel_fg": "#c0caf5",
                "accent": "#bb9af7",
            },
            "Gotham": {
                "bg": "#0a0f14",
                "fg": "#98d1ce",
                "panel_bg": "#0a0f14",
                "panel_fg": "#98d1ce",
                "accent": "#d26937",
            },
            "Material Dark": {
                "bg": "#263238",
                "fg": "#eeffff",
                "panel_bg": "#37474f",
                "panel_fg": "#eeffff",
                "accent": "#00bcd4",
            },
            # Light Themes
            "Spring": {
                "bg": "#f0f8ff",
                "fg": "#2e8b57",
                "panel_bg": "#e6f3ff",
                "panel_fg": "#2e8b57",
                "accent": "#32cd32",
            },
            "Sunset": {
                "bg": "#fff8f0",
                "fg": "#b22222",
                "panel_bg": "#ffe4b5",
                "panel_fg": "#b22222",
                "accent": "#ff6347",
            },
            "Candy": {
                "bg": "#fdf5ff",
                "fg": "#8b008b",
                "panel_bg": "#fce4ff",
                "panel_fg": "#8b008b",
                "accent": "#ff69b4",
            },
            "Forest": {
                "bg": "#f0fff0",
                "fg": "#006400",
                "panel_bg": "#e6f9e6",
                "panel_fg": "#006400",
                "accent": "#228b22",
            },
            "Solarized Light": {
                "bg": "#fdf6e3",
                "fg": "#586e75",
                "panel_bg": "#eee8d5",
                "panel_fg": "#586e75",
                "accent": "#268bd2",
            },
            "Gruvbox Light": {
                "bg": "#fbf1c7",
                "fg": "#3c3836",
                "panel_bg": "#ebdbb2",
                "panel_fg": "#3c3836",
                "accent": "#d79921",
            },
            "One Light": {
                "bg": "#fafafa",
                "fg": "#2c2c2c",
                "panel_bg": "#f0f0f0",
                "panel_fg": "#2c2c2c",
                "accent": "#4078f2",
            },
            "GitHub Light": {
                "bg": "#ffffff",
                "fg": "#24292f",
                "panel_bg": "#f6f8fa",
                "panel_fg": "#24292f",
                "accent": "#0969da",
            },
            "Material Light": {
                "bg": "#ffffff",
                "fg": "#212121",
                "panel_bg": "#f5f5f5",
                "panel_fg": "#212121",
                "accent": "#1976d2",
            },
            "Minimal": {
                "bg": "#ffffff",
                "fg": "#000000",
                "panel_bg": "#f5f5f5",
                "panel_fg": "#000000",
                "accent": "#666666",
            },
        }

        colors = theme_colors.get(theme_name, theme_colors["Dracula"])

        # Apply theme to main window and frames
        self.root.config(bg=colors["bg"])
        self.main_frame.config(bg=colors["bg"])

        # Apply theme to unified canvas
        if hasattr(self, "unified_canvas"):
            # Create Theme object for unified canvas
            theme_data = {
                "background": colors["bg"],
                "foreground": colors["fg"],
                "accent": colors["accent"],
                "panel_bg": colors["panel_bg"],
                "panel_fg": colors["panel_fg"],
                "cursor": colors["fg"],
                "selection_bg": self._get_selection_color(colors["bg"]),
                "syntax": {
                    "keyword": colors["accent"],
                    "string": "#4ecdc4",
                    "number": "#45b7d1",
                    "comment": "#7d8796",
                    "function": "#f9ca24",
                    "variable": "#6c5ce7",
                },
            }
            canvas_theme = Theme(theme_name, theme_data)
            self.unified_canvas.set_theme(canvas_theme)

        # Apply theme to status bar (if it exists)
        if hasattr(self, "status_label") and self.status_label:
            self.status_label.config(
                bg=colors["panel_bg"], fg=colors["panel_fg"]
            )

        # Update menu colors (limited Tkinter support)
        try:
            self.menubar.config(bg=colors["panel_bg"], fg=colors["panel_fg"])
        except Exception:
            pass

        # Force UI update
        self.root.update_idletasks()

    def _get_selection_color(self, bg_color):
        """Calculate appropriate selection color based on background"""
        # Convert hex to RGB
        bg_color = bg_color.lstrip("#")
        r = int(bg_color[0:2], 16)
        g = int(bg_color[2:4], 16)
        b = int(bg_color[4:6], 16)

        # Calculate brightness (YIQ formula)
        brightness = (r * 299 + g * 587 + b * 114) / 1000

        if brightness > 128:  # Light background
            # Use darker selection for light backgrounds
            return "#add8e6"  # Light blue
        else:  # Dark background
            # Use lighter selection for dark backgrounds
            return "#4a90e2"  # Medium blue

    def _save_theme_config(self, theme_name):
        """Save theme configuration to file"""
        try:
            config_dir = os.path.expanduser("~/.Time_Warp")
            os.makedirs(config_dir, exist_ok=True)
            config_file = os.path.join(config_dir, "config.json")
            config = {}
            if os.path.exists(config_file):
                with open(config_file, "r") as f:
                    config = json.load(f)
            config["theme"] = theme_name
            with open(config_file, "w") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            # Silently fail if we can't save config
            pass

    def _load_theme_config(self):
        """Load theme configuration from file"""
        try:
            config_file = os.path.expanduser("~/.Time_Warp/config.json")
            if os.path.exists(config_file):
                with open(config_file, "r") as f:
                    content = f.read().strip()
                    if content:  # Only parse if file is not empty
                        config = json.loads(content)
                        saved_theme = config.get("theme", "Dracula")
                        if saved_theme in [
                            "Dracula",
                            "Monokai",
                            "Solarized Dark",
                            "Ocean",
                            "Spring",
                            "Sunset",
                            "Candy",
                            "Forest",
                        ]:
                            self.selected_theme = saved_theme
        except Exception as e:
            # Silently fail if we can't load config, use default
            pass

    def run_tests(self):
        """Run test suite and display results in unified canvas"""
        import subprocess
        import sys

        try:
            result = subprocess.run(
                [sys.executable, "scripts/run_tests.py"],
                capture_output=True,
                text=True,
            )
            output = result.stdout + "\n" + result.stderr
            # Show in unified canvas
            self.unified_canvas.write_text("🧪 Test Results:\n\n" + output)
            # Also show summary in messagebox
            messagebox.showinfo(
                "Test Results", f"🧪 Test run complete:\n\n{output[:1000]}"
            )
        except Exception as e:
            self.unified_canvas.write_text(
                f"❌ Could not run tests:\n\n{str(e)}"
            )
            messagebox.showerror(
                "Test Error", f"❌ Could not run tests:\n\n{str(e)}"
            )

    def on_closing(self):
        """Handle window close event."""
        try:
            # Check if the root window still exists before showing dialog
            if self.root.winfo_exists():
                if messagebox.askokcancel(
                    "Quit", "Do you want to quit Time_Warp IDE?"
                ):
                    self.root.destroy()
            else:
                # Window already destroyed, just exit
                self.root.destroy()
        except tk.TclError:
            # Application is already being destroyed, just exit
            pass

    def _create_ui(self):
        # Create menu bar
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        # === FILE MENU === 📁
        file_menu = tk.Menu(self.menubar, tearoff=0)
        file_menu.add_command(
            label="📄 New File", command=self.new_file, accelerator="Ctrl+N"
        )
        file_menu.add_command(
            label="📂 Open File...",
            command=self.open_file,
            accelerator="Ctrl+O",
        )
        file_menu.add_command(
            label="💾 Save", command=self.save_file, accelerator="Ctrl+S"
        )
        file_menu.add_command(
            label="💾 Save As...",
            command=self.save_file_as,
            accelerator="Ctrl+Shift+S",
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="🚪 Exit", command=self.on_closing, accelerator="Ctrl+Q"
        )
        self.menubar.add_cascade(label="File", menu=file_menu)

        # === EDIT MENU === ✏️
        edit_menu = tk.Menu(self.menubar, tearoff=0)
        edit_menu.add_command(
            label="↩️ Undo", command=self._undo, accelerator="Ctrl+Z"
        )
        edit_menu.add_command(
            label="↪️ Redo", command=self._redo, accelerator="Ctrl+Y"
        )
        edit_menu.add_separator()
        edit_menu.add_command(
            label="✂️ Cut", command=self._cut_text, accelerator="Ctrl+X"
        )
        edit_menu.add_command(
            label="📋 Copy", command=self._copy_text, accelerator="Ctrl+C"
        )
        edit_menu.add_command(
            label="📄 Paste", command=self._paste_text, accelerator="Ctrl+V"
        )
        edit_menu.add_separator()
        edit_menu.add_command(
            label="🔍 Find/Replace...",
            command=self._open_find_replace,
            accelerator="Ctrl+F",
        )
        edit_menu.add_command(
            label="🔍 Find Next", command=self._find_next, accelerator="F3"
        )
        edit_menu.add_separator()
        edit_menu.add_command(
            label="💬 Toggle Comment",
            command=self._toggle_comment,
            accelerator="Ctrl+/",
        )
        edit_menu.add_command(
            label="⬅️ Decrease Indent",
            command=self._decrease_indent,
            accelerator="Shift+Tab",
        )
        edit_menu.add_command(
            label="➡️ Increase Indent",
            command=self._increase_indent,
            accelerator="Tab",
        )
        self.menubar.add_cascade(label="Edit", menu=edit_menu)

        # === VIEW MENU === 👁️
        view_menu = tk.Menu(self.menubar, tearoff=0)
        view_menu.add_command(
            label="🔢 Toggle Line Numbers", command=self._toggle_line_numbers
        )
        view_menu.add_separator()
        view_menu.add_command(label="🧹 Clear All", command=self._clear_all)
        view_menu.add_command(
            label="📝 Clear Code Editor", command=self.clear_editor
        )
        view_menu.add_command(
            label="📊 Clear Output", command=self.clear_output
        )
        view_menu.add_command(
            label="🐢 Clear Turtle Graphics", command=self.clear_turtle
        )
        view_menu.add_separator()
        view_menu.add_command(
            label="📝 Switch to Code Editor", command=self.switch_to_editor
        )
        view_menu.add_command(
            label="📊 Switch to Output", command=self.toggle_output_panel
        )
        view_menu.add_command(
            label="🐢 Switch to Turtle Graphics",
            command=self.toggle_turtle_graphics,
        )
        self.menubar.add_cascade(label="View", menu=view_menu)

        # === RUN MENU === ▶️
        run_menu = tk.Menu(self.menubar, tearoff=0)
        run_menu.add_command(
            label="🚀 Run Program", command=self.run_program, accelerator="F5"
        )
        run_menu.add_command(
            label="🛑 Stop Program",
            command=self._stop_program,
            accelerator="Ctrl+Break",
        )
        run_menu.add_separator()
        run_menu.add_command(label="🧪 Run Tests", command=self.run_tests)
        run_menu.add_command(
            label="📝 Check Syntax",
            command=self._check_syntax,
            accelerator="F7",
        )
        run_menu.add_separator()
        run_menu.add_command(
            label="🔄 Restart Interpreter", command=self._restart_interpreter
        )
        self.menubar.add_cascade(label="Run", menu=run_menu)

        # === LANGUAGE MENU === 💻
        lang_menu = tk.Menu(self.menubar, tearoff=0)
        lang_menu.add_command(
            label="⏰ TW BASIC", command=lambda: self._set_language("tw_basic")
        )
        lang_menu.add_command(
            label="Pascal", command=lambda: self._set_language("pascal")
        )
        lang_menu.add_command(
            label="Prolog", command=lambda: self._set_language("prolog")
        )
        lang_menu.add_separator()
        lang_menu.add_command(
            label="🔍 Auto-Detect", command=lambda: self._set_language("auto")
        )
        self.menubar.add_cascade(label="Language", menu=lang_menu)

        # === TOOLS MENU === 🛠️
        tools_menu = tk.Menu(self.menubar, tearoff=0)
        tools_menu.add_command(
            label="🎨 Theme Selector...", command=self.open_theme_selector
        )
        tools_menu.add_command(
            label="🔤 Font Settings...",
            command=lambda: self._open_font_settings(None),
        )
        tools_menu.add_separator()
        tools_menu.add_command(
            label="📦 Plugin Manager", command=self.open_plugin_manager
        )
        tools_menu.add_command(
            label="⚙️ Settings...", command=self._open_settings
        )
        tools_menu.add_separator()

        # Developer Tools submenu
        dev_tools_menu = tk.Menu(tools_menu, tearoff=0)
        dev_tools_menu.add_command(
            label="📊 System Info", command=self._show_system_info
        )
        dev_tools_menu.add_command(
            label="🧪 Test Suite", command=self.run_tests
        )
        dev_tools_menu.add_command(
            label="📋 Generate Report", command=self._generate_report
        )
        tools_menu.add_cascade(label="Developer Tools", menu=dev_tools_menu)

        self.menubar.add_cascade(label="Tools", menu=tools_menu)

        # === HELP MENU === ❓
        help_menu = tk.Menu(self.menubar, tearoff=0)
        help_menu.add_command(
            label="ℹ️ About Time_Warp IDE", command=self.show_about
        )
        help_menu.add_command(
            label="📚 Documentation", command=self.show_documentation
        )
        help_menu.add_command(
            label="🌐 Online Resources", command=self._open_online_resources
        )
        help_menu.add_separator()
        help_menu.add_command(
            label="🆘 Report Issue", command=self._report_issue
        )
        help_menu.add_command(
            label="💡 Feature Request", command=self._feature_request
        )
        help_menu.add_separator()
        help_menu.add_command(
            label="🔄 Check for Updates", command=self._check_updates
        )

        self.menubar.add_cascade(label="Help", menu=help_menu)

        # Toolbar intentionally omitted per user preference (no tab buttons)

        # --- Tabbed Canvas Layout ---
        from tkinter import ttk

        # Main frame for padding and layout
        self.main_frame = tk.Frame(self.root, bg="black")
        self.main_frame.pack(expand=True, fill="both")

        # Create tabbed notebook for dual canvases
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(expand=True, fill="both")

        # Code Editor tab (left)
        self.editor_frame = tk.Frame(self.notebook, bg="#f8f8f8")
        self.code_editor = EnhancedCodeEditor(self.editor_frame)
        self.code_editor.pack(expand=True, fill="both")
        # Backwards-compatibility alias: some code expects `self.editor`
        # so ensure both names reference the same editor instance.
        self.editor = self.code_editor
        self.notebook.add(self.editor_frame, text="Code Editor")

        # Output (UnifiedCanvas) tab (right)
        self.output_frame = tk.Frame(self.notebook, bg="black")
        self.unified_canvas = UnifiedCanvas(
            self.output_frame,
            bg="black",
            relief="flat",
            bd=0,
            font_family=self.selected_font_family,
            font_size=self.selected_font_size,
        )
        # Quick visual sanity checks to ensure canvas is visible
        try:
            # Bind events for basic interactivity
            self.unified_canvas.bind(
                "<Key>", self.unified_canvas._on_key_press
            )
            self.unified_canvas.bind(
                "<Button-1>", self.unified_canvas._on_mouse_click
            )
            self.unified_canvas.bind(
                "<Configure>", self.unified_canvas._on_resize
            )
            self.unified_canvas.bind(
                "<FocusIn>", self.unified_canvas._on_focus_in
            )
            self.unified_canvas.bind(
                "<FocusOut>", self.unified_canvas._on_focus_out
            )
        except Exception:
            pass
        self.unified_canvas.pack(expand=True, fill="both", padx=0, pady=0)
        try:
            # Print a visible message and draw a small rectangle as a sanity check
            self.unified_canvas.write_text(
                "[System] Output console initialized.\n", color=15
            )
            # Draw a small accent rectangle in the top-left corner
            self.unified_canvas.draw_rectangle(
                10,
                10,
                60,
                40,
                filled=True,
                color=self.unified_canvas.current_theme.accent,
            )
        except Exception:
            pass
        self.notebook.add(self.output_frame, text="Output Console")

        # Bind tab change events and set initial focus
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        self.notebook.select(self.editor_frame)
        self.code_editor.focus_set()

        # Make sure the main frame and root allow resizing
        self.root.resizable(True, True)
        self.main_frame.pack_propagate(False)  # Don't shrink to fit contents

        # Set unified canvas reference for interpreters
        self.tw_basic.ide_unified_canvas = self.unified_canvas
        self.pascal.ide_unified_canvas = self.unified_canvas
        self.prolog.ide_unified_canvas = self.unified_canvas

        # Set output widget reference for interpreter logging
        # Use thread-safe UnifiedCanvasOutputHandler which schedules writes via after()
        self.tw_basic.output_widget = UnifiedCanvasOutputHandler(
            self.unified_canvas
        )
        self.pascal.output_widget = UnifiedCanvasOutputHandler(
            self.unified_canvas
        )
        self.prolog.output_widget = UnifiedCanvasOutputHandler(
            self.unified_canvas
        )

        # Create a UI output queue and a poller to flush outputs from background threads
        self._ui_output_queue = queue.Queue()

        # Ensure interpreters always have an output callback that enqueues into the UI queue.
        # This guarantees program output appears in the unified canvas regardless of the entry path.
        def _enqueue_output(text, color=10):
            try:
                # Always enqueue a (text, color) tuple to keep shape consistent
                self._ui_output_queue.put((str(text), color))
            except Exception:
                try:
                    self._ui_output_queue.put((str(text), None))
                except Exception:
                    pass

        try:
            self.tw_basic.set_output_callback(_enqueue_output)
        except Exception:
            pass
        try:
            self.pascal.set_output_callback(_enqueue_output)
        except Exception:
            pass
        try:
            self.prolog.set_output_callback(_enqueue_output)
        except Exception:
            pass

        def _flush_ui_queue():
            try:
                while True:
                    item = self._ui_output_queue.get_nowait()
                    try:
                        # item is expected to be (text, color)
                        if isinstance(item, tuple) and len(item) >= 1:
                            text = item[0]
                            color = item[1] if len(item) > 1 else None
                            # Normalize text: ensure it ends with a single newline so each
                            # queued message appears on its own line in the console.
                            txt = str(text)
                            if not txt.endswith("\n"):
                                txt = txt + "\n"
                            # Write text; UnifiedCanvas will schedule redraws but we also
                            # force a redraw after the flush to make output visible.
                            self.unified_canvas.write_text(txt, color=color)
                        else:
                            self.unified_canvas.write_text(str(item))
                    except Exception:
                        # Ignore write errors to keep UI thread robust
                        pass
            except Exception:
                # queue.Empty or other issues — ignore for now
                pass
            # Schedule next poll
            try:
                self.root.after(50, _flush_ui_queue)
            except Exception:
                pass
            # Force an immediate redraw after flushing the queue to ensure
            # freshly-written text is painted on-screen promptly.
            try:
                self.unified_canvas.redraw()
            except Exception:
                pass

        # Start the UI queue poller
        self.root.after(50, _flush_ui_queue)

        # Set turtle canvas reference (unified canvas acts as turtle canvas too)
        self.tw_basic.ide_turtle_canvas = self.unified_canvas
        self.pascal.ide_turtle_canvas = self.unified_canvas
        self.prolog.ide_turtle_canvas = self.unified_canvas

        # Track when to show OK prompt
        self.show_ok_prompt = True  # Show OK on initial run

        # Schedule welcome screen to show after GUI is fully initialized
        self._welcome_after_id = self.root.after(
            100, self._show_welcome_screen
        )

    def _show_welcome_screen(self):
        """Display the welcome screen with introduction text, memory info, and OK prompt"""
        try:
            import psutil

            memory = psutil.virtual_memory()
            free_memory_kb = memory.available // 1024
            free_memory_mb = free_memory_kb // 1024
            memory_info = (
                f"Free Memory: {free_memory_mb} MB ({free_memory_kb} KB)"
            )
        except ImportError:
            memory_info = "Memory info unavailable (psutil not installed)"

        import platform

        # Clear canvas and set to unified mode
        self.unified_canvas.clear_screen()

        # Display welcome text
        welcome_text = f"""
        Time_Warp IDE v1.3.0 - Educational Programming Environment
        {platform.system()} {platform.release()} - {platform.machine()}

        Supports: TW BASIC, Pascal, Prolog

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
                command_upper = command.upper()
                if command_upper == "HELP":
                    self._show_help()
                elif command_upper in ["CLS", "CLEAR"]:
                    self.unified_canvas.clear_screen()
                    # Show welcome screen after clear
                    self._show_welcome_screen()
                    return
                elif command_upper in ["EXIT", "QUIT", "BYE"]:
                    self.on_closing()
                    return
                else:
                    self._execute_command(command)

            self.root.after(
                100, lambda: self._show_next_prompt(command_callback)
            )

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

        Languages: TW BASIC

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
                current_interpreter = self.get_current_interpreter()
                # Cancel welcome screen if still pending to avoid it overwriting program output
                try:
                    if (
                        hasattr(self, "_welcome_after_id")
                        and self._welcome_after_id
                    ):
                        try:
                            self.root.after_cancel(self._welcome_after_id)
                        except Exception:
                            pass
                        self._welcome_after_id = None
                except Exception:
                    pass
                if current_interpreter.program_lines:
                    # Execute stored program lines in a background thread by calling execute_command
                    def _run_program_lines():
                        try:
                            for line_num, cmd in list(
                                current_interpreter.program_lines
                            ):
                                try:
                                    # Execute each command; interpreter's execute_command should call log_output which
                                    # is wired to enqueue into the UI queue via set_output_callback
                                    current_interpreter.execute_command(cmd)
                                except Exception:
                                    # Continue even if one line errors
                                    pass
                            # Ensure UI reflects completion
                            try:
                                self.root.after(
                                    0,
                                    lambda: self.status_label.config(
                                        text="🚀 Program executed."
                                    ),
                                )
                            except Exception:
                                pass
                        finally:
                            return

                    t = threading.Thread(
                        target=_run_program_lines, daemon=True
                    )
                    t.start()
                    return
                else:
                    self.unified_canvas.write_text(
                        "No program loaded. Enter line-numbered commands first.\n",
                        color=14,
                    )
                    return
            elif command_upper == "LIST":
                # List the stored program (batch output to avoid UI freeze)
                current_interpreter = self.get_current_interpreter()
                if current_interpreter.program_lines:
                    # Clear screen for listing
                    self.unified_canvas.clear_screen()
                    # Build full listing string and write once to minimize redraws
                    output_lines = ["Program:\n"]
                    output_lines.extend(
                        f"{line_num} {cmd}\n"
                        for line_num, cmd in current_interpreter.program_lines
                    )
                    full_output = "".join(output_lines)
                    self.unified_canvas.write_text(full_output, color=15)
                else:
                    self.unified_canvas.write_text(
                        "No program loaded.\n", color=14
                    )
                return
            elif command_upper.startswith("NEW"):
                # Clear the stored program
                current_interpreter = self.get_current_interpreter()
                current_interpreter.program_lines = []
                self.unified_canvas.write_text("Program cleared.\n", color=15)
                return

            # Check if this is a line-numbered program line BEFORE language detection
            command_stripped = command.strip()
            if command_stripped and command_stripped[0].isdigit():
                # This is a program line with line number - store it, don't execute
                try:
                    # Parse line number and command
                    parts = command_stripped.split(
                        None, 1
                    )  # Split on first whitespace
                    line_num = int(parts[0])
                    cmd = parts[1] if len(parts) > 1 else ""

                    if cmd:  # Must have a command after the line number
                        # Update or add the line
                        current_interpreter = self.get_current_interpreter()
                        existing_index = None
                        for i, (existing_num, _) in enumerate(
                            current_interpreter.program_lines
                        ):
                            if existing_num == line_num:
                                existing_index = i
                                break

                        if existing_index is not None:
                            current_interpreter.program_lines[
                                existing_index
                            ] = (line_num, cmd)
                        else:
                            # Insert in line number order
                            insert_pos = 0
                            for i, (existing_num, _) in enumerate(
                                current_interpreter.program_lines
                            ):
                                if existing_num > line_num:
                                    break
                                insert_pos = i + 1
                            current_interpreter.program_lines.insert(
                                insert_pos, (line_num, cmd)
                            )

                        # Line stored silently - no message needed
                        return
                    else:
                        # Invalid line number format - no command after line number
                        self.unified_canvas.write_text(
                            "Invalid line number format - missing command.\n",
                            color=12,
                        )
                        return
                except (ValueError, IndexError):
                    # Invalid line number format
                    self.unified_canvas.write_text(
                        "Invalid line number format.\n", color=12
                    )
                    return

            # Execute as current language command
            current_interpreter = self.get_current_interpreter()
            result = current_interpreter.execute_command(command)
        except Exception as e:
            self.unified_canvas.write_text(f"Error: {str(e)}\n", color=12)

    def _check_syntax(self):
        """Check syntax of code - requires external code input in unified canvas mode"""
        self.unified_canvas.write_text("Syntax check requires code input.\n")
        self.unified_canvas.write_text(
            "Please implement code input mechanism.\n"
        )
        # Update status label if it exists (for compatibility)
        if hasattr(self, "status_label") and self.status_label:
            self.status_label.config(
                text="❌ Syntax check not available in unified canvas mode."
            )

    def _detect_language_from_code(self, code):
        """Detect programming language from code content"""
        lines = code.strip().split("\n")
        if not lines:
            return "time_warp"
        # Simple detection: Pascal and Prolog have unique keywords
        first_lines = "\n".join(lines[:10]).lower()
        if any(
            word in first_lines
            for word in [
                "program ",
                "begin",
                "end.",
                "var ",
                "procedure",
                "function",
            ]
        ):
            return "pascal"
        if any(
            word in first_lines
            for word in [":-", "?-", "listing", "trace", "notrace"]
        ):
            return "prolog"
        return "time_warp"
        # with established language syntax
        time_warp_commands = [
            "FORWARD",
            "BACK",
            "LEFT",
            "RIGHT",
            "PENUP",
            "PENDOWN",
            "CLEARSCREEN",
            "HOME",
            "SETXY",
            "SETCOLOR",
            "SETPENSIZE",
            "CIRCLE",
            "DOT",
            "RECT",
            "TEXT",
            "SHOWTURTLE",
            "HIDETURTLE",
            "REPEAT",
            "DEFINE",
            "CALL",
            "SIN",
            "COS",
            "TAN",
            "SQRT",
            "ABS",
            "INT",
            "RND",
            "LEN",
            "MID",
            "LEFT",
            "RIGHT",
            "UPPER",
            "LOWER",
            "SORT",
            "FIND",
            "SUM",
            "AVG",
            "MIN",
            "MAX",
            "LINE",
            "BOX",
            "TRIANGLE",
            "ELLIPSE",
            "FILL",
            "BEEP",
            "PLAY",
            "SOUND",
            "NOTE",
            "PLAYNOTE",
            "SETSOUND",
            "OPEN",
            "CLOSE",
            "READ",
            "WRITE",
            "EOF",
            "LET",
            "PRINT",
            "INPUT",
            "GOTO",
            "IF",
            "THEN",
            "FOR",
            "TO",
            "NEXT",
        ]

        # Check for single immediate commands first (PRINT, INPUT, LET, variable assignments)
        immediate_commands = ["PRINT", "INPUT", "LET"]
        for cmd in immediate_commands:
            if re.search(r"\b" + re.escape(cmd) + r"\b", code.upper()):
                return "time_warp"

        # Check for exact word matches to avoid substring conflicts
        time_warp_score = 0
        for cmd in time_warp_commands:
            # Use word boundaries to match whole words only
            if re.search(r"\b" + re.escape(cmd) + r"\b", code.upper()):
                time_warp_score += 1

        # If any Time_Warp commands are found, treat as Time_Warp
        if time_warp_score >= 1:
            return "time_warp"

        # Check for variable assignment patterns (var = expr) - only if no other language detected
        # and the assignment looks like Time_Warp syntax (simple variable names)
        if "=" in code and not code.upper().startswith(
            ("IF", "FOR", "WHILE", "LET")
        ):
            # Must look like a variable assignment: identifier = expression
            parts = code.split("=", 1)
            if len(parts) == 2:
                var_part = parts[0].strip()
                expr_part = parts[1].strip()
                # Variable name must be valid identifier, not start with digit, and expression must exist
                # Also check that this doesn't look like other language syntax
                if (
                    var_part.replace("_", "").isalnum()
                    and not var_part[0].isdigit()
                    and var_part
                    and expr_part
                    and not any(
                        char in expr_part
                        for char in ["(", ")", "{", "}", ";", ":"]
                    )
                ):
                    return "time_warp"

        # Default to Time_Warp for immediate commands instead of PILOT
        return "time_warp"

    def _validate_syntax(self, code, language):
        """Validate syntax for the given language"""
        errors = []
        lines = code.split("\n")

        if language == "basic":
            errors = self._validate_basic_syntax(lines)
        elif language == "logo":
            errors = self._validate_logo_syntax(lines)
        elif language == "pilot":
            errors = self._validate_pilot_syntax(lines)
        elif language == "pascal":
            errors = self._validate_pascal_syntax(code)
        elif language == "prolog":
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
            if not line or line.upper().startswith("REM"):
                continue

            # Check for line numbers (optional in this BASIC)
            parts = line.split(None, 1)
            if parts and parts[0].isdigit():
                command = parts[1] if len(parts) > 1 else ""
            else:
                command = line

            # Check for unmatched quotes
            if command.count('"') % 2 != 0:
                errors.append({"line": i, "message": "Unmatched quotes"})

            # Check for THEN without IF
            if "THEN" in command.upper() and "IF" not in command.upper():
                errors.append({"line": i, "message": "THEN without IF"})

        return errors

    # Logo and PILOT syntax validation removed (now unified in TW BASIC)

    def _validate_pascal_syntax(self, code):
        """Validate Pascal syntax (basic checks)"""
        errors = []
        lines = code.split("\n")

        for i, line in enumerate(lines, 1):
            line = line.strip().upper()
            if not line or line.startswith("{") or line.startswith("(*"):
                continue

            # Check for unmatched braces
            open_braces = line.count("(")
            close_braces = line.count(")")
            if open_braces != close_braces:
                errors.append(
                    {
                        "line": i,
                        "message": f"Unmatched parentheses: {open_braces} opening, {close_braces} closing",
                    }
                )

            # Check for semicolons (basic check)
            if (
                line
                and not line.endswith(";")
                and not any(
                    line.endswith(x)
                    for x in ["BEGIN", "END", "THEN", "ELSE", "DO"]
                )
            ):
                if not line.startswith(
                    (
                        "PROGRAM",
                        "VAR",
                        "CONST",
                        "PROCEDURE",
                        "FUNCTION",
                        "BEGIN",
                        "END",
                    )
                ):
                    errors.append({"line": i, "message": "Missing semicolon"})

        return errors

    def _validate_prolog_syntax(self, code):
        """Validate Prolog syntax (basic checks)"""
        errors = []
        lines = code.split("\n")

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith("%"):
                continue

            # Check for unmatched parentheses
            open_parens = line.count("(")
            close_parens = line.count(")")
            if open_parens != close_parens:
                errors.append(
                    {
                        "line": i,
                        "message": f"Unmatched parentheses: {open_parens} opening, {close_parens} closing",
                    }
                )

            # Check for missing period at end
            if line and not line.endswith("."):
                errors.append(
                    {"line": i, "message": "Missing period at end of clause"}
                )

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
                errors.append({"line": i, "message": "Unmatched quotes"})

            # Check for unmatched parentheses
            open_parens = line.count("(")
            close_parens = line.count(")")
            if open_parens != close_parens:
                errors.append(
                    {
                        "line": i,
                        "message": f"Unmatched parentheses: {open_parens} opening, {close_parens} closing",
                    }
                )

        return errors


def main():
    import sys

    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test" and len(sys.argv) >= 4:
            # Run in test mode: python Time_Warp.py --test test_file language
            test_file = sys.argv[2]
            language = sys.argv[3]
            try:
                with open(test_file, "r", encoding="utf-8") as f:
                    code = f.read()
                print(f"Testing {language} code from {test_file}")
                # Use a fresh interpreter instance for test runs to avoid relying on GUI state
                from core.interpreter import Time_WarpInterpreter as _TWI
                _TWI().run_program(code, language=language.lower())
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
    root = tk.Tk()
    app = TimeWarpApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
