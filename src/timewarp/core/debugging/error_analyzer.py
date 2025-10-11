"""
Error Analysis and Stack Trace Visualization for Time_Warp IDE
Intelligent error detection, pattern matching, and stack trace visualization
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import traceback
import sys
import re
import threading
from typing import Dict, List, Any, Optional, Callable, Tuple
from datetime import datetime
from collections import defaultdict, Counter
import ast
import inspect


class ErrorPatternMatcher:
    """Matches and categorizes common error patterns"""

    def __init__(self):
        self.error_patterns = {
            "syntax_errors": [
                (r"SyntaxError: invalid syntax", "Invalid Python syntax"),
                (r"IndentationError:", "Incorrect indentation"),
                (r"TabError:", "Inconsistent use of tabs and spaces"),
                (r"SyntaxError: unexpected EOF", "Unexpected end of file"),
                (r"SyntaxError: .*expected.*", "Missing expected syntax element"),
            ],
            "name_errors": [
                (
                    r"NameError: name .* is not defined",
                    "Undefined variable or function",
                ),
                (r"UnboundLocalError:", "Local variable referenced before assignment"),
                (
                    r"NameError: global name .* is not defined",
                    "Undefined global variable",
                ),
            ],
            "type_errors": [
                (
                    r"TypeError: .* object is not callable",
                    "Attempting to call non-callable object",
                ),
                (
                    r"TypeError: .* takes .* positional argument",
                    "Incorrect number of function arguments",
                ),
                (
                    r"TypeError: unsupported operand type",
                    "Invalid operation between types",
                ),
                (
                    r"TypeError: .* object is not subscriptable",
                    "Attempting to index non-indexable object",
                ),
                (
                    r"TypeError: .* object is not iterable",
                    "Attempting to iterate over non-iterable object",
                ),
            ],
            "attribute_errors": [
                (
                    r"AttributeError: .* object has no attribute",
                    "Accessing non-existent attribute",
                ),
                (
                    r"AttributeError: module .* has no attribute",
                    "Module attribute not found",
                ),
                (
                    r"AttributeError: type object .* has no attribute",
                    "Class attribute not found",
                ),
            ],
            "import_errors": [
                (r"ImportError: No module named", "Module not found"),
                (r"ModuleNotFoundError:", "Module not installed or not in path"),
                (r"ImportError: cannot import name", "Import name not found in module"),
            ],
            "index_errors": [
                (r"IndexError: list index out of range", "List index exceeds bounds"),
                (
                    r"IndexError: string index out of range",
                    "String index exceeds bounds",
                ),
                (r"KeyError:", "Dictionary key not found"),
            ],
            "value_errors": [
                (
                    r"ValueError: invalid literal for .* with base",
                    "Invalid conversion to number",
                ),
                (
                    r"ValueError: could not convert string to",
                    "String conversion failed",
                ),
                (r"ValueError: .* is not in list", "Value not found in list"),
            ],
            "file_errors": [
                (r"FileNotFoundError:", "File or directory not found"),
                (r"PermissionError:", "Insufficient permissions"),
                (r"IsADirectoryError:", "Expected file but found directory"),
                (r"NotADirectoryError:", "Expected directory but found file"),
            ],
            "runtime_errors": [
                (r"RecursionError:", "Maximum recursion depth exceeded"),
                (r"MemoryError:", "Out of memory"),
                (r"ZeroDivisionError:", "Division by zero"),
                (r"OverflowError:", "Numeric overflow"),
            ],
        }

        self.suggestions = {
            "syntax_errors": [
                "Check for missing colons, parentheses, or brackets",
                "Verify proper indentation (use consistent spaces or tabs)",
                "Look for unclosed strings or comments",
                "Check for invalid characters or keywords",
            ],
            "name_errors": [
                "Check variable/function name spelling",
                "Ensure variables are defined before use",
                "Verify import statements are correct",
                "Check variable scope (local vs global)",
            ],
            "type_errors": [
                "Verify object types match expected operations",
                "Check function call arguments and types",
                "Ensure objects support the operations being performed",
                "Review type annotations and conversions",
            ],
            "attribute_errors": [
                "Check object type and available attributes",
                "Verify import statements and module structure",
                "Look for typos in attribute names",
                "Check if object is None before accessing attributes",
            ],
            "import_errors": [
                "Verify module is installed (pip install <module>)",
                "Check module name spelling",
                "Ensure module is in Python path",
                "Check for circular imports",
            ],
            "index_errors": [
                "Check array/list bounds before accessing",
                "Verify dictionary keys exist",
                "Use .get() method for safe dictionary access",
                "Check for empty collections",
            ],
            "value_errors": [
                "Validate input data format",
                "Check for null or unexpected values",
                "Use try/except for conversion operations",
                "Verify value ranges and constraints",
            ],
            "file_errors": [
                "Check file/directory path spelling",
                "Verify file permissions",
                "Ensure file exists before opening",
                "Use absolute paths when possible",
            ],
            "runtime_errors": [
                "Check for infinite recursion",
                "Review memory usage and data structures",
                "Validate mathematical operations",
                "Add bounds checking for numeric operations",
            ],
        }

    def analyze_error(self, error_text: str) -> Dict[str, Any]:
        """Analyze error text and provide suggestions"""
        analysis = {
            "category": "unknown",
            "pattern": None,
            "description": "Unknown error type",
            "suggestions": [],
            "severity": "medium",
            "common_causes": [],
        }

        # Match against known patterns
        for category, patterns in self.error_patterns.items():
            for pattern, description in patterns:
                if re.search(pattern, error_text, re.IGNORECASE):
                    analysis["category"] = category
                    analysis["pattern"] = pattern
                    analysis["description"] = description
                    analysis["suggestions"] = self.suggestions.get(category, [])
                    analysis["severity"] = self._determine_severity(category)
                    break
            if analysis["category"] != "unknown":
                break

        return analysis

    def _determine_severity(self, category: str) -> str:
        """Determine error severity based on category"""
        severe_categories = ["syntax_errors", "import_errors", "runtime_errors"]
        medium_categories = ["type_errors", "attribute_errors", "file_errors"]

        if category in severe_categories:
            return "high"
        elif category in medium_categories:
            return "medium"
        else:
            return "low"


class StackTraceVisualizer:
    """Visualizes stack traces with interactive navigation"""

    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.setup_ui()
        self.current_traceback = None
        self.stack_frames = []

    def setup_ui(self):
        """Create stack trace visualization interface"""
        # Main frame
        self.frame = ttk.LabelFrame(self.parent, text="Stack Trace Visualizer")
        self.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Control panel
        control_frame = ttk.Frame(self.frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            control_frame,
            text="Capture Current Exception",
            command=self.capture_current_exception,
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            control_frame, text="Load from Text", command=self.load_from_text
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Clear", command=self.clear_trace).pack(
            side=tk.LEFT, padx=2
        )

        # Main content area
        content_frame = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left panel - stack frames
        left_frame = ttk.Frame(content_frame)
        content_frame.add(left_frame, weight=1)

        ttk.Label(left_frame, text="Stack Frames").pack(anchor=tk.W)

        self.frames_tree = ttk.Treeview(
            left_frame,
            columns=("file", "line", "function"),
            show="tree headings",
            height=10,
        )
        self.frames_tree.heading("#0", text="Level")
        self.frames_tree.heading("file", text="File")
        self.frames_tree.heading("line", text="Line")
        self.frames_tree.heading("function", text="Function")

        self.frames_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        self.frames_tree.bind("<<TreeviewSelect>>", self.on_frame_select)

        # Scrollbar for frames tree
        frames_scroll = ttk.Scrollbar(
            left_frame, orient=tk.VERTICAL, command=self.frames_tree.yview
        )
        frames_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.frames_tree.configure(yscrollcommand=frames_scroll.set)

        # Right panel - frame details
        right_frame = ttk.Frame(content_frame)
        content_frame.add(right_frame, weight=2)

        # Frame details notebook
        self.details_notebook = ttk.Notebook(right_frame)
        self.details_notebook.pack(fill=tk.BOTH, expand=True)

        # Source code tab
        source_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(source_frame, text="Source Code")

        self.source_text = scrolledtext.ScrolledText(
            source_frame, wrap=tk.NONE, height=15
        )
        self.source_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Local variables tab
        locals_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(locals_frame, text="Local Variables")

        self.locals_tree = ttk.Treeview(
            locals_frame, columns=("type", "value"), show="tree headings"
        )
        self.locals_tree.heading("#0", text="Name")
        self.locals_tree.heading("type", text="Type")
        self.locals_tree.heading("value", text="Value")
        self.locals_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Error details tab
        error_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(error_frame, text="Error Details")

        self.error_text = scrolledtext.ScrolledText(
            error_frame, wrap=tk.WORD, height=15
        )
        self.error_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def capture_current_exception(self):
        """Capture the current exception if one exists"""
        exc_type, exc_value, exc_traceback = sys.exc_info()

        if exc_traceback is None:
            messagebox.showinfo("No Exception", "No current exception to capture")
            return

        self.visualize_traceback(exc_traceback, exc_type, exc_value)

    def load_from_text(self):
        """Load traceback from text input"""
        # Create dialog for text input
        dialog = tk.Toplevel(self.parent)
        dialog.title("Load Traceback from Text")
        dialog.geometry("600x400")

        ttk.Label(dialog, text="Paste traceback text:").pack(
            anchor=tk.W, padx=10, pady=5
        )

        text_area = scrolledtext.ScrolledText(dialog, wrap=tk.WORD, height=15)
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        def load_text():
            text = text_area.get(1.0, tk.END).strip()
            if text:
                self.parse_traceback_text(text)
                dialog.destroy()

        ttk.Button(button_frame, text="Load", command=load_text).pack(
            side=tk.RIGHT, padx=2
        )
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(
            side=tk.RIGHT, padx=2
        )

    def visualize_traceback(self, tb, exc_type=None, exc_value=None):
        """Visualize a traceback object"""
        self.current_traceback = tb
        self.stack_frames = []

        # Extract stack frames
        current_tb = tb
        level = 0

        while current_tb is not None:
            frame = current_tb.tb_frame
            filename = frame.f_code.co_filename
            line_number = current_tb.tb_lineno
            function_name = frame.f_code.co_name

            frame_info = {
                "level": level,
                "filename": filename,
                "line_number": line_number,
                "function_name": function_name,
                "frame": frame,
                "locals": frame.f_locals.copy(),
                "globals": frame.f_globals,
            }

            self.stack_frames.append(frame_info)
            current_tb = current_tb.tb_next
            level += 1

        # Update UI
        self._update_frames_tree()

        # Show error details
        if exc_type and exc_value:
            error_text = f"Exception Type: {exc_type.__name__}\n"
            error_text += f"Exception Value: {str(exc_value)}\n\n"
            error_text += "Full Traceback:\n"
            error_text += "".join(traceback.format_exception(exc_type, exc_value, tb))

            self.error_text.delete(1.0, tk.END)
            self.error_text.insert(1.0, error_text)

    def parse_traceback_text(self, text: str):
        """Parse traceback from text and visualize"""
        # Simple parsing - this could be made more sophisticated
        lines = text.split("\n")
        self.stack_frames = []

        current_frame = None
        level = 0

        for line in lines:
            line = line.strip()

            # Look for file/line patterns
            if line.startswith('File "') and ", line " in line:
                # Extract file and line information
                match = re.match(r'File "([^"]+)", line (\d+), in (.+)', line)
                if match:
                    filename, line_number, function_name = match.groups()

                    frame_info = {
                        "level": level,
                        "filename": filename,
                        "line_number": int(line_number),
                        "function_name": function_name,
                        "frame": None,
                        "locals": {},
                        "globals": {},
                    }

                    self.stack_frames.append(frame_info)
                    level += 1

        # Update UI
        self._update_frames_tree()

        # Show original text in error details
        self.error_text.delete(1.0, tk.END)
        self.error_text.insert(1.0, text)

    def _update_frames_tree(self):
        """Update the frames tree with current stack frames"""
        # Clear existing items
        for item in self.frames_tree.get_children():
            self.frames_tree.delete(item)

        # Add stack frames
        for frame_info in self.stack_frames:
            filename_short = (
                frame_info["filename"].split("/")[-1]
                if frame_info["filename"]
                else "unknown"
            )

            self.frames_tree.insert(
                "",
                "end",
                text=str(frame_info["level"]),
                values=(
                    filename_short,
                    frame_info["line_number"],
                    frame_info["function_name"],
                ),
            )

    def on_frame_select(self, event):
        """Handle frame selection in tree"""
        selection = self.frames_tree.selection()
        if not selection:
            return

        item = selection[0]
        level = int(self.frames_tree.item(item, "text"))

        if 0 <= level < len(self.stack_frames):
            frame_info = self.stack_frames[level]

            # Update source code display
            self._show_source_code(frame_info)

            # Update local variables display
            self._show_local_variables(frame_info)

    def _show_source_code(self, frame_info: Dict):
        """Show source code for the selected frame"""
        self.source_text.delete(1.0, tk.END)

        try:
            filename = frame_info["filename"]
            line_number = frame_info["line_number"]

            if filename and os.path.exists(filename):
                with open(filename, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                # Show context around the error line
                start_line = max(0, line_number - 10)
                end_line = min(len(lines), line_number + 10)

                for i in range(start_line, end_line):
                    line_text = f"{i+1:4d}: {lines[i]}"

                    # Highlight the error line
                    if i + 1 == line_number:
                        line_text = f">>> {line_text}"

                    self.source_text.insert(tk.END, line_text)

                # Scroll to error line
                error_line_pos = f"{line_number - start_line + 1}.0"
                self.source_text.see(error_line_pos)

            else:
                self.source_text.insert(1.0, f"Source file not found: {filename}")

        except Exception as e:
            self.source_text.insert(1.0, f"Error loading source: {str(e)}")

    def _show_local_variables(self, frame_info: Dict):
        """Show local variables for the selected frame"""
        # Clear existing items
        for item in self.locals_tree.get_children():
            self.locals_tree.delete(item)

        locals_dict = frame_info["locals"]

        for name, value in locals_dict.items():
            if name.startswith("__") and name.endswith("__"):
                continue  # Skip dunder variables

            value_type = type(value).__name__
            value_str = self._format_value(value)

            self.locals_tree.insert(
                "", "end", text=name, values=(value_type, value_str)
            )

    def _format_value(self, value: Any, max_length: int = 100) -> str:
        """Format a value for display"""
        try:
            value_str = repr(value)
            if len(value_str) > max_length:
                value_str = value_str[: max_length - 3] + "..."
            return value_str
        except Exception:
            return f"<{type(value).__name__} object>"

    def clear_trace(self):
        """Clear current trace visualization"""
        self.current_traceback = None
        self.stack_frames = []

        # Clear UI elements
        for item in self.frames_tree.get_children():
            self.frames_tree.delete(item)

        for item in self.locals_tree.get_children():
            self.locals_tree.delete(item)

        self.source_text.delete(1.0, tk.END)
        self.error_text.delete(1.0, tk.END)


class ErrorAnalyzer:
    """Main error analysis interface combining pattern matching and visualization"""

    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.setup_ui()

        # Core components
        self.pattern_matcher = ErrorPatternMatcher()
        self.stack_visualizer = StackTraceVisualizer(self.analysis_frame)

        # Error tracking
        self.error_history = []
        self.current_analysis = None

    def setup_ui(self):
        """Create the main error analyzer interface"""
        # Main frame
        self.frame = ttk.LabelFrame(self.parent, text="Error Analyzer")
        self.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create notebook for different analysis views
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Error analysis tab
        self.analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analysis_frame, text="Error Analysis")

        # Error history tab
        self.history_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text="Error History")
        self.setup_history_tab()

        # Pattern statistics tab
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Pattern Statistics")
        self.setup_statistics_tab()

    def setup_history_tab(self):
        """Setup error history display"""
        # Control frame
        history_control = ttk.Frame(self.history_frame)
        history_control.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            history_control, text="Clear History", command=self.clear_history
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            history_control, text="Export History", command=self.export_history
        ).pack(side=tk.LEFT, padx=2)

        # History tree
        self.history_tree = ttk.Treeview(
            self.history_frame,
            columns=("timestamp", "category", "description"),
            show="tree headings",
        )
        self.history_tree.heading("#0", text="#")
        self.history_tree.heading("timestamp", text="Time")
        self.history_tree.heading("category", text="Category")
        self.history_tree.heading("description", text="Description")

        self.history_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.history_tree.bind("<Double-1>", self.on_history_double_click)

        # Scrollbar for history tree
        history_scroll = ttk.Scrollbar(
            self.history_frame, orient=tk.VERTICAL, command=self.history_tree.yview
        )
        history_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_tree.configure(yscrollcommand=history_scroll.set)

    def setup_statistics_tab(self):
        """Setup pattern statistics display"""
        self.stats_text = scrolledtext.ScrolledText(
            self.stats_frame, wrap=tk.WORD, height=20
        )
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def analyze_error(self, error_text: str, traceback_obj=None):
        """Analyze an error and display results"""
        # Perform pattern analysis
        analysis = self.pattern_matcher.analyze_error(error_text)

        # Store in history
        error_record = {
            "timestamp": datetime.now(),
            "error_text": error_text,
            "analysis": analysis,
            "traceback": traceback_obj,
        }
        self.error_history.append(error_record)
        self.current_analysis = analysis

        # Update UI
        self._update_history_display()
        self._update_statistics()

        # If we have a traceback, visualize it
        if traceback_obj:
            self.stack_visualizer.visualize_traceback(traceback_obj)

        # Show analysis results
        self._display_analysis_results(analysis)

        return analysis

    def _display_analysis_results(self, analysis: Dict):
        """Display analysis results in a popup or dedicated area"""
        # For now, create a simple popup
        result_window = tk.Toplevel(self.parent)
        result_window.title("Error Analysis Results")
        result_window.geometry("600x400")

        # Analysis content
        content_frame = ttk.Frame(result_window)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Category and description
        ttk.Label(
            content_frame,
            text=f"Category: {analysis['category']}",
            font=("TkDefaultFont", 10, "bold"),
        ).pack(anchor=tk.W, pady=2)
        ttk.Label(content_frame, text=f"Description: {analysis['description']}").pack(
            anchor=tk.W, pady=2
        )
        ttk.Label(content_frame, text=f"Severity: {analysis['severity']}").pack(
            anchor=tk.W, pady=2
        )

        # Suggestions
        if analysis["suggestions"]:
            ttk.Label(
                content_frame, text="Suggestions:", font=("TkDefaultFont", 10, "bold")
            ).pack(anchor=tk.W, pady=(10, 2))

            suggestions_frame = ttk.Frame(content_frame)
            suggestions_frame.pack(fill=tk.X, anchor=tk.W, pady=2)

            for i, suggestion in enumerate(analysis["suggestions"], 1):
                ttk.Label(suggestions_frame, text=f"{i}. {suggestion}").pack(
                    anchor=tk.W, padx=10
                )

        # Close button
        ttk.Button(content_frame, text="Close", command=result_window.destroy).pack(
            pady=10
        )

    def _update_history_display(self):
        """Update error history display"""
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        # Add error records
        for i, record in enumerate(self.error_history):
            timestamp = record["timestamp"].strftime("%H:%M:%S")
            category = record["analysis"]["category"]
            description = record["analysis"]["description"]

            self.history_tree.insert(
                "", "end", text=str(i + 1), values=(timestamp, category, description)
            )

    def _update_statistics(self):
        """Update pattern statistics"""
        if not self.error_history:
            return

        # Count categories
        category_counts = Counter(
            record["analysis"]["category"] for record in self.error_history
        )
        severity_counts = Counter(
            record["analysis"]["severity"] for record in self.error_history
        )

        # Generate statistics text
        stats_text = "Error Pattern Statistics\n"
        stats_text += "=" * 40 + "\n\n"

        stats_text += f"Total errors analyzed: {len(self.error_history)}\n\n"

        stats_text += "Errors by Category:\n"
        stats_text += "-" * 20 + "\n"
        for category, count in category_counts.most_common():
            percentage = (count / len(self.error_history)) * 100
            stats_text += f"{category}: {count} ({percentage:.1f}%)\n"

        stats_text += f"\nErrors by Severity:\n"
        stats_text += "-" * 20 + "\n"
        for severity, count in severity_counts.most_common():
            percentage = (count / len(self.error_history)) * 100
            stats_text += f"{severity}: {count} ({percentage:.1f}%)\n"

        # Update display
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)

    def on_history_double_click(self, event):
        """Handle double-click on history item"""
        selection = self.history_tree.selection()
        if not selection:
            return

        item = selection[0]
        index = int(self.history_tree.item(item, "text")) - 1

        if 0 <= index < len(self.error_history):
            record = self.error_history[index]

            # Show analysis results
            self._display_analysis_results(record["analysis"])

            # If traceback available, visualize it
            if record["traceback"]:
                self.stack_visualizer.visualize_traceback(record["traceback"])

    def clear_history(self):
        """Clear error history"""
        self.error_history.clear()
        self._update_history_display()
        self._update_statistics()

    def export_history(self):
        """Export error history to file"""
        if not self.error_history:
            messagebox.showinfo("No Data", "No error history to export")
            return

        filename = f"error_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        try:
            with open(filename, "w") as f:
                f.write("Time_Warp IDE Error History Report\n")
                f.write("=" * 50 + "\n\n")

                for i, record in enumerate(self.error_history, 1):
                    f.write(f"Error #{i}\n")
                    f.write(f"Timestamp: {record['timestamp']}\n")
                    f.write(f"Category: {record['analysis']['category']}\n")
                    f.write(f"Description: {record['analysis']['description']}\n")
                    f.write(f"Severity: {record['analysis']['severity']}\n")
                    f.write(f"Error Text: {record['error_text']}\n")
                    f.write("-" * 30 + "\n\n")

            messagebox.showinfo("Export Complete", f"History exported to {filename}")

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export history: {str(e)}")


# Make sure os is imported for file operations
import os
