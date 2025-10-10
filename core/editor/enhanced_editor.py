"""
Enhanced Code Editor for Time_Warp IDE
Integrates language-specific features with the existing editor
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Optional, Callable, Any
import os
import tempfile

from .language_engine import LanguageEngine
from .code_formatter import CodeFormatter
from .syntax_analyzer import SyntaxAnalyzer, SyntaxError as EditorSyntaxError
from .code_completion import CodeCompletionEngine
from .compiler_manager import CompilerManager


class EnhancedCodeEditor:
    """Enhanced code editor with language-specific features"""

    def __init__(self, parent, initial_language: str = "pilot"):
        self.parent = parent
        self.current_file = None
        self.current_language = initial_language.lower()
        self.is_modified = False

        # Initialize core components
        self.language_engine = LanguageEngine()
        self.code_formatter = CodeFormatter(self.language_engine)
        self.syntax_analyzer = SyntaxAnalyzer(self.language_engine)
        self.compiler_manager = CompilerManager()

        # Set initial language
        self.language_engine.set_language(self.current_language)

        # Initialize editor variables (needed even when toolbar is disabled)
        self.language_var = tk.StringVar(value=self.current_language.upper())
        self.syntax_highlight_var = tk.BooleanVar(value=True)
        self.auto_complete_var = tk.BooleanVar(value=True)
        self.syntax_check_var = tk.BooleanVar(value=True)
        self.auto_format_var = tk.BooleanVar(value=True)

        # Setup UI
        self.setup_editor()
        self.setup_advanced_features()

        # Callbacks
        self.output_callback: Optional[Callable[[str], None]] = None
        self.status_callback: Optional[Callable[[str], None]] = None
        self.menu_update_callback: Optional[Callable[[], None]] = None

    def setup_editor(self):
        """Setup the main editor interface"""
        # Main container
        self.container = ttk.Frame(self.parent)
        self.container.pack(fill=tk.BOTH, expand=True)

        # Toolbar disabled - controlled by main Time_Warp interface
        # self.create_enhanced_toolbar()

        # Create main editor area
        self.create_editor_area()

        # Create status bar
        self.create_enhanced_status_bar()

    def create_enhanced_toolbar(self):
        """Create enhanced toolbar with language-specific options"""
        toolbar = ttk.Frame(self.container)
        toolbar.pack(fill=tk.X, padx=5, pady=2)

        # Language selection
        ttk.Label(toolbar, text="Language:").pack(side=tk.LEFT, padx=(0, 5))

        language_combo = ttk.Combobox(
            toolbar,
            textvariable=self.language_var,
            values=["PILOT", "BASIC", "Logo", "Python", "JavaScript", "Perl"],
            state="readonly",
            width=12,
        )
        language_combo.pack(side=tk.LEFT, padx=(0, 10))
        language_combo.bind("<<ComboboxSelected>>", self.on_language_change)

        # Separator
        ttk.Separator(toolbar, orient="vertical").pack(side=tk.LEFT, padx=5, fill=tk.Y)

        # Editor features
        self.syntax_highlight_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            toolbar,
            text="Syntax Highlighting",
            variable=self.syntax_highlight_var,
            command=self.toggle_syntax_highlighting,
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.auto_complete_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            toolbar,
            text="Auto Complete",
            variable=self.auto_complete_var,
            command=self.toggle_auto_complete,
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.syntax_check_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            toolbar,
            text="Syntax Check",
            variable=self.syntax_check_var,
            command=self.toggle_syntax_check,
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.auto_format_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            toolbar, text="Auto Format", variable=self.auto_format_var
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Separator
        ttk.Separator(toolbar, orient="vertical").pack(side=tk.LEFT, padx=5, fill=tk.Y)

        # Compilation controls
        self.compile_button = ttk.Button(
            toolbar,
            text="🔨 Compile",
            command=self.compile_current_file,
            state="disabled",
        )
        self.compile_button.pack(side=tk.LEFT, padx=2)

        self.compile_run_button = ttk.Button(
            toolbar,
            text="🚀 Compile & Run",
            command=self.compile_and_run,
            state="disabled",
        )
        self.compile_run_button.pack(side=tk.LEFT, padx=2)

        # Separator
        ttk.Separator(toolbar, orient="vertical").pack(side=tk.LEFT, padx=5, fill=tk.Y)

        # Formatting controls
        ttk.Button(toolbar, text="🎨 Format", command=self.format_current_file).pack(
            side=tk.LEFT, padx=2
        )

        ttk.Button(toolbar, text="🔍 Check Syntax", command=self.check_syntax_now).pack(
            side=tk.LEFT, padx=2
        )

    def create_editor_area(self):
        """Create the main editor area - clean editor without line numbers panel"""
        # Editor container
        editor_container = ttk.Frame(self.container)
        editor_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Vertical scrollbar
        v_scrollbar = ttk.Scrollbar(editor_container, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(editor_container, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Main text editor - full width, no side panels
        self.text_editor = tk.Text(
            editor_container,
            font=("Courier", 10),
            undo=True,
            maxundo=50,
            bg="white",
            fg="black",
            insertbackground="black",
            selectbackground="lightblue",
            wrap=tk.NONE,
        )
        self.text_editor.pack(fill=tk.BOTH, expand=True)

        # Connect scrollbars to text editor
        v_scrollbar.configure(command=self.text_editor.yview)
        h_scrollbar.configure(command=self.text_editor.xview)
        self.text_editor.configure(
            yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set
        )

        # Bind events
        self.text_editor.bind("<KeyPress>", self.on_key_press)
        self.text_editor.bind("<KeyRelease>", self.on_key_release)
        self.text_editor.bind("<Button-1>", self.on_click)
        self.text_editor.bind("<Control-s>", lambda e: self.save_file())
        self.text_editor.bind("<Control-o>", lambda e: self.open_file())
        self.text_editor.bind("<Control-n>", lambda e: self.new_file())
        self.text_editor.bind("<Control-f>", lambda e: self.find_text())
        self.text_editor.bind("<Control-h>", lambda e: self.replace_text())
        self.text_editor.bind("<Control-space>", lambda e: self.show_completions())
        self.text_editor.bind("<F5>", lambda e: self.run_current_file())

        # Update line numbers initially
        self.update_line_numbers()

    def create_enhanced_status_bar(self):
        """Create enhanced status bar"""
        status_frame = ttk.Frame(self.container)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # Left side - general status
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.pack(side=tk.LEFT, padx=5)

        # Language indicator
        self.language_label = ttk.Label(
            status_frame, text=f"Language: {self.current_language.upper()}"
        )
        self.language_label.pack(side=tk.LEFT, padx=10)

        # Error count
        self.error_label = ttk.Label(status_frame, text="Errors: 0")
        self.error_label.pack(side=tk.LEFT, padx=10)

        # Right side - position
        self.cursor_label = ttk.Label(status_frame, text="Line 1, Col 1")
        self.cursor_label.pack(side=tk.RIGHT, padx=5)

        # File indicator
        self.file_label = ttk.Label(status_frame, text="Untitled")
        self.file_label.pack(side=tk.RIGHT, padx=10)

    def setup_advanced_features(self):
        """Setup advanced editor features"""
        # Code completion
        self.completion_engine = CodeCompletionEngine(
            self.text_editor, self.language_engine
        )

        # Syntax analyzer callback
        self.syntax_analyzer.set_error_callback(self.on_syntax_errors)

        # Compiler manager callback
        self.compiler_manager.set_output_callback(self.on_compiler_output)

        # Setup syntax highlighting tags
        self.setup_syntax_tags()

        # Update compilation buttons
        self.update_compilation_buttons()

    def setup_syntax_tags(self):
        """Setup syntax highlighting tags"""
        # Keywords
        self.text_editor.tag_configure(
            "keyword", foreground="#0000FF", font=("Courier", 10, "bold")
        )

        # Comments
        self.text_editor.tag_configure(
            "comment", foreground="#008000", font=("Courier", 10, "italic")
        )

        # Strings
        self.text_editor.tag_configure("string", foreground="#FF0000")

        # Numbers
        self.text_editor.tag_configure("number", foreground="#800080")

        # Operators
        self.text_editor.tag_configure("operator", foreground="#FF8000")

        # Errors
        self.text_editor.tag_configure(
            "error", background="#FFCCCC", foreground="#CC0000"
        )

        # Warnings
        self.text_editor.tag_configure(
            "warning", background="#FFFFCC", foreground="#CC8800"
        )

        # Variables (PILOT)
        self.text_editor.tag_configure("variable", foreground="#8000FF")

        # Labels (PILOT)
        self.text_editor.tag_configure(
            "label", foreground="#FF0080", font=("Courier", 10, "bold")
        )

    def on_language_change(self, event=None):
        """Handle language change"""
        new_language = self.language_var.get().lower()
        if new_language != self.current_language:
            self.current_language = new_language
            self.language_engine.set_language(new_language)

            # Update UI
            self.language_label.config(text=f"Language: {new_language.upper()}")
            self.update_compilation_buttons()

            # Re-analyze syntax
            if self.syntax_check_var.get():
                self.check_syntax_now()

            # Re-highlight syntax
            if self.syntax_highlight_var.get():
                self.highlight_syntax()

            # Update status
            self.update_status(f"Language changed to {new_language.upper()}")

            # Notify main application of language change
            if self.menu_update_callback:
                self.menu_update_callback()

    def on_key_press(self, event):
        """Handle key press events"""
        self.is_modified = True

        # Handle special formatting
        if self.auto_format_var.get() and event.char in ["\n", ":", "}", ")", "]"]:
            # Schedule format-on-type
            self.text_editor.after(10, lambda: self.format_on_type(event.char))

    def on_key_release(self, event):
        """Handle key release events"""
        # Update line numbers
        self.text_editor.after_idle(self.update_line_numbers)

        # Update cursor position
        self.update_cursor_position()

        # Schedule syntax highlighting
        if self.syntax_highlight_var.get():
            self.text_editor.after(200, self.highlight_syntax)

        # Schedule syntax checking
        if self.syntax_check_var.get():
            self.text_editor.after(500, self.check_syntax_delayed)

    def on_click(self, event):
        """Handle mouse click"""
        self.update_cursor_position()

    def update_line_numbers(self):
        """Line numbers removed - this method is now a no-op"""
        pass

    def update_cursor_position(self):
        """Update cursor position in status bar"""
        cursor_pos = self.text_editor.index(tk.INSERT)
        line, col = cursor_pos.split(".")
        self.cursor_label.config(text=f"Line {line}, Col {int(col) + 1}")

    def highlight_syntax(self):
        """Perform syntax highlighting"""
        if not self.syntax_highlight_var.get():
            return

        # Clear existing tags
        for tag in [
            "keyword",
            "comment",
            "string",
            "number",
            "operator",
            "variable",
            "label",
        ]:
            self.text_editor.tag_remove(tag, "1.0", tk.END)

        # Get text and highlights
        text = self.text_editor.get("1.0", tk.END)
        highlights = self.language_engine.get_syntax_highlights(text)

        # Apply highlights
        for tag, start, end in highlights:
            start_pos = self._offset_to_index(text, start)
            end_pos = self._offset_to_index(text, end)
            self.text_editor.tag_add(tag, start_pos, end_pos)

    def _offset_to_index(self, text: str, offset: int) -> str:
        """Convert byte offset to Tkinter text index"""
        lines = text[:offset].split("\n")
        line_num = len(lines)
        col_num = len(lines[-1]) if lines else 0
        return f"{line_num}.{col_num}"

    def check_syntax_delayed(self):
        """Check syntax with delay (called from key events)"""
        if self.syntax_check_var.get():
            text = self.text_editor.get("1.0", tk.END)
            self.syntax_analyzer.analyze_syntax(text, self.current_language)

    def check_syntax_now(self):
        """Check syntax immediately"""
        text = self.text_editor.get("1.0", tk.END)
        errors = self.syntax_analyzer.analyze_syntax(
            text, self.current_language, immediate=True
        )
        self.on_syntax_errors(errors)

    def on_syntax_errors(self, errors: List[EditorSyntaxError]):
        """Handle syntax errors from analyzer"""
        # Clear existing error tags
        self.text_editor.tag_remove("error", "1.0", tk.END)
        self.text_editor.tag_remove("warning", "1.0", tk.END)

        # Apply error highlighting
        for error in errors:
            line_start = f"{error.line}.0"
            line_end = f"{error.line}.end"

            if error.error_type == "error":
                self.text_editor.tag_add("error", line_start, line_end)
            elif error.error_type == "warning":
                self.text_editor.tag_add("warning", line_start, line_end)

        # Update status
        error_count = len([e for e in errors if e.error_type == "error"])
        warning_count = len([e for e in errors if e.error_type == "warning"])

        if error_count > 0:
            self.error_label.config(text=f"Errors: {error_count}")
        elif warning_count > 0:
            self.error_label.config(text=f"Warnings: {warning_count}")
        else:
            self.error_label.config(text="No errors")

    def format_current_file(self):
        """Format the current file"""
        text = self.text_editor.get("1.0", tk.END)
        formatted_text = self.code_formatter.format_code(text, self.current_language)

        if formatted_text != text:
            # Save cursor position
            cursor_pos = self.text_editor.index(tk.INSERT)

            # Replace text
            self.text_editor.delete("1.0", tk.END)
            self.text_editor.insert("1.0", formatted_text)

            # Restore cursor position (approximately)
            try:
                self.text_editor.mark_set(tk.INSERT, cursor_pos)
            except tk.TclError:
                pass

            # Re-highlight syntax
            if self.syntax_highlight_var.get():
                self.highlight_syntax()

            self.update_status("Code formatted")
        else:
            self.update_status("No formatting changes needed")

    def format_on_type(self, char: str):
        """Format code as user types"""
        if not self.auto_format_var.get():
            return

        cursor_pos = self.text_editor.index(tk.INSERT)
        text = self.text_editor.get("1.0", tk.END)
        cursor_offset = len(self.text_editor.get("1.0", cursor_pos).encode("utf-8"))

        formatted_text = self.code_formatter.format_on_type(
            text, cursor_offset, char, self.current_language
        )

        if formatted_text and formatted_text != text:
            # Replace text and restore cursor
            self.text_editor.delete("1.0", tk.END)
            self.text_editor.insert("1.0", formatted_text)
            self.text_editor.mark_set(tk.INSERT, cursor_pos)

    def show_completions(self):
        """Show code completions"""
        if self.auto_complete_var.get():
            self.completion_engine.show_completions(force=True)

    def compile_current_file(self):
        """Compile current file"""
        if not self.compiler_manager.supports_language(self.current_language):
            self.update_status(f"Compilation not supported for {self.current_language}")
            return

        # Save file if modified
        if self.is_modified:
            if not self.save_file():
                return

        if self.current_file:
            result = self.compiler_manager.compile_file(
                self.current_file, self.current_language
            )
            if result.success:
                self.update_status(f"Compilation successful: {result.executable_path}")
            else:
                self.update_status(f"Compilation failed: {result.error}")
        else:
            # Compile text content
            text = self.text_editor.get("1.0", tk.END)
            result = self.compiler_manager.compile_text(
                text, self.current_language, "temp"
            )
            if result.success:
                self.update_status(f"Compilation successful: {result.executable_path}")
            else:
                self.update_status(f"Compilation failed: {result.error}")

    def compile_and_run(self):
        """Compile and run current file"""
        if not self.compiler_manager.supports_language(self.current_language):
            self.update_status(f"Compilation not supported for {self.current_language}")
            return

        # First compile
        self.compile_current_file()

        # Then run if compilation successful
        # This would be enhanced to check compilation result
        self.text_editor.after(1000, self.run_compiled_program)

    def run_compiled_program(self):
        """Run the compiled program"""
        # Find the compiled file
        if self.current_file:
            compiled_file = self.current_file + "_compiled"
        else:
            compiled_file = f"temp_{self.current_language}_compiled"

        if os.path.exists(compiled_file):
            self.compiler_manager.run_compiled_program(compiled_file)
        else:
            self.update_status("No compiled program found")

    def run_current_file(self):
        """Run current file (interpreter mode)"""
        if self.output_callback:
            text = self.text_editor.get("1.0", tk.END)
            self.output_callback(f"🚀 Running {self.current_language.upper()} code...")
            # This would integrate with the main Time_Warp interpreter

    def update_compilation_buttons(self):
        """Update compilation button states"""
        # Check if buttons exist (they may not if toolbar is disabled)
        if not hasattr(self, "compile_button") or not hasattr(
            self, "compile_run_button"
        ):
            return

        if self.compiler_manager.supports_language(self.current_language):
            self.compile_button.config(state="normal")
            self.compile_run_button.config(state="normal")
        else:
            self.compile_button.config(state="disabled")
            self.compile_run_button.config(state="disabled")

    def on_compiler_output(self, message: str):
        """Handle compiler output"""
        if self.output_callback:
            self.output_callback(message)

    def toggle_syntax_highlighting(self):
        """Toggle syntax highlighting"""
        if self.syntax_highlight_var.get():
            self.highlight_syntax()
            self.update_status("Syntax highlighting enabled")
        else:
            # Clear all tags
            for tag in [
                "keyword",
                "comment",
                "string",
                "number",
                "operator",
                "variable",
                "label",
            ]:
                self.text_editor.tag_remove(tag, "1.0", tk.END)
            self.update_status("Syntax highlighting disabled")

    def toggle_auto_complete(self):
        """Toggle auto completion"""
        if self.auto_complete_var.get():
            self.update_status("Auto completion enabled")
        else:
            self.completion_engine.hide_completions()
            self.update_status("Auto completion disabled")

    def toggle_syntax_check(self):
        """Toggle syntax checking"""
        if self.syntax_check_var.get():
            self.check_syntax_now()
            self.update_status("Syntax checking enabled")
        else:
            self.syntax_analyzer.clear_analysis()
            self.text_editor.tag_remove("error", "1.0", tk.END)
            self.text_editor.tag_remove("warning", "1.0", tk.END)
            self.error_label.config(text="Syntax check disabled")
            self.update_status("Syntax checking disabled")

    # File operations
    def new_file(self):
        """Create new file"""
        if self.is_modified:
            if not self.confirm_save_changes():
                return

        self.text_editor.delete("1.0", tk.END)
        self.current_file = None
        self.is_modified = False
        self.file_label.config(text="Untitled")
        self.update_status("New file created")

    def open_file(self):
        """Open file"""
        from tkinter import filedialog

        if self.is_modified:
            if not self.confirm_save_changes():
                return

        # Get appropriate file types based on current language
        engine = self.language_engine.get_current_engine()
        if engine:
            extensions = engine.config.extensions
            filetypes = [
                (f"{engine.config.name} Files", f"*{ext}") for ext in extensions
            ]
            filetypes.append(("All Files", "*.*"))
        else:
            filetypes = [("All Files", "*.*")]

        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    content = f.read()

                self.text_editor.delete("1.0", tk.END)
                self.text_editor.insert("1.0", content)
                self.current_file = filename
                self.is_modified = False
                self.file_label.config(text=os.path.basename(filename))

                # Auto-detect language from file extension
                ext = os.path.splitext(filename)[1]
                if ext == ".pilot":
                    self.language_var.set("PILOT")
                elif ext in [".bas", ".basic"]:
                    self.language_var.set("BASIC")
                elif ext in [".logo", ".lg"]:
                    self.language_var.set("Logo")
                elif ext == ".py":
                    self.language_var.set("Python")

                self.on_language_change()
                self.update_status(f"Opened {filename}")

            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")

    def save_file(self) -> bool:
        """Save current file"""
        if self.current_file:
            try:
                with open(self.current_file, "w", encoding="utf-8") as f:
                    f.write(self.text_editor.get("1.0", tk.END + "-1c"))

                self.is_modified = False
                self.update_status(f"Saved {self.current_file}")
                return True

            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")
                return False
        else:
            return self.save_file_as()

    def save_file_as(self) -> bool:
        """Save file with new name"""
        from tkinter import filedialog

        # Get appropriate file types
        engine = self.language_engine.get_current_engine()
        if engine:
            extensions = engine.config.extensions
            filetypes = [
                (f"{engine.config.name} Files", f"*{ext}") for ext in extensions
            ]
            filetypes.append(("All Files", "*.*"))
            default_ext = extensions[0] if extensions else ".txt"
        else:
            filetypes = [("All Files", "*.*")]
            default_ext = ".txt"

        filename = filedialog.asksaveasfilename(
            filetypes=filetypes, defaultextension=default_ext
        )

        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(self.text_editor.get("1.0", tk.END + "-1c"))

                self.current_file = filename
                self.is_modified = False
                self.file_label.config(text=os.path.basename(filename))
                self.update_status(f"Saved as {filename}")
                return True

            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")
                return False

        return False

    def confirm_save_changes(self) -> bool:
        """Confirm save changes dialog"""
        if self.is_modified:
            result = messagebox.askyesnocancel(
                "Save Changes",
                "The current file has unsaved changes. Do you want to save them?",
            )
            if result is True:  # Yes
                return self.save_file()
            elif result is False:  # No
                return True
            else:  # Cancel
                return False
        return True

    def find_text(self):
        """Open find dialog"""
        # This would open a find dialog
        self.update_status("Find dialog would open here")

    def replace_text(self):
        """Open replace dialog"""
        # This would open a replace dialog
        self.update_status("Replace dialog would open here")

    def update_status(self, message: str):
        """Update status bar"""
        self.status_label.config(text=message)
        if self.status_callback:
            self.status_callback(message)

        # Clear status after 3 seconds
        self.text_editor.after(3000, lambda: self.status_label.config(text="Ready"))

    def set_output_callback(self, callback: Callable[[str], None]):
        """Set callback for output messages"""
        self.output_callback = callback

    def set_status_callback(self, callback: Callable[[str], None]):
        """Set callback for status messages"""
        self.status_callback = callback

    def set_menu_update_callback(self, callback: Callable[[], None]):
        """Set callback for menu updates"""
        self.menu_update_callback = callback

    def get_content(self) -> str:
        """Get editor content"""
        return self.text_editor.get("1.0", tk.END + "-1c")

    def set_content(self, content: str):
        """Set editor content"""
        self.text_editor.delete("1.0", tk.END)
        self.text_editor.insert("1.0", content)
        self.is_modified = True
        self.update_line_numbers()

        if self.syntax_highlight_var.get():
            self.highlight_syntax()

    def get_current_language(self) -> str:
        """Get current language"""
        return self.current_language

    def set_language(self, language: str):
        """Set current language"""
        self.language_var.set(language.upper())
        self.on_language_change()

    def get_compilation_menu_items(self) -> List[Dict[str, Any]]:
        """Get compilation menu items for current language"""
        return self.compiler_manager.get_compilation_menu_items()

    # Compatibility methods for existing Time_Warp.py integration
    def clear_content(self):
        """Clear editor content - compatibility method"""
        self.text_editor.delete("1.0", tk.END)
        self.is_modified = False
        self.update_line_numbers()

    def show_find_dialog(self):
        """Show find dialog - compatibility method"""
        self.find_text()

    def show_replace_dialog(self):
        """Show replace dialog - compatibility method"""
        self.replace_text()
