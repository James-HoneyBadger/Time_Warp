"""
Code Completion Engine for Time_Warp IDE
Provides intelligent code completion based on language context
"""

import re
import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Optional, Callable, Any, Tuple
from .language_engine import LanguageEngine, BaseLanguageEngine


class CompletionItem:
    """Represents a code completion item"""

    def __init__(
        self,
        text: str,
        display_text: str = None,
        kind: str = "keyword",
        detail: str = "",
        documentation: str = "",
        insert_text: str = None,
    ):
        self.text = text
        self.display_text = display_text or text
        self.kind = kind  # keyword, function, variable, class, module, etc.
        self.detail = detail
        self.documentation = documentation
        self.insert_text = insert_text or text
        self.priority = 0  # Higher priority items appear first

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "text": self.text,
            "display_text": self.display_text,
            "kind": self.kind,
            "detail": self.detail,
            "documentation": self.documentation,
            "insert_text": self.insert_text,
            "priority": self.priority,
        }


class CompletionPopup:
    """Popup window for showing completions"""

    def __init__(self, parent_widget):
        self.parent_widget = parent_widget
        self.popup = None
        self.listbox = None
        self.items = []
        self.selected_index = 0
        self.callback: Optional[Callable[[CompletionItem], None]] = None

    def show(
        self,
        x: int,
        y: int,
        items: List[CompletionItem],
        callback: Callable[[CompletionItem], None],
    ):
        """Show completion popup at specified position"""
        self.items = items
        self.callback = callback
        self.selected_index = 0

        if not items:
            self.hide()
            return

        if self.popup:
            self.hide()

        # Create popup window
        self.popup = tk.Toplevel(self.parent_widget)
        self.popup.wm_overrideredirect(True)
        self.popup.configure(bg="white", relief="solid", borderwidth=1)

        # Create listbox
        self.listbox = tk.Listbox(
            self.popup,
            height=min(10, len(items)),
            font=("Courier", 9),
            bg="white",
            fg="black",
            selectbackground="#0078D4",
            selectforeground="white",
            borderwidth=0,
            highlightthickness=0,
        )
        self.listbox.pack(fill=tk.BOTH, expand=True)

        # Populate listbox
        for item in items:
            display = f"{item.display_text}"
            if item.kind and item.kind != "keyword":
                display += f" ({item.kind})"
            self.listbox.insert(tk.END, display)

        # Select first item
        if items:
            self.listbox.selection_set(0)

        # Position popup
        self.popup.geometry(f"+{x}+{y}")

        # Bind events
        self.listbox.bind("<Double-Button-1>", self._on_double_click)
        self.listbox.bind("<Return>", self._on_return)
        self.listbox.bind("<Escape>", self._on_escape)
        self.listbox.bind("<Up>", self._on_up)
        self.listbox.bind("<Down>", self._on_down)

        # Give focus to listbox
        self.listbox.focus_set()

    def hide(self):
        """Hide completion popup"""
        if self.popup:
            self.popup.destroy()
            self.popup = None
            self.listbox = None
        self.items = []

    def _on_double_click(self, event):
        """Handle double click on item"""
        self._accept_completion()

    def _on_return(self, event):
        """Handle Return key"""
        self._accept_completion()

    def _on_escape(self, event):
        """Handle Escape key"""
        self.hide()

    def _on_up(self, event):
        """Handle Up arrow"""
        if self.selected_index > 0:
            self.selected_index -= 1
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(self.selected_index)
            self.listbox.see(self.selected_index)

    def _on_down(self, event):
        """Handle Down arrow"""
        if self.selected_index < len(self.items) - 1:
            self.selected_index += 1
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(self.selected_index)
            self.listbox.see(self.selected_index)

    def _accept_completion(self):
        """Accept selected completion"""
        if 0 <= self.selected_index < len(self.items) and self.callback:
            item = self.items[self.selected_index]
            self.callback(item)
        self.hide()

    def is_visible(self) -> bool:
        """Check if popup is visible"""
        return self.popup is not None


class CodeCompletionEngine:
    """Main code completion engine"""

    def __init__(self, text_widget, language_engine: LanguageEngine):
        self.text_widget = text_widget
        self.language_engine = language_engine
        self.popup = CompletionPopup(text_widget)
        self.completion_cache: Dict[str, List[CompletionItem]] = {}
        self.trigger_chars = [".", ":", "#", " "]
        self.min_chars = 1

        # Bind events
        self.text_widget.bind("<KeyPress>", self._on_key_press)
        self.text_widget.bind("<Button-1>", self._on_click)

    def _on_key_press(self, event):
        """Handle key press events"""
        # Hide completion on certain keys
        if event.keysym in ["Escape", "Return", "Tab"]:
            self.popup.hide()
        elif event.keysym in ["Up", "Down"] and self.popup.is_visible():
            # Let popup handle navigation
            return
        elif event.char.isprintable():
            # Schedule completion check after character is inserted
            self.text_widget.after(10, self._check_completion)

    def _on_click(self, event):
        """Handle click events"""
        self.popup.hide()

    def _check_completion(self):
        """Check if completion should be triggered"""
        cursor_pos = self.text_widget.index(tk.INSERT)
        line_start = cursor_pos.split(".")[0] + ".0"
        current_line = self.text_widget.get(line_start, cursor_pos)

        # Check for trigger conditions
        should_trigger = False

        # Trigger on certain characters
        if current_line and current_line[-1] in self.trigger_chars:
            should_trigger = True

        # Trigger after minimum characters
        elif len(current_line.strip()) >= self.min_chars:
            # Check if we're typing a word
            match = re.search(r"([A-Za-z_][A-Za-z0-9_]*\*?)$", current_line)
            if match and len(match.group(1)) >= self.min_chars:
                should_trigger = True

        if should_trigger:
            self.show_completions()

    def show_completions(self, force: bool = False):
        """Show completion popup"""
        cursor_pos = self.text_widget.index(tk.INSERT)
        completions = self.get_completions(cursor_pos)

        if not completions and not force:
            self.popup.hide()
            return

        # Get cursor position on screen
        x, y, width, height = self.text_widget.bbox(cursor_pos)
        x += self.text_widget.winfo_rootx()
        y += self.text_widget.winfo_rooty() + height

        self.popup.show(x, y, completions, self._on_completion_selected)

    def get_completions(self, cursor_pos: str) -> List[CompletionItem]:
        """Get completions for current position"""
        # Get text up to cursor
        text = self.text_widget.get("1.0", cursor_pos)
        cursor_line, cursor_col = map(int, cursor_pos.split("."))

        # Get current word being typed
        lines = text.split("\n")
        current_line = lines[cursor_line - 1] if cursor_line <= len(lines) else ""

        # Find word at cursor
        word_start = cursor_col
        while word_start > 0 and (
            current_line[word_start - 1].isalnum()
            or current_line[word_start - 1] in "_:*#"
        ):
            word_start -= 1

        current_word = current_line[word_start:cursor_col]

        # Get language-specific completions
        engine = self.language_engine.get_current_engine()
        if not engine:
            return []

        raw_completions = engine.get_completions(text, len(text.encode("utf-8")))

        # Convert to CompletionItem objects
        items = []
        for completion in raw_completions:
            if isinstance(completion, str):
                # Filter by current word
                if current_word and not completion.lower().startswith(
                    current_word.lower()
                ):
                    continue

                item = self._create_completion_item(completion, engine)
                items.append(item)

        # Sort by priority and alphabetically
        items.sort(key=lambda x: (-x.priority, x.text.lower()))

        return items[:20]  # Limit to 20 items

    def _create_completion_item(
        self, text: str, engine: BaseLanguageEngine
    ) -> CompletionItem:
        """Create a completion item from text"""
        kind = "keyword"
        detail = ""
        documentation = ""
        priority = 0

        # Determine kind based on text and language
        language = engine.config.name.lower()

        if text in engine.config.keywords:
            kind = "keyword"
            priority = 10
        elif text.startswith("#") and language == "pilot":
            kind = "variable"
            detail = "PILOT variable"
            priority = 8
        elif text.startswith("*") and language == "pilot":
            kind = "label"
            detail = "PILOT label"
            priority = 9
        elif text.startswith(":") and language == "logo":
            kind = "variable"
            detail = "Logo variable"
            priority = 8
        elif "(" in text:
            kind = "function"
            detail = "Function"
            priority = 9
        elif text.isupper():
            kind = "keyword"
            priority = 10
        else:
            kind = "identifier"
            priority = 5

        # Add language-specific documentation
        if language == "pilot":
            documentation = self._get_pilot_documentation(text)
        elif language == "basic":
            documentation = self._get_basic_documentation(text)
        elif language == "logo":
            documentation = self._get_logo_documentation(text)
        elif language == "python":
            documentation = self._get_python_documentation(text)

        return CompletionItem(
            text=text,
            kind=kind,
            detail=detail,
            documentation=documentation,
            priority=priority,
        )

    def _get_pilot_documentation(self, text: str) -> str:
        """Get PILOT-specific documentation"""
        docs = {
            "T:": "Type/display text to the user",
            "A:": "Accept input from the user",
            "J:": "Jump to a label",
            "Y:": "Yes - conditional jump if true",
            "N:": "No - conditional jump if false",
            "U:": "Use - perform calculation",
            "C:": "Compute - arithmetic operation",
            "R:": "Remark - comment line",
            "M:": "Match - pattern matching",
            "E:": "End - end of program",
        }
        return docs.get(text, "")

    def _get_basic_documentation(self, text: str) -> str:
        """Get BASIC-specific documentation"""
        docs = {
            "PRINT": "Display text or values",
            "INPUT": "Get input from user",
            "LET": "Assign value to variable",
            "IF": "Conditional statement",
            "FOR": "Loop with counter",
            "WHILE": "Loop while condition is true",
            "GOTO": "Jump to line number",
            "GOSUB": "Call subroutine",
            "RETURN": "Return from subroutine",
            "DIM": "Declare array dimensions",
        }
        return docs.get(text.upper(), "")

    def _get_logo_documentation(self, text: str) -> str:
        """Get Logo-specific documentation"""
        docs = {
            "FORWARD": "Move turtle forward by specified distance",
            "FD": "Move turtle forward (short form)",
            "BACK": "Move turtle backward by specified distance",
            "BK": "Move turtle backward (short form)",
            "LEFT": "Turn turtle left by specified angle",
            "LT": "Turn turtle left (short form)",
            "RIGHT": "Turn turtle right by specified angle",
            "RT": "Turn turtle right (short form)",
            "PENUP": "Lift pen (stop drawing)",
            "PU": "Lift pen (short form)",
            "PENDOWN": "Put pen down (start drawing)",
            "PD": "Put pen down (short form)",
            "REPEAT": "Repeat commands specified number of times",
            "TO": "Define a procedure",
            "END": "End procedure definition",
        }
        return docs.get(text.upper(), "")

    def _get_python_documentation(self, text: str) -> str:
        """Get Python-specific documentation"""
        docs = {
            "def": "Define a function",
            "class": "Define a class",
            "if": "Conditional statement",
            "elif": "Else if condition",
            "else": "Else clause",
            "for": "For loop",
            "while": "While loop",
            "try": "Try block for exception handling",
            "except": "Exception handler",
            "finally": "Finally block",
            "import": "Import module",
            "from": "Import from module",
            "return": "Return value from function",
            "yield": "Yield value (generator)",
            "print": "Print to console",
            "input": "Get input from user",
            "len": "Get length of object",
            "range": "Generate range of numbers",
        }
        return docs.get(text, "")

    def _on_completion_selected(self, item: CompletionItem):
        """Handle completion selection"""
        # Get current cursor position
        cursor_pos = self.text_widget.index(tk.INSERT)
        cursor_line, cursor_col = map(int, cursor_pos.split("."))

        # Get current line
        line_start = f"{cursor_line}.0"
        line_end = f"{cursor_line}.end"
        current_line = self.text_widget.get(line_start, line_end)

        # Find word boundaries
        word_start = cursor_col
        while word_start > 0 and (
            current_line[word_start - 1].isalnum()
            or current_line[word_start - 1] in "_:*#"
        ):
            word_start -= 1

        word_end = cursor_col
        while word_end < len(current_line) and (
            current_line[word_end].isalnum() or current_line[word_end] in "_:*#"
        ):
            word_end += 1

        # Replace the word
        start_pos = f"{cursor_line}.{word_start}"
        end_pos = f"{cursor_line}.{word_end}"

        self.text_widget.delete(start_pos, end_pos)
        self.text_widget.insert(start_pos, item.insert_text)

        # Move cursor to end of inserted text
        new_pos = f"{cursor_line}.{word_start + len(item.insert_text)}"
        self.text_widget.mark_set(tk.INSERT, new_pos)

    def set_trigger_chars(self, chars: List[str]):
        """Set characters that trigger completion"""
        self.trigger_chars = chars

    def set_min_chars(self, count: int):
        """Set minimum characters before triggering completion"""
        self.min_chars = max(1, count)

    def clear_cache(self):
        """Clear completion cache"""
        self.completion_cache.clear()

    def hide_completions(self):
        """Hide completion popup"""
        self.popup.hide()
