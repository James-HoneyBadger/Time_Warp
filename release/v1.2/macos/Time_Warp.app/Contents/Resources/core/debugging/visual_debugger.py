"""
Visual Debugger for Time_Warp IDE
Comprehensive debugging interface with breakpoints, variable inspection, and call stack visualization
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import sys
import pdb
import traceback
import threading
import queue
from typing import Dict, List, Any, Optional, Callable
import ast
import inspect
import json
from datetime import datetime


class BreakpointManager:
    """Manages breakpoints in the debugging session"""

    def __init__(self):
        self.breakpoints: Dict[str, List[int]] = {}  # file -> list of line numbers
        self.conditional_breakpoints: Dict[str, Dict[int, str]] = (
            {}
        )  # file -> {line: condition}
        self.hit_counts: Dict[str, Dict[int, int]] = {}  # file -> {line: count}
        self.enabled: Dict[str, Dict[int, bool]] = {}  # file -> {line: enabled}

    def add_breakpoint(
        self, filename: str, line_number: int, condition: Optional[str] = None
    ) -> bool:
        """Add a breakpoint at the specified location"""
        if filename not in self.breakpoints:
            self.breakpoints[filename] = []
            self.conditional_breakpoints[filename] = {}
            self.hit_counts[filename] = {}
            self.enabled[filename] = {}

        if line_number not in self.breakpoints[filename]:
            self.breakpoints[filename].append(line_number)
            self.breakpoints[filename].sort()

        self.enabled[filename][line_number] = True
        self.hit_counts[filename][line_number] = 0

        if condition:
            self.conditional_breakpoints[filename][line_number] = condition

        return True

    def remove_breakpoint(self, filename: str, line_number: int) -> bool:
        """Remove a breakpoint"""
        if filename in self.breakpoints and line_number in self.breakpoints[filename]:
            self.breakpoints[filename].remove(line_number)
            if line_number in self.conditional_breakpoints.get(filename, {}):
                del self.conditional_breakpoints[filename][line_number]
            if line_number in self.hit_counts.get(filename, {}):
                del self.hit_counts[filename][line_number]
            if line_number in self.enabled.get(filename, {}):
                del self.enabled[filename][line_number]
            return True
        return False

    def toggle_breakpoint(self, filename: str, line_number: int) -> bool:
        """Toggle breakpoint enabled/disabled state"""
        if filename in self.enabled and line_number in self.enabled[filename]:
            self.enabled[filename][line_number] = not self.enabled[filename][
                line_number
            ]
            return self.enabled[filename][line_number]
        return False

    def is_breakpoint_hit(
        self, filename: str, line_number: int, local_vars: Optional[Dict] = None
    ) -> bool:
        """Check if breakpoint should be hit"""
        if (
            filename not in self.breakpoints
            or line_number not in self.breakpoints[filename]
        ):
            return False

        if not self.enabled[filename].get(line_number, False):
            return False

        # Check conditional breakpoint
        condition = self.conditional_breakpoints.get(filename, {}).get(line_number)
        if condition and local_vars:
            try:
                if not eval(condition, {"__builtins__": {}}, local_vars):
                    return False
            except Exception:
                return False  # Invalid condition, skip breakpoint

        # Increment hit count
        self.hit_counts[filename][line_number] += 1
        return True

    def get_breakpoints(self, filename: Optional[str] = None) -> Dict:
        """Get breakpoints for file or all files"""
        if filename:
            return {
                "lines": self.breakpoints.get(filename, []),
                "conditions": self.conditional_breakpoints.get(filename, {}),
                "hit_counts": self.hit_counts.get(filename, {}),
                "enabled": self.enabled.get(filename, {}),
            }
        return {
            "breakpoints": self.breakpoints,
            "conditions": self.conditional_breakpoints,
            "hit_counts": self.hit_counts,
            "enabled": self.enabled,
        }


class VariableInspector:
    """Inspects and displays variable values during debugging"""

    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.setup_ui()
        self.variables = {}
        self.watch_expressions = []

    def setup_ui(self):
        """Create the variable inspector interface"""
        # Main frame
        self.frame = ttk.LabelFrame(self.parent, text="Variables")
        self.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Notebook for different variable scopes
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Local variables tab
        self.locals_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.locals_frame, text="Locals")

        self.locals_tree = ttk.Treeview(
            self.locals_frame, columns=("type", "value"), show="tree headings"
        )
        self.locals_tree.heading("#0", text="Name")
        self.locals_tree.heading("type", text="Type")
        self.locals_tree.heading("value", text="Value")
        self.locals_tree.pack(fill=tk.BOTH, expand=True)

        # Global variables tab
        self.globals_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.globals_frame, text="Globals")

        self.globals_tree = ttk.Treeview(
            self.globals_frame, columns=("type", "value"), show="tree headings"
        )
        self.globals_tree.heading("#0", text="Name")
        self.globals_tree.heading("type", text="Type")
        self.globals_tree.heading("value", text="Value")
        self.globals_tree.pack(fill=tk.BOTH, expand=True)

        # Watch expressions tab
        self.watch_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.watch_frame, text="Watch")

        # Add watch expression
        watch_entry_frame = ttk.Frame(self.watch_frame)
        watch_entry_frame.pack(fill=tk.X, padx=5, pady=5)

        self.watch_entry = ttk.Entry(watch_entry_frame)
        self.watch_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(
            watch_entry_frame, text="Add", command=self.add_watch_expression
        ).pack(side=tk.RIGHT, padx=(5, 0))

        self.watch_tree = ttk.Treeview(
            self.watch_frame, columns=("expression", "value"), show="tree headings"
        )
        self.watch_tree.heading("#0", text="#")
        self.watch_tree.heading("expression", text="Expression")
        self.watch_tree.heading("value", text="Value")
        self.watch_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def update_variables(self, local_vars: Dict, global_vars: Dict):
        """Update variable displays"""
        self._update_tree(self.locals_tree, local_vars)
        self._update_tree(self.globals_tree, global_vars)
        self._update_watch_expressions(local_vars, global_vars)

    def _update_tree(self, tree: ttk.Treeview, variables: Dict):
        """Update a variable tree with new values"""
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)

        # Add variables
        for name, value in variables.items():
            if name.startswith("__") and name.endswith("__"):
                continue  # Skip dunder methods

            value_type = type(value).__name__
            value_str = self._format_value(value)

            item = tree.insert("", "end", text=name, values=(value_type, value_str))

            # Add expandable items for complex objects
            if isinstance(value, (dict, list, tuple)) and len(str(value)) > 50:
                self._add_expandable_item(tree, item, value)

    def _format_value(self, value: Any, max_length: int = 100) -> str:
        """Format a value for display"""
        try:
            value_str = repr(value)
            if len(value_str) > max_length:
                value_str = value_str[: max_length - 3] + "..."
            return value_str
        except Exception:
            return f"<{type(value).__name__} object>"

    def _add_expandable_item(self, tree: ttk.Treeview, parent_item: str, value: Any):
        """Add expandable child items for complex objects"""
        try:
            if isinstance(value, dict):
                for k, v in list(value.items())[:10]:  # Limit to first 10 items
                    child_item = tree.insert(
                        parent_item,
                        "end",
                        text=str(k),
                        values=(type(v).__name__, self._format_value(v)),
                    )
                    if isinstance(v, (dict, list, tuple)):
                        self._add_expandable_item(tree, child_item, v)

            elif isinstance(value, (list, tuple)):
                for i, v in enumerate(list(value)[:10]):  # Limit to first 10 items
                    child_item = tree.insert(
                        parent_item,
                        "end",
                        text=f"[{i}]",
                        values=(type(v).__name__, self._format_value(v)),
                    )
                    if isinstance(v, (dict, list, tuple)):
                        self._add_expandable_item(tree, child_item, v)
        except Exception as e:
            tree.insert(parent_item, "end", text="<error>", values=("", str(e)))

    def add_watch_expression(self):
        """Add a new watch expression"""
        expression = self.watch_entry.get().strip()
        if expression and expression not in self.watch_expressions:
            self.watch_expressions.append(expression)
            self.watch_entry.delete(0, tk.END)

    def _update_watch_expressions(self, local_vars: Dict, global_vars: Dict):
        """Update watch expression values"""
        # Clear existing items
        for item in self.watch_tree.get_children():
            self.watch_tree.delete(item)

        # Evaluate watch expressions
        combined_vars = {**global_vars, **local_vars}
        for i, expression in enumerate(self.watch_expressions):
            try:
                value = eval(expression, {"__builtins__": {}}, combined_vars)
                value_str = self._format_value(value)
            except Exception as e:
                value_str = f"Error: {str(e)}"

            self.watch_tree.insert(
                "", "end", text=str(i + 1), values=(expression, value_str)
            )


class CallStackVisualizer:
    """Visualizes the call stack during debugging"""

    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.setup_ui()
        self.call_stack = []

    def setup_ui(self):
        """Create the call stack interface"""
        self.frame = ttk.LabelFrame(self.parent, text="Call Stack")
        self.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tree = ttk.Treeview(
            self.frame, columns=("function", "file", "line"), show="tree headings"
        )
        self.tree.heading("#0", text="#")
        self.tree.heading("function", text="Function")
        self.tree.heading("file", text="File")
        self.tree.heading("line", text="Line")

        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            self.frame, orient=tk.VERTICAL, command=self.tree.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

    def update_call_stack(self, frame):
        """Update call stack display"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Build call stack
        self.call_stack = []
        current_frame = frame
        level = 0

        while current_frame and level < 50:  # Limit depth to prevent infinite loops
            filename = current_frame.f_code.co_filename
            function_name = current_frame.f_code.co_name
            line_number = current_frame.f_lineno

            self.call_stack.append(
                {
                    "level": level,
                    "function": function_name,
                    "file": filename,
                    "line": line_number,
                    "frame": current_frame,
                }
            )

            # Add to tree
            self.tree.insert(
                "",
                "end",
                text=str(level),
                values=(function_name, filename.split("/")[-1], line_number),
            )

            current_frame = current_frame.f_back
            level += 1


class VisualDebugger:
    """Main visual debugger interface"""

    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.setup_ui()

        # Core components
        self.breakpoint_manager = BreakpointManager()
        self.variable_inspector = VariableInspector(self.variables_frame)
        self.call_stack = CallStackVisualizer(self.stack_frame)

        # Debugging state
        self.is_debugging = False
        self.current_frame = None
        self.debug_thread = None
        self.step_mode = None  # 'over', 'into', 'out', 'continue'

        # Communication with debugger
        self.command_queue = queue.Queue()
        self.result_queue = queue.Queue()

    def setup_ui(self):
        """Create the debugger interface"""
        # Main debugging panel
        self.debug_panel = ttk.PanedWindow(self.parent, orient=tk.HORIZONTAL)
        self.debug_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left panel - controls and stack
        left_panel = ttk.Frame(self.debug_panel)
        self.debug_panel.add(left_panel, weight=1)

        # Debug controls
        controls_frame = ttk.LabelFrame(left_panel, text="Debug Controls")
        controls_frame.pack(fill=tk.X, padx=5, pady=5)

        button_frame = ttk.Frame(controls_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            button_frame, text="▶ Continue", command=self.continue_execution
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="⏭ Step Over", command=self.step_over).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(button_frame, text="⏬ Step Into", command=self.step_into).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(button_frame, text="⏫ Step Out", command=self.step_out).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(button_frame, text="⏹ Stop", command=self.stop_debugging).pack(
            side=tk.LEFT, padx=2
        )

        # Call stack frame
        self.stack_frame = ttk.Frame(left_panel)
        self.stack_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Right panel - variables
        self.variables_frame = ttk.Frame(self.debug_panel)
        self.debug_panel.add(self.variables_frame, weight=1)

    def start_debugging(self, code: str, filename: str = "<debug>"):
        """Start debugging session"""
        if self.is_debugging:
            return False

        self.is_debugging = True
        self.debug_thread = threading.Thread(
            target=self._debug_worker, args=(code, filename)
        )
        self.debug_thread.daemon = True
        self.debug_thread.start()
        return True

    def _debug_worker(self, code: str, filename: str):
        """Debug worker thread"""
        try:
            # Create custom debugger
            debugger = Time_WarpDebugger(self)

            # Set up debugging environment
            global_vars = {"__name__": "__main__", "__file__": filename}
            local_vars = {}

            # Compile and execute code
            compiled_code = compile(code, filename, "exec")
            debugger.run(compiled_code, global_vars, local_vars)

        except Exception as e:
            self._handle_debug_error(e)
        finally:
            self.is_debugging = False

    def _handle_debug_error(self, error: Exception):
        """Handle debugging errors"""
        error_msg = f"Debug Error: {str(error)}\n{traceback.format_exc()}"
        print(error_msg)  # For now, print to console

    def continue_execution(self):
        """Continue execution until next breakpoint"""
        if self.is_debugging:
            self.command_queue.put(("continue", None))

    def step_over(self):
        """Step over current line"""
        if self.is_debugging:
            self.command_queue.put(("step_over", None))

    def step_into(self):
        """Step into function calls"""
        if self.is_debugging:
            self.command_queue.put(("step_into", None))

    def step_out(self):
        """Step out of current function"""
        if self.is_debugging:
            self.command_queue.put(("step_out", None))

    def stop_debugging(self):
        """Stop debugging session"""
        if self.is_debugging:
            self.command_queue.put(("stop", None))
            self.is_debugging = False

    def update_debug_display(self, frame, event, arg):
        """Update debugger display with current state"""
        self.current_frame = frame

        # Update call stack
        self.call_stack.update_call_stack(frame)

        # Update variables
        local_vars = frame.f_locals.copy()
        global_vars = frame.f_globals.copy()
        self.variable_inspector.update_variables(local_vars, global_vars)


class Time_WarpDebugger(pdb.Pdb):
    """Custom debugger for Time_Warp IDE"""

    def __init__(self, visual_debugger: VisualDebugger):
        super().__init__()
        self.visual_debugger = visual_debugger

    def user_call(self, frame, argument_list):
        """Called when entering a function"""
        self.visual_debugger.update_debug_display(frame, "call", argument_list)
        self._wait_for_command()

    def user_line(self, frame):
        """Called at each line of code"""
        filename = frame.f_code.co_filename
        line_number = frame.f_lineno

        # Check for breakpoint
        if self.visual_debugger.breakpoint_manager.is_breakpoint_hit(
            filename, line_number, frame.f_locals
        ):
            self.visual_debugger.update_debug_display(frame, "line", None)
            self._wait_for_command()

    def user_return(self, frame, return_value):
        """Called when returning from a function"""
        self.visual_debugger.update_debug_display(frame, "return", return_value)

    def user_exception(self, frame, exc_info):
        """Called when an exception occurs"""
        self.visual_debugger.update_debug_display(frame, "exception", exc_info)
        self._wait_for_command()

    def _wait_for_command(self):
        """Wait for command from UI thread"""
        try:
            command, arg = self.visual_debugger.command_queue.get(timeout=0.1)

            if command == "continue":
                return
            elif command == "step_over":
                if self.curframe:
                    self.set_next(self.curframe)
            elif command == "step_into":
                self.set_step()
            elif command == "step_out":
                if self.curframe:
                    self.set_return(self.curframe)
            elif command == "stop":
                self.set_quit()

        except queue.Empty:
            # No command available, continue waiting
            self._wait_for_command()
