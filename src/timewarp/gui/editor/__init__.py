"""
Advanced Code Editor Module
Main editor class that integrates syntax highlighting, auto-completion, and other features.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from .features import (
    AdvancedSyntaxHighlighter,
    AutoCompletionEngine,
    IntelligentCodeCompletion,
    RealTimeSyntaxChecker,
    CodeFoldingSystem,
)


class AdvancedCodeEditor:
    """Advanced code editor with syntax highlighting, auto-completion, and error checking"""

    def __init__(self, parent):
        self.parent = parent
        self.current_language = "pilot"
        self.setup_editor()
        self.setup_features()

    def setup_editor(self):
        """Setup the main editor interface"""
        # Create main frame
        self.editor_frame = ttk.Frame(self.parent)
        self.editor_frame.pack(fill=tk.BOTH, expand=True)

        # Create toolbar
        self.create_toolbar()

        # Create text editor with line numbers
        self.create_text_editor()

        # Create status bar
        self.create_status_bar()

    def create_toolbar(self):
        """Create editor toolbar"""
        toolbar = ttk.Frame(self.editor_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=2)

        # Language selection
        ttk.Label(toolbar, text="Language:").pack(side=tk.LEFT, padx=(0, 5))

        self.language_var = tk.StringVar(value="PILOT")
        language_combo = ttk.Combobox(
            toolbar,
            textvariable=self.language_var,
            values=["PILOT", "BASIC", "Logo", "Python", "Perl", "JavaScript"],
            state="readonly",
            width=12,
        )
        language_combo.pack(side=tk.LEFT, padx=(0, 10))
        language_combo.bind("<<ComboboxSelected>>", self.on_language_change)

        # Editor options
        self.syntax_highlight_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            toolbar,
            text="Syntax Highlighting",
            variable=self.syntax_highlight_var,
            command=self.toggle_syntax_highlighting,
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.auto_complete_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            toolbar,
            text="Auto Complete",
            variable=self.auto_complete_var,
            command=self.toggle_auto_complete,
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.syntax_check_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            toolbar,
            text="Syntax Check",
            variable=self.syntax_check_var,
            command=self.toggle_syntax_check,
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Fold/Unfold buttons
        ttk.Button(toolbar, text="Fold All", command=self.fold_all).pack(
            side=tk.RIGHT, padx=(5, 0)
        )
        ttk.Button(toolbar, text="Unfold All", command=self.unfold_all).pack(
            side=tk.RIGHT, padx=(5, 0)
        )

    def create_text_editor(self):
        """Create the main text editor with line numbers"""
        # Create frame for editor and line numbers
        editor_container = ttk.Frame(self.editor_frame)
        editor_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Line numbers frame
        self.line_numbers_frame = tk.Frame(editor_container, width=50, bg="lightgray")
        self.line_numbers_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Line numbers text widget
        self.line_numbers = tk.Text(
            self.line_numbers_frame,
            width=4,
            padx=3,
            takefocus=0,
            border=0,
            state="disabled",
            bg="lightgray",
            fg="black",
            font=("Courier", 10),
        )
        self.line_numbers.pack(side=tk.TOP, fill=tk.Y)

        # Main text editor
        self.text_editor = scrolledtext.ScrolledText(
            editor_container,
            wrap=tk.NONE,
            font=("Courier", 10),
            undo=True,
            maxundo=50,
            bg="white",
            fg="black",
            insertbackground="black",
            selectbackground="lightblue",
        )
        self.text_editor.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Bind events
        self.text_editor.bind("<KeyPress>", self.on_key_press)
        self.text_editor.bind("<KeyRelease>", self.on_key_release)
        self.text_editor.bind("<Button-1>", self.on_click)
        self.text_editor.bind("<Control-space>", self.show_completions)
        self.text_editor.bind("<MouseWheel>", self.sync_scrollbars)
        self.text_editor.bind("<Control-Key>", self.on_control_key)

        # Sync scrollbars
        self.text_editor.vbar.config(command=self.on_scroll)

        # Update line numbers initially
        self.update_line_numbers()

    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = ttk.Frame(self.editor_frame)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_label = ttk.Label(self.status_bar, text="Ready")
        self.status_label.pack(side=tk.LEFT, padx=5)

        self.cursor_label = ttk.Label(self.status_bar, text="Line 1, Col 1")
        self.cursor_label.pack(side=tk.RIGHT, padx=5)

    def setup_features(self):
        """Setup advanced editor features"""
        # Syntax highlighter
        self.syntax_highlighter = AdvancedSyntaxHighlighter(self.text_editor)

        # Auto-completion engine
        self.auto_completion = AutoCompletionEngine(self.text_editor)

        # Intelligent completion
        self.intelligent_completion = IntelligentCodeCompletion(self.text_editor)

        # Syntax checker
        self.syntax_checker = RealTimeSyntaxChecker(self.text_editor)

        # Code folding
        self.code_folding = CodeFoldingSystem(self.text_editor)
        self.code_folding.setup_folding()

    def on_language_change(self, event=None):
        """Handle language selection change"""
        self.current_language = self.language_var.get().lower()
        self.update_status(f"Language changed to {self.language_var.get()}")

        # Re-highlight syntax
        if self.syntax_highlight_var.get():
            self.syntax_highlighter.highlight_syntax()

    def on_key_press(self, event):
        """Handle key press events"""
        # Auto-completion triggers
        if event.char.isalnum() or event.char in "._:":
            if self.auto_complete_var.get():
                self.text_editor.after(100, self.check_auto_complete)

        # Special key combinations
        if event.state & 0x4:  # Control key
            if event.keysym == "space":
                self.show_completions()
                return "break"
            elif event.keysym == "s":
                self.save_file()
                return "break"
            elif event.keysym == "o":
                self.open_file()
                return "break"

    def on_key_release(self, event):
        """Handle key release events"""
        # Update line numbers
        self.text_editor.after_idle(self.update_line_numbers)

        # Update cursor position
        self.update_cursor_position()

        # Syntax highlighting
        if self.syntax_highlight_var.get():
            self.text_editor.after(200, self.syntax_highlighter.highlight_syntax)

        # Syntax checking
        if self.syntax_check_var.get():
            self.text_editor.after(500, self.syntax_checker.check_syntax)

    def on_click(self, event):
        """Handle mouse click events"""
        self.update_cursor_position()

    def on_control_key(self, event):
        """Handle control key combinations"""
        if event.keysym == "f":
            self.show_find_dialog()
        elif event.keysym == "h":
            self.show_replace_dialog()
        elif event.keysym == "g":
            self.show_goto_dialog()

    def check_auto_complete(self):
        """Check if auto-completion should be shown"""
        cursor_pos = self.text_editor.index(tk.INSERT)
        line_start = cursor_pos.split(".")[0] + ".0"
        current_line = self.text_editor.get(line_start, cursor_pos)

        # Show completion if typing a word
        if len(current_line) > 0 and current_line[-1].isalnum():
            word_start = len(current_line) - 1
            while word_start > 0 and (
                current_line[word_start].isalnum() or current_line[word_start] in "_:"
            ):
                word_start -= 1

            current_word = current_line[word_start:].strip()
            if len(current_word) >= 2:
                self.auto_completion.show_completions()

    def show_completions(self, event=None):
        """Show completion popup"""
        self.auto_completion.show_completions()

    def update_line_numbers(self):
        """Update line numbers display"""
        content = self.text_editor.get("1.0", tk.END)
        lines = content.count("\n")

        line_numbers_content = "\n".join(str(i) for i in range(1, lines + 1))

        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", tk.END)
        self.line_numbers.insert("1.0", line_numbers_content)
        self.line_numbers.config(state="disabled")

    def update_cursor_position(self):
        """Update cursor position in status bar"""
        cursor_pos = self.text_editor.index(tk.INSERT)
        line, col = cursor_pos.split(".")
        self.cursor_label.config(text=f"Line {line}, Col {int(col) + 1}")

    def sync_scrollbars(self, event):
        """Sync line numbers with text editor scrolling"""
        self.line_numbers.yview_moveto(self.text_editor.yview()[0])

    def on_scroll(self, *args):
        """Handle scrollbar events"""
        self.text_editor.yview(*args)
        self.line_numbers.yview(*args)

    def toggle_syntax_highlighting(self):
        """Toggle syntax highlighting"""
        if self.syntax_highlight_var.get():
            self.syntax_highlighter.highlight_syntax()
            self.update_status("Syntax highlighting enabled")
        else:
            # Clear all syntax tags
            tags = [
                "pilot_command",
                "pilot_label",
                "pilot_variable",
                "logo_command",
                "logo_procedure",
                "logo_number",
                "basic_keyword",
                "basic_number",
                "basic_string",
                "python_keyword",
                "python_string",
                "python_comment",
                "comment",
                "error",
            ]
            for tag in tags:
                self.text_editor.tag_remove(tag, "1.0", tk.END)
            self.update_status("Syntax highlighting disabled")

    def toggle_auto_complete(self):
        """Toggle auto-completion"""
        if self.auto_complete_var.get():
            self.update_status("Auto-completion enabled")
        else:
            self.auto_completion.hide_completion_popup()
            self.update_status("Auto-completion disabled")

    def toggle_syntax_check(self):
        """Toggle syntax checking"""
        if self.syntax_check_var.get():
            self.syntax_checker.check_syntax()
            self.update_status("Syntax checking enabled")
        else:
            self.syntax_checker.clear_error_markers()
            self.update_status("Syntax checking disabled")

    def fold_all(self):
        """Fold all code regions"""
        regions = self.code_folding.find_foldable_regions()
        for start, end in regions:
            self.code_folding.fold_region(start, end)
        self.update_status(f"Folded {len(regions)} regions")

    def unfold_all(self):
        """Unfold all code regions"""
        folded_count = len(self.code_folding.folded_regions)
        for region_id in list(self.code_folding.folded_regions.keys()):
            start, end = map(int, region_id.split("_"))
            self.code_folding.unfold_region(start, end)
        self.update_status(f"Unfolded {folded_count} regions")

    def show_find_dialog(self):
        """Show find dialog"""
        find_dialog = FindDialog(self.text_editor)

    def show_replace_dialog(self):
        """Show find/replace dialog"""
        replace_dialog = ReplaceDialog(self.text_editor)

    def show_goto_dialog(self):
        """Show go to line dialog"""
        goto_dialog = GotoDialog(self.text_editor)

    def save_file(self):
        """Save current file"""
        # This would integrate with file system
        self.update_status("File saved")

    def open_file(self):
        """Open file"""
        # This would integrate with file system
        self.update_status("File opened")

    def update_status(self, message):
        """Update status bar message"""
        self.status_label.config(text=message)
        # Clear message after 3 seconds
        self.text_editor.after(3000, lambda: self.status_label.config(text="Ready"))

    def get_content(self):
        """Get editor content"""
        return self.text_editor.get("1.0", tk.END)

    def set_content(self, content):
        """Set editor content"""
        self.text_editor.delete("1.0", tk.END)
        self.text_editor.insert("1.0", content)
        self.update_line_numbers()

        if self.syntax_highlight_var.get():
            self.syntax_highlighter.highlight_syntax()

    def clear_content(self):
        """Clear editor content"""
        self.text_editor.delete("1.0", tk.END)
        self.update_line_numbers()

    def insert_text(self, text):
        """Insert text at cursor position"""
        self.text_editor.insert(tk.INSERT, text)
        if self.syntax_highlight_var.get():
            self.text_editor.after(100, self.syntax_highlighter.highlight_syntax)


class FindDialog:
    """Find dialog for text searching"""

    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.create_dialog()

    def create_dialog(self):
        """Create find dialog"""
        self.dialog = tk.Toplevel()
        self.dialog.title("Find")
        self.dialog.geometry("300x100")
        self.dialog.resizable(False, False)

        # Find entry
        ttk.Label(self.dialog, text="Find:").pack(pady=5)
        self.find_entry = ttk.Entry(self.dialog, width=30)
        self.find_entry.pack(pady=5)
        self.find_entry.focus()

        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Find Next", command=self.find_next).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(
            side=tk.LEFT, padx=5
        )

        # Bind Enter key
        self.find_entry.bind("<Return>", lambda e: self.find_next())

    def find_next(self):
        """Find next occurrence"""
        search_text = self.find_entry.get()
        if not search_text:
            return

        # Start search from current cursor position
        start_pos = self.text_widget.index(tk.INSERT)
        found_pos = self.text_widget.search(search_text, start_pos, tk.END)

        if found_pos:
            # Select found text
            end_pos = f"{found_pos}+{len(search_text)}c"
            self.text_widget.tag_remove(tk.SEL, "1.0", tk.END)
            self.text_widget.tag_add(tk.SEL, found_pos, end_pos)
            self.text_widget.mark_set(tk.INSERT, end_pos)
            self.text_widget.see(found_pos)
        else:
            # Search from beginning
            found_pos = self.text_widget.search(search_text, "1.0", start_pos)
            if found_pos:
                end_pos = f"{found_pos}+{len(search_text)}c"
                self.text_widget.tag_remove(tk.SEL, "1.0", tk.END)
                self.text_widget.tag_add(tk.SEL, found_pos, end_pos)
                self.text_widget.mark_set(tk.INSERT, end_pos)
                self.text_widget.see(found_pos)
            else:
                messagebox.showinfo("Find", f"'{search_text}' not found")


class ReplaceDialog:
    """Find and replace dialog"""

    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.create_dialog()

    def create_dialog(self):
        """Create replace dialog"""
        self.dialog = tk.Toplevel()
        self.dialog.title("Find & Replace")
        self.dialog.geometry("350x150")
        self.dialog.resizable(False, False)

        # Find entry
        ttk.Label(self.dialog, text="Find:").pack(pady=2)
        self.find_entry = ttk.Entry(self.dialog, width=40)
        self.find_entry.pack(pady=2)

        # Replace entry
        ttk.Label(self.dialog, text="Replace with:").pack(pady=2)
        self.replace_entry = ttk.Entry(self.dialog, width=40)
        self.replace_entry.pack(pady=2)

        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Find Next", command=self.find_next).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(button_frame, text="Replace", command=self.replace_current).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(button_frame, text="Replace All", command=self.replace_all).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(
            side=tk.LEFT, padx=2
        )

        self.find_entry.focus()

    def find_next(self):
        """Find next occurrence"""
        search_text = self.find_entry.get()
        if not search_text:
            return

        start_pos = self.text_widget.index(tk.INSERT)
        found_pos = self.text_widget.search(search_text, start_pos, tk.END)

        if found_pos:
            end_pos = f"{found_pos}+{len(search_text)}c"
            self.text_widget.tag_remove(tk.SEL, "1.0", tk.END)
            self.text_widget.tag_add(tk.SEL, found_pos, end_pos)
            self.text_widget.mark_set(tk.INSERT, end_pos)
            self.text_widget.see(found_pos)
        else:
            messagebox.showinfo("Find", f"'{search_text}' not found")

    def replace_current(self):
        """Replace current selection"""
        if self.text_widget.tag_ranges(tk.SEL):
            replace_text = self.replace_entry.get()
            self.text_widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text_widget.insert(tk.INSERT, replace_text)

    def replace_all(self):
        """Replace all occurrences"""
        search_text = self.find_entry.get()
        replace_text = self.replace_entry.get()

        if not search_text:
            return

        content = self.text_widget.get("1.0", tk.END)
        new_content = content.replace(search_text, replace_text)

        if content != new_content:
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert("1.0", new_content)
            count = content.count(search_text)
            messagebox.showinfo("Replace All", f"Replaced {count} occurrences")
        else:
            messagebox.showinfo("Replace All", "No occurrences found")


class GotoDialog:
    """Go to line dialog"""

    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.create_dialog()

    def create_dialog(self):
        """Create goto dialog"""
        self.dialog = tk.Toplevel()
        self.dialog.title("Go To Line")
        self.dialog.geometry("250x100")
        self.dialog.resizable(False, False)

        # Line entry
        ttk.Label(self.dialog, text="Line number:").pack(pady=5)
        self.line_entry = ttk.Entry(self.dialog, width=20)
        self.line_entry.pack(pady=5)
        self.line_entry.focus()

        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Go", command=self.goto_line).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(
            side=tk.LEFT, padx=5
        )

        # Bind Enter key
        self.line_entry.bind("<Return>", lambda e: self.goto_line())

    def goto_line(self):
        """Go to specified line"""
        try:
            line_num = int(self.line_entry.get())
            self.text_widget.mark_set(tk.INSERT, f"{line_num}.0")
            self.text_widget.see(f"{line_num}.0")
            self.dialog.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid line number")
