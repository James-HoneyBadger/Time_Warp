"""
Advanced Code Editor Features
Syntax highlighting, auto-completion, and intelligent code editing for Time_Warp.
"""

import re
import tkinter as tk
from typing import List, Dict, Tuple, Optional


class AdvancedSyntaxHighlighter:
    """Advanced syntax highlighting for PILOT, Logo, BASIC, and Python"""

    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.setup_tags()

    def setup_tags(self):
        """Setup syntax highlighting tags"""
        # PILOT syntax highlighting
        self.text_widget.tag_configure(
            "pilot_command", foreground="#0066cc", font=("Courier", 10, "bold")
        )
        self.text_widget.tag_configure(
            "pilot_label", foreground="#cc6600", font=("Courier", 10, "bold")
        )
        self.text_widget.tag_configure("pilot_variable", foreground="#009900")

        # Logo syntax highlighting
        self.text_widget.tag_configure(
            "logo_command", foreground="#990099", font=("Courier", 10, "bold")
        )
        self.text_widget.tag_configure(
            "logo_procedure", foreground="#cc00cc", font=("Courier", 10, "bold")
        )
        self.text_widget.tag_configure("logo_number", foreground="#ff6600")

        # BASIC syntax highlighting
        self.text_widget.tag_configure(
            "basic_keyword", foreground="#0000cc", font=("Courier", 10, "bold")
        )
        self.text_widget.tag_configure("basic_number", foreground="#ff6600")
        self.text_widget.tag_configure("basic_string", foreground="#009900")

        # Python syntax highlighting
        self.text_widget.tag_configure(
            "python_keyword", foreground="#0000cc", font=("Courier", 10, "bold")
        )
        self.text_widget.tag_configure("python_string", foreground="#009900")
        self.text_widget.tag_configure(
            "python_comment", foreground="#666666", font=("Courier", 10, "italic")
        )
        self.text_widget.tag_configure(
            "python_function", foreground="#cc00cc", font=("Courier", 10, "bold")
        )

        # Comments and general
        self.text_widget.tag_configure(
            "comment", foreground="#666666", font=("Courier", 10, "italic")
        )
        self.text_widget.tag_configure("error", background="#ffcccc")
        self.text_widget.tag_configure("breakpoint", background="#ffcccc")
        self.text_widget.tag_configure("highlight", background="#ffffcc")

    def highlight_syntax(self, event=None):
        """Main syntax highlighting method"""
        # Clear existing tags
        tags_to_clear = [
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
            "python_function",
            "comment",
            "error",
        ]

        for tag in tags_to_clear:
            self.text_widget.tag_remove(tag, "1.0", tk.END)

        content = self.text_widget.get("1.0", tk.END)
        lines = content.split("\n")

        # Detect language and apply appropriate highlighting
        language = self.detect_language(content)

        if language == "pilot":
            self.highlight_pilot(lines)
        elif language == "logo":
            self.highlight_logo(lines)
        elif language == "basic":
            self.highlight_basic(lines)
        elif language == "python":
            self.highlight_python(lines)
        else:
            # Default highlighting
            self.highlight_comments(lines)

    def detect_language(self, content):
        """Detect programming language from content"""
        content_lower = content.lower()

        # PILOT indicators
        if any(
            cmd in content_lower
            for cmd in ["::type", "::accept", "::compute", "::jump", "::match"]
        ):
            return "pilot"

        # Logo indicators
        if any(
            cmd in content_lower
            for cmd in ["forward", "fd", "back", "bk", "penup", "pendown"]
        ):
            return "logo"

        # BASIC indicators
        if any(
            cmd in content_lower
            for cmd in ["print", "input", "for", "next", "if", "then", "goto"]
        ):
            if "def " not in content_lower and "import " not in content_lower:
                return "basic"

        # Python indicators
        if any(
            indicator in content_lower
            for indicator in ["def ", "import ", "class ", "from ", "__init__"]
        ):
            return "python"

        return "unknown"

    def highlight_pilot(self, lines):
        """Highlight PILOT syntax"""
        pilot_commands = ["TYPE", "ACCEPT", "COMPUTE", "JUMP", "MATCH", "USE", "CLEAR"]

        for i, line in enumerate(lines):
            # PILOT commands (starting with ::)
            if "::" in line:
                cmd_start = line.find("::")
                cmd_end = cmd_start + 2

                # Find end of command
                for j in range(cmd_start + 2, len(line)):
                    if line[j].isspace() or line[j] in ",:":
                        cmd_end = j
                        break
                else:
                    cmd_end = len(line)

                self.text_widget.tag_add(
                    "pilot_command", f"{i+1}.{cmd_start}", f"{i+1}.{cmd_end}"
                )

            # PILOT labels (ending with :)
            if ":" in line and not "::" in line:
                label_end = line.find(":")
                if label_end > 0:
                    self.text_widget.tag_add(
                        "pilot_label", f"{i+1}.0", f"{i+1}.{label_end+1}"
                    )

    def highlight_logo(self, lines):
        """Highlight Logo syntax"""
        logo_commands = [
            "FORWARD",
            "FD",
            "BACK",
            "BK",
            "LEFT",
            "LT",
            "RIGHT",
            "RT",
            "PENUP",
            "PU",
            "PENDOWN",
            "PD",
            "CLEARSCREEN",
            "CS",
            "HOME",
            "SETXY",
            "SETHEADING",
            "SETH",
            "REPEAT",
            "DEFINE",
            "CALL",
        ]

        for i, line in enumerate(lines):
            words = line.split()
            for word in words:
                if word.upper() in logo_commands:
                    word_start = line.find(word)
                    if word_start >= 0:
                        self.text_widget.tag_add(
                            "logo_command",
                            f"{i+1}.{word_start}",
                            f"{i+1}.{word_start + len(word)}",
                        )

            # Highlight numbers
            for match in re.finditer(r"\b\d+\.?\d*\b", line):
                start, end = match.span()
                self.text_widget.tag_add(
                    "logo_number", f"{i+1}.{start}", f"{i+1}.{end}"
                )

    def highlight_basic(self, lines):
        """Highlight BASIC syntax"""
        basic_keywords = [
            "PRINT",
            "INPUT",
            "FOR",
            "NEXT",
            "IF",
            "THEN",
            "ELSE",
            "GOTO",
            "GOSUB",
            "RETURN",
            "LET",
            "DIM",
            "DATA",
            "READ",
            "END",
        ]

        for i, line in enumerate(lines):
            # Keywords
            for keyword in basic_keywords:
                pattern = r"\b" + keyword + r"\b"
                for match in re.finditer(pattern, line, re.IGNORECASE):
                    start, end = match.span()
                    self.text_widget.tag_add(
                        "basic_keyword", f"{i+1}.{start}", f"{i+1}.{end}"
                    )

            # Numbers
            for match in re.finditer(r"\b\d+\.?\d*\b", line):
                start, end = match.span()
                self.text_widget.tag_add(
                    "basic_number", f"{i+1}.{start}", f"{i+1}.{end}"
                )

            # Strings
            for match in re.finditer(r'"[^"]*"', line):
                start, end = match.span()
                self.text_widget.tag_add(
                    "basic_string", f"{i+1}.{start}", f"{i+1}.{end}"
                )

    def highlight_python(self, lines):
        """Highlight Python syntax"""
        python_keywords = [
            "def",
            "class",
            "if",
            "elif",
            "else",
            "for",
            "while",
            "try",
            "except",
            "finally",
            "with",
            "import",
            "from",
            "as",
            "return",
            "yield",
            "break",
            "continue",
            "pass",
            "and",
            "or",
            "not",
            "in",
            "is",
            "lambda",
            "None",
            "True",
            "False",
            "self",
        ]

        for i, line in enumerate(lines):
            # Keywords
            for keyword in python_keywords:
                pattern = r"\b" + keyword + r"\b"
                for match in re.finditer(pattern, line):
                    start, end = match.span()
                    self.text_widget.tag_add(
                        "python_keyword", f"{i+1}.{start}", f"{i+1}.{end}"
                    )

            # Function definitions
            func_match = re.search(r"def\s+(\w+)", line)
            if func_match:
                start = func_match.start(1)
                end = func_match.end(1)
                self.text_widget.tag_add(
                    "python_function", f"{i+1}.{start}", f"{i+1}.{end}"
                )

            # Strings
            for match in re.finditer(r'["\']([^"\'\\\\]|\\\\.)*["\']', line):
                start, end = match.span()
                self.text_widget.tag_add(
                    "python_string", f"{i+1}.{start}", f"{i+1}.{end}"
                )

            # Comments
            comment_match = re.search(r"#.*$", line)
            if comment_match:
                start, end = comment_match.span()
                self.text_widget.tag_add(
                    "python_comment", f"{i+1}.{start}", f"{i+1}.{end}"
                )

    def highlight_comments(self, lines):
        """Highlight comments in any language"""
        for i, line in enumerate(lines):
            # Line comments
            for comment_char in ["#", "//", ";", "'", "REM"]:
                if comment_char in line:
                    comment_start = line.find(comment_char)
                    self.text_widget.tag_add(
                        "comment", f"{i+1}.{comment_start}", f"{i+1}.{len(line)}"
                    )
                    break


class AutoCompletionEngine:
    """Auto-completion system for Time_Warp languages"""

    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.completion_window = None
        self.completions = []
        self.setup_completions()

    def setup_completions(self):
        """Setup completion dictionaries for different languages"""
        self.pilot_completions = [
            "::TYPE",
            "::ACCEPT",
            "::COMPUTE",
            "::JUMP",
            "::MATCH",
            "::USE",
            "::CLEAR",
            "::IF",
            "::ENDIF",
            "::WHILE",
            "::ENDWHILE",
            "::FOR",
            "::ENDFOR",
        ]

        self.logo_completions = [
            "FORWARD",
            "FD",
            "BACK",
            "BK",
            "LEFT",
            "LT",
            "RIGHT",
            "RT",
            "PENUP",
            "PU",
            "PENDOWN",
            "PD",
            "CLEARSCREEN",
            "CS",
            "HOME",
            "SETXY",
            "SETHEADING",
            "SETH",
            "REPEAT",
            "DEFINE",
            "CALL",
            "SETCOLOR",
            "SETPENSIZE",
            "CIRCLE",
            "ARC",
        ]

        self.basic_completions = [
            "PRINT",
            "INPUT",
            "FOR",
            "NEXT",
            "IF",
            "THEN",
            "ELSE",
            "GOTO",
            "GOSUB",
            "RETURN",
            "LET",
            "DIM",
            "DATA",
            "READ",
            "END",
            "WHILE",
            "WEND",
            "DO",
            "LOOP",
            "SELECT",
            "CASE",
        ]

        self.python_completions = [
            "def",
            "class",
            "if",
            "elif",
            "else",
            "for",
            "while",
            "try",
            "except",
            "finally",
            "with",
            "import",
            "from",
            "as",
            "return",
            "yield",
            "break",
            "continue",
            "pass",
            "and",
            "or",
            "not",
            "in",
            "is",
            "lambda",
            "None",
            "True",
            "False",
            "self",
            "__init__",
            "__main__",
        ]

    def show_completions(self, event=None):
        """Show auto-completion popup"""
        current_word = self.get_current_word()
        if len(current_word) < 2:  # Don't show for very short words
            return

        # Get completions based on current language
        language = self.detect_current_language()
        possible_completions = self.get_completions_for_language(language, current_word)

        if possible_completions:
            self.show_completion_popup(possible_completions, current_word)

    def get_current_word(self):
        """Get the word currently being typed"""
        cursor_pos = self.text_widget.index(tk.INSERT)
        line_start = cursor_pos.split(".")[0] + ".0"
        line_text = self.text_widget.get(line_start, cursor_pos)

        # Find the start of the current word
        word_start = len(line_text)
        for i in range(len(line_text) - 1, -1, -1):
            if line_text[i].isalnum() or line_text[i] in "_:":
                word_start = i
            else:
                break

        return line_text[word_start:]

    def detect_current_language(self):
        """Detect the current programming language"""
        content = self.text_widget.get("1.0", tk.END)
        content_lower = content.lower()

        if "::" in content or any(
            cmd in content_lower for cmd in ["::type", "::accept"]
        ):
            return "pilot"
        elif any(cmd in content_lower for cmd in ["forward", "fd", "penup"]):
            return "logo"
        elif any(cmd in content_lower for cmd in ["def ", "import ", "class "]):
            return "python"
        elif (
            any(cmd in content_lower for cmd in ["print", "input"])
            and "def " not in content_lower
        ):
            return "basic"
        else:
            return "unknown"

    def get_completions_for_language(self, language, current_word):
        """Get completions for specific language"""
        current_word_upper = current_word.upper()

        if language == "pilot":
            completions = self.pilot_completions
        elif language == "logo":
            completions = self.logo_completions
        elif language == "basic":
            completions = self.basic_completions
        elif language == "python":
            completions = self.python_completions
        else:
            completions = (
                self.pilot_completions + self.logo_completions + self.basic_completions
            )

        # Filter completions that start with current word
        matching = []
        for completion in completions:
            if completion.upper().startswith(current_word_upper):
                matching.append(completion)

        return matching[:10]  # Limit to 10 suggestions

    def show_completion_popup(self, completions, current_word):
        """Show completion popup window"""
        if self.completion_window:
            self.completion_window.destroy()

        self.completion_window = tk.Toplevel(self.text_widget)
        self.completion_window.wm_overrideredirect(True)

        # Position popup near cursor
        cursor_pos = self.text_widget.index(tk.INSERT)
        x, y, _, _ = self.text_widget.bbox(cursor_pos)
        x += self.text_widget.winfo_rootx()
        y += self.text_widget.winfo_rooty() + 20

        self.completion_window.geometry(f"+{x}+{y}")

        # Create listbox with completions
        listbox = tk.Listbox(self.completion_window, height=min(len(completions), 8))
        listbox.pack()

        for completion in completions:
            listbox.insert(tk.END, completion)

        # Select first item
        if completions:
            listbox.selection_set(0)

        # Bind events
        listbox.bind(
            "<Double-Button-1>", lambda e: self.insert_completion(listbox, current_word)
        )
        listbox.bind(
            "<Return>", lambda e: self.insert_completion(listbox, current_word)
        )
        listbox.bind("<Escape>", lambda e: self.hide_completion_popup())

        listbox.focus_set()

    def insert_completion(self, listbox, current_word):
        """Insert selected completion"""
        selection = listbox.curselection()
        if selection:
            completion = listbox.get(selection[0])

            # Replace current word with completion
            cursor_pos = self.text_widget.index(tk.INSERT)
            word_start_pos = f"{cursor_pos.split('.')[0]}.{int(cursor_pos.split('.')[1]) - len(current_word)}"

            self.text_widget.delete(word_start_pos, cursor_pos)
            self.text_widget.insert(word_start_pos, completion)

        self.hide_completion_popup()

    def hide_completion_popup(self):
        """Hide completion popup"""
        if self.completion_window:
            self.completion_window.destroy()
            self.completion_window = None


class IntelligentCodeCompletion:
    """Context-aware intelligent code completion"""

    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.context_analyzer = ContextAnalyzer()
        self.completion_engine = AutoCompletionEngine(text_widget)

    def get_smart_completions(self, current_line, cursor_pos):
        """Get context-aware completions"""
        context = self.context_analyzer.analyze_context(current_line, cursor_pos)

        # Generate completions based on context
        completions = []

        if context["expecting_command"]:
            completions.extend(self.get_command_completions(context["language"]))
        elif context["expecting_parameter"]:
            completions.extend(self.get_parameter_completions(context))
        elif context["in_expression"]:
            completions.extend(self.get_expression_completions(context))

        return completions

    def get_command_completions(self, language):
        """Get command completions for language"""
        if language == "pilot":
            return ["::TYPE", "::ACCEPT", "::COMPUTE", "::JUMP", "::MATCH"]
        elif language == "logo":
            return ["FORWARD", "BACK", "LEFT", "RIGHT", "PENUP", "PENDOWN"]
        elif language == "basic":
            return ["PRINT", "INPUT", "FOR", "IF", "GOTO", "LET"]
        return []

    def get_parameter_completions(self, context):
        """Get parameter completions based on command"""
        command = context.get("current_command", "").upper()

        if command in ["FORWARD", "FD", "BACK", "BK"]:
            return ["10", "50", "100", "200"]
        elif command in ["LEFT", "LT", "RIGHT", "RT"]:
            return ["90", "45", "30", "60", "180"]
        elif command == "SETXY":
            return ["0 0", "100 100", "200 150"]

        return []

    def get_expression_completions(self, context):
        """Get completions for expressions"""
        return ["TRUE", "FALSE", "AND", "OR", "NOT", "+", "-", "*", "/"]


class ContextAnalyzer:
    """Analyzes code context for intelligent completion"""

    def analyze_context(self, line, cursor_pos):
        """Analyze the current code context"""
        before_cursor = line[:cursor_pos]
        after_cursor = line[cursor_pos:]

        context = {
            "language": self.detect_language(line),
            "expecting_command": self.is_expecting_command(before_cursor),
            "expecting_parameter": self.is_expecting_parameter(before_cursor),
            "in_expression": self.is_in_expression(before_cursor),
            "current_command": self.get_current_command(before_cursor),
            "indentation_level": self.get_indentation_level(line),
        }

        return context

    def detect_language(self, line):
        """Detect language from line content"""
        if "::" in line:
            return "pilot"
        elif any(cmd in line.upper() for cmd in ["FORWARD", "BACK", "PENUP"]):
            return "logo"
        elif any(cmd in line.upper() for cmd in ["PRINT", "INPUT", "FOR"]):
            return "basic"
        elif any(indicator in line for indicator in ["def ", "import ", "class "]):
            return "python"
        return "unknown"

    def is_expecting_command(self, text):
        """Check if we're expecting a command"""
        stripped = text.strip()
        return len(stripped) == 0 or stripped.endswith(":") or stripped.endswith("\n")

    def is_expecting_parameter(self, text):
        """Check if we're expecting a parameter"""
        words = text.split()
        if len(words) >= 1:
            last_word = words[-1].upper()
            return last_word in ["FORWARD", "BACK", "LEFT", "RIGHT", "REPEAT", "SETXY"]
        return False

    def is_in_expression(self, text):
        """Check if we're in an expression"""
        return any(op in text for op in ["=", "+", "-", "*", "/", "(", ")"])

    def get_current_command(self, text):
        """Get the current command being typed"""
        words = text.split()
        if words:
            return words[0]
        return ""

    def get_indentation_level(self, line):
        """Get indentation level of line"""
        return len(line) - len(line.lstrip())


class RealTimeSyntaxChecker:
    """Real-time syntax checking and error highlighting"""

    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.error_markers = []

    def check_syntax(self, event=None):
        """Check syntax and highlight errors"""
        # Clear previous error markers
        self.clear_error_markers()

        content = self.text_widget.get("1.0", tk.END)
        lines = content.split("\n")

        # Detect language and check syntax
        language = self.detect_language(content)

        if language == "pilot":
            self.check_pilot_syntax(lines)
        elif language == "logo":
            self.check_logo_syntax(lines)
        elif language == "basic":
            self.check_basic_syntax(lines)
        elif language == "python":
            self.check_python_syntax(lines)

    def clear_error_markers(self):
        """Clear all error markers"""
        self.text_widget.tag_remove("syntax_error", "1.0", tk.END)
        self.error_markers.clear()

    def mark_error(self, line_num, start_col, end_col, message):
        """Mark a syntax error"""
        start_pos = f"{line_num}.{start_col}"
        end_pos = f"{line_num}.{end_col}"

        self.text_widget.tag_add("syntax_error", start_pos, end_pos)
        self.text_widget.tag_configure(
            "syntax_error", underline=True, underlinefg="red"
        )

        self.error_markers.append(
            {"line": line_num, "start": start_col, "end": end_col, "message": message}
        )

    def detect_language(self, content):
        """Detect programming language"""
        content_lower = content.lower()

        if "::" in content:
            return "pilot"
        elif any(cmd in content_lower for cmd in ["forward", "fd", "penup"]):
            return "logo"
        elif any(cmd in content_lower for cmd in ["def ", "import ", "class "]):
            return "python"
        elif any(cmd in content_lower for cmd in ["print", "input"]):
            return "basic"
        return "unknown"

    def check_pilot_syntax(self, lines):
        """Check PILOT syntax"""
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            # Check for proper command format
            if line.startswith("::"):
                if len(line) < 4:
                    self.mark_error(i, 0, len(line), "Incomplete PILOT command")

            # Check for unmatched brackets
            if line.count("(") != line.count(")"):
                self.mark_error(i, 0, len(line), "Unmatched parentheses")

    def check_logo_syntax(self, lines):
        """Check Logo syntax"""
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            # Check for proper procedure definitions
            if line.upper().startswith("TO "):
                if len(line.split()) < 2:
                    self.mark_error(i, 0, len(line), "Incomplete procedure definition")

            # Check for balanced brackets
            if line.count("[") != line.count("]"):
                self.mark_error(i, 0, len(line), "Unmatched brackets")

    def check_basic_syntax(self, lines):
        """Check BASIC syntax"""
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            # Check FOR/NEXT matching
            if line.upper().startswith("FOR ") and "TO" not in line.upper():
                self.mark_error(i, 0, len(line), "FOR statement missing TO")

            # Check IF/THEN structure
            if line.upper().startswith("IF ") and "THEN" not in line.upper():
                self.mark_error(i, 0, len(line), "IF statement missing THEN")

    def check_python_syntax(self, lines):
        """Check Python syntax"""
        try:
            code = "\n".join(lines)
            compile(code, "<string>", "exec")
        except SyntaxError as e:
            if e.lineno and e.offset:
                self.mark_error(e.lineno, e.offset - 1, e.offset, str(e.msg))


class CodeFoldingSystem:
    """Code folding system for collapsible code sections"""

    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.folded_regions = {}
        self.fold_markers = {}

    def setup_folding(self):
        """Setup code folding system"""
        # Add folding markers
        self.text_widget.tag_configure(
            "fold_marker", foreground="blue", font=("Courier", 8)
        )

        # Bind events
        self.text_widget.bind("<Button-1>", self.on_click)

    def find_foldable_regions(self):
        """Find regions that can be folded"""
        content = self.text_widget.get("1.0", tk.END)
        lines = content.split("\n")

        regions = []

        # Find function definitions
        for i, line in enumerate(lines):
            if line.strip().startswith("def ") or line.strip().startswith("class "):
                end_line = self.find_block_end(lines, i)
                if end_line > i + 1:
                    regions.append((i + 1, end_line))

            # Find control structures
            elif any(
                line.strip().startswith(keyword)
                for keyword in ["if ", "for ", "while ", "try:"]
            ):
                end_line = self.find_block_end(lines, i)
                if end_line > i + 1:
                    regions.append((i + 1, end_line))

        return regions

    def find_block_end(self, lines, start_line):
        """Find the end of a code block"""
        if start_line >= len(lines):
            return start_line

        start_indent = len(lines[start_line]) - len(lines[start_line].lstrip())

        for i in range(start_line + 1, len(lines)):
            line = lines[i]
            if line.strip():  # Non-empty line
                current_indent = len(line) - len(line.lstrip())
                if current_indent <= start_indent:
                    return i

        return len(lines)

    def fold_region(self, start_line, end_line):
        """Fold a code region"""
        region_id = f"{start_line}_{end_line}"

        if region_id not in self.folded_regions:
            # Hide lines
            for line_num in range(start_line + 1, end_line + 1):
                self.text_widget.tag_add("hidden", f"{line_num}.0", f"{line_num}.end")

            self.text_widget.tag_configure("hidden", elide=True)

            # Add fold marker
            marker_pos = f"{start_line}.end"
            self.text_widget.insert(marker_pos, " [+]")
            self.text_widget.tag_add("fold_marker", marker_pos, f"{marker_pos}+4c")

            self.folded_regions[region_id] = True

    def unfold_region(self, start_line, end_line):
        """Unfold a code region"""
        region_id = f"{start_line}_{end_line}"

        if region_id in self.folded_regions:
            # Show lines
            for line_num in range(start_line + 1, end_line + 1):
                self.text_widget.tag_remove(
                    "hidden", f"{line_num}.0", f"{line_num}.end"
                )

            # Remove fold marker
            content = self.text_widget.get(f"{start_line}.0", f"{start_line}.end")
            if " [+]" in content:
                marker_start = content.find(" [+]")
                self.text_widget.delete(
                    f"{start_line}.{marker_start}", f"{start_line}.{marker_start + 4}"
                )

            del self.folded_regions[region_id]

    def on_click(self, event):
        """Handle click events for folding"""
        pos = self.text_widget.index(f"@{event.x},{event.y}")
        line_num = int(pos.split(".")[0])

        # Check if clicked on fold marker
        line_content = self.text_widget.get(f"{line_num}.0", f"{line_num}.end")
        if " [+]" in line_content:
            # Find the folded region and unfold it
            for region_id, folded in self.folded_regions.items():
                start, end = map(int, region_id.split("_"))
                if start == line_num:
                    self.unfold_region(start, end)
                    break
        else:
            # Check if this line can be folded
            regions = self.find_foldable_regions()
            for start, end in regions:
                if start == line_num:
                    self.fold_region(start, end)
                    break
