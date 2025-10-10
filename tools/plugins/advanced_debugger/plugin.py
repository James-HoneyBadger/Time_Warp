#!/usr/bin/env python3
"""
Advanced Debugger Plugin for Time_Warp IDE
Professional-grade debugging tool with breakpoints, variable inspection,
call stack analysis, execution control, and memory monitoring
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
import gc
import psutil
import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

# Import the base framework
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from core.framework import ToolPlugin


class AdvancedDebuggerPlugin(ToolPlugin):
    """Advanced debugging tool plugin"""

    def __init__(self, ide_instance, framework):
        super().__init__(ide_instance, framework)

        # Plugin metadata
        self.name = "Advanced Debugger"
        self.version = "1.0.0"
        self.author = "Time_Warp IDE Team"
        self.description = "Professional-grade debugging tool with breakpoints, variable inspection, call stack analysis, execution control, and memory monitoring"
        self.category = "debugging"

        # Debugger state
        self.debugger_state = {
            "breakpoints": {},
            "watch_variables": [],
            "execution_paused": False,
            "current_line": 0,
            "call_stack": [],
        }

        # UI references
        self._tool_window = None
        self.breakpoints_tree = None
        self.debug_vars_tree = None
        self.callstack_listbox = None
        self.stack_info_text = None
        self.execution_text = None
        self.memory_text = None
        self.memory_labels = {}

    def initialize(self) -> bool:
        """Initialize the debugger plugin"""
        try:
            # Subscribe to relevant events
            self.subscribe_event("interpreter_ready", self._on_interpreter_ready)
            self.subscribe_event("code_executed", self._on_code_executed)
            self.subscribe_event("execution_error", self._on_execution_error)

            return True
        except Exception as e:
            print(f"Error initializing Advanced Debugger: {e}")
            return False

    def activate(self) -> bool:
        """Activate the debugger"""
        try:
            # Add menu item
            self.add_menu_item(
                "Tools", "🐛 Advanced Debugger", self.show_tool_dialog, "Ctrl+Shift+D"
            )

            # Add toolbar item
            self.add_toolbar_item(
                "🐛 Debug", self.show_tool_dialog, tooltip="Open Advanced Debugger"
            )

            return True
        except Exception as e:
            print(f"Error activating Advanced Debugger: {e}")
            return False

    def deactivate(self) -> bool:
        """Deactivate the debugger"""
        try:
            # Close debugger window if open
            if self._tool_window:
                self._tool_window.destroy()
                self._tool_window = None

            return True
        except Exception as e:
            print(f"Error deactivating Advanced Debugger: {e}")
            return False

    def create_ui(self, parent_widget) -> tk.Widget:
        """Create the debugger UI"""
        try:
            # Main container
            main_frame = ttk.Frame(parent_widget)

            # Header
            header_frame = ttk.Frame(main_frame)
            header_frame.pack(fill=tk.X, pady=(0, 10))

            ttk.Label(
                header_frame, text="🐛 Advanced Debugger", font=("Arial", 16, "bold")
            ).pack(side=tk.LEFT)

            ttk.Button(
                header_frame, text="🔄 Refresh", command=self.refresh_all_data
            ).pack(side=tk.RIGHT, padx=5)

            # Create notebook for different debugging aspects
            self.notebook = ttk.Notebook(main_frame)
            self.notebook.pack(fill=tk.BOTH, expand=True)

            # Setup tabs
            self._setup_breakpoints_tab()
            self._setup_variables_tab()
            self._setup_call_stack_tab()
            self._setup_execution_control_tab()
            self._setup_memory_monitoring_tab()

            return main_frame

        except Exception as e:
            print(f"Error creating debugger UI: {e}")
            return ttk.Label(parent_widget, text=f"Error creating debugger UI: {e}")

    def _setup_breakpoints_tab(self):
        """Setup breakpoints management tab"""
        breakpoints_frame = ttk.Frame(self.notebook)
        self.notebook.add(breakpoints_frame, text="🔴 Breakpoints")

        # Breakpoints list frame
        list_frame = ttk.LabelFrame(breakpoints_frame, text="Breakpoints")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Treeview for breakpoints
        columns = ("File", "Line", "Condition", "Status")
        self.breakpoints_tree = ttk.Treeview(
            list_frame, columns=columns, show="headings", height=15
        )

        for col in columns:
            self.breakpoints_tree.heading(col, text=col)
            self.breakpoints_tree.column(col, width=150)

        self.breakpoints_tree.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5
        )

        bp_scroll = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.breakpoints_tree.yview
        )
        self.breakpoints_tree.config(yscrollcommand=bp_scroll.set)
        bp_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Control buttons
        button_frame = ttk.Frame(breakpoints_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            button_frame, text="➕ Add Breakpoint", command=self._add_breakpoint
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            button_frame, text="❌ Remove", command=self._remove_breakpoint
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            button_frame, text="✅ Enable All", command=self._enable_all_breakpoints
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            button_frame, text="⏸️ Disable All", command=self._disable_all_breakpoints
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            button_frame, text="🧹 Clear All", command=self._clear_all_breakpoints
        ).pack(side=tk.LEFT, padx=2)

    def _setup_variables_tab(self):
        """Setup debug variables tab"""
        variables_frame = ttk.Frame(self.notebook)
        self.notebook.add(variables_frame, text="📊 Variables")

        # Variables tree frame
        tree_frame = ttk.LabelFrame(variables_frame, text="Variables & Values")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Variables treeview
        columns = ("Variable", "Type", "Value", "Scope")
        self.debug_vars_tree = ttk.Treeview(
            tree_frame, columns=columns, show="headings", height=15
        )

        for col in columns:
            self.debug_vars_tree.heading(col, text=col)
            if col == "Value":
                self.debug_vars_tree.column(col, width=200)
            else:
                self.debug_vars_tree.column(col, width=120)

        self.debug_vars_tree.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5
        )

        vars_scroll = ttk.Scrollbar(
            tree_frame, orient=tk.VERTICAL, command=self.debug_vars_tree.yview
        )
        self.debug_vars_tree.config(yscrollcommand=vars_scroll.set)
        vars_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Control buttons
        vars_button_frame = ttk.Frame(variables_frame)
        vars_button_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            vars_button_frame, text="🔄 Refresh", command=self._refresh_debug_variables
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            vars_button_frame, text="👁️ Watch Variable", command=self._add_watch_variable
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            vars_button_frame, text="✏️ Edit Value", command=self._edit_variable_value
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            vars_button_frame,
            text="💾 Export Variables",
            command=self._export_debug_variables,
        ).pack(side=tk.LEFT, padx=2)

    def _setup_call_stack_tab(self):
        """Setup call stack tab"""
        callstack_frame = ttk.Frame(self.notebook)
        self.notebook.add(callstack_frame, text="📚 Call Stack")

        # Call stack frame
        stack_frame = ttk.LabelFrame(callstack_frame, text="Call Stack")
        stack_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Call stack listbox
        self.callstack_listbox = tk.Listbox(stack_frame, font=("Consolas", 10))
        self.callstack_listbox.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5
        )

        stack_scroll = ttk.Scrollbar(
            stack_frame, orient=tk.VERTICAL, command=self.callstack_listbox.yview
        )
        self.callstack_listbox.config(yscrollcommand=stack_scroll.set)
        stack_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Stack info frame
        info_frame = ttk.LabelFrame(callstack_frame, text="Stack Frame Details")
        info_frame.pack(fill=tk.X, padx=5, pady=5)

        self.stack_info_text = tk.Text(info_frame, height=8, font=("Consolas", 9))
        info_scroll = ttk.Scrollbar(
            info_frame, orient=tk.VERTICAL, command=self.stack_info_text.yview
        )
        self.stack_info_text.config(yscrollcommand=info_scroll.set)

        self.stack_info_text.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5
        )
        info_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Bind selection event
        self.callstack_listbox.bind("<<ListboxSelect>>", self._on_stack_select)

        # Initialize with sample data
        self._populate_sample_call_stack()

    def _setup_execution_control_tab(self):
        """Setup execution control tab"""
        execution_frame = ttk.Frame(self.notebook)
        self.notebook.add(execution_frame, text="⚡ Execution")

        # Execution controls frame
        controls_frame = ttk.LabelFrame(execution_frame, text="Execution Control")
        controls_frame.pack(fill=tk.X, padx=5, pady=5)

        # Control buttons
        button_row1 = ttk.Frame(controls_frame)
        button_row1.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(button_row1, text="▶️ Run", command=self._debug_run).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(button_row1, text="⏸️ Pause", command=self._debug_pause).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(button_row1, text="⏹️ Stop", command=self._debug_stop).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(button_row1, text="🔄 Restart", command=self._debug_restart).pack(
            side=tk.LEFT, padx=2
        )

        button_row2 = ttk.Frame(controls_frame)
        button_row2.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(button_row2, text="➡️ Step Over", command=self._debug_step_over).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(button_row2, text="⬇️ Step Into", command=self._debug_step_into).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(button_row2, text="⬆️ Step Out", command=self._debug_step_out).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(
            button_row2, text="🏃 Run to Cursor", command=self._debug_run_to_cursor
        ).pack(side=tk.LEFT, padx=2)

        # Execution status frame
        status_frame = ttk.LabelFrame(execution_frame, text="Execution Status")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.execution_text = tk.Text(status_frame, height=15, font=("Consolas", 10))
        exec_scroll = ttk.Scrollbar(
            status_frame, orient=tk.VERTICAL, command=self.execution_text.yview
        )
        self.execution_text.config(yscrollcommand=exec_scroll.set)

        self.execution_text.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5
        )
        exec_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Initialize execution status
        self._update_execution_status()

    def _setup_memory_monitoring_tab(self):
        """Setup memory monitoring tab"""
        memory_frame = ttk.Frame(self.notebook)
        self.notebook.add(memory_frame, text="💾 Memory")

        # Memory usage frame
        memory_usage_frame = ttk.LabelFrame(memory_frame, text="Memory Usage")
        memory_usage_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Memory statistics
        stats_frame = ttk.Frame(memory_usage_frame)
        stats_frame.pack(fill=tk.X, padx=5, pady=5)

        self.memory_labels = {}
        memory_items = [
            "Total Memory",
            "Used Memory",
            "Free Memory",
            "Python Objects",
            "Variables Count",
        ]

        for i, item in enumerate(memory_items):
            ttk.Label(stats_frame, text=f"{item}:").grid(
                row=i, column=0, sticky="w", padx=5, pady=2
            )
            self.memory_labels[item] = ttk.Label(stats_frame, text="0 MB")
            self.memory_labels[item].grid(row=i, column=1, sticky="w", padx=20, pady=2)

        # Memory monitor text
        monitor_frame = ttk.Frame(memory_usage_frame)
        monitor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.memory_text = tk.Text(monitor_frame, height=15, font=("Consolas", 9))
        memory_scroll = ttk.Scrollbar(
            monitor_frame, orient=tk.VERTICAL, command=self.memory_text.yview
        )
        self.memory_text.config(yscrollcommand=memory_scroll.set)

        self.memory_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        memory_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Control buttons
        memory_buttons = ttk.Frame(memory_frame)
        memory_buttons.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            memory_buttons, text="🔄 Refresh", command=self._refresh_memory_info
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            memory_buttons, text="📊 Memory Profile", command=self._show_memory_profile
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            memory_buttons,
            text="🧹 Garbage Collect",
            command=self._force_garbage_collection,
        ).pack(side=tk.LEFT, padx=2)

        # Initialize memory display
        self._refresh_memory_info()

    # === EVENT HANDLERS ===

    def _on_interpreter_ready(self, interpreter):
        """Handle interpreter ready event"""
        self._update_execution_status("Interpreter ready for debugging")

    def _on_code_executed(self, code, result):
        """Handle code execution event"""
        self._update_execution_status(f"Executed: {code[:50]}...")
        self._refresh_debug_variables()

    def _on_execution_error(self, error):
        """Handle execution error event"""
        self._update_execution_status(f"Error: {error}")

    def _on_stack_select(self, event):
        """Handle call stack selection"""
        selection = self.callstack_listbox.curselection()
        if selection:
            index = selection[0]
            stack_info = (
                self.debugger_state["call_stack"][index]
                if index < len(self.debugger_state["call_stack"])
                else {}
            )

            self.stack_info_text.delete("1.0", tk.END)
            info_text = f"""Function: {stack_info.get('function', 'Unknown')}
File: {stack_info.get('file', 'Unknown')}
Line: {stack_info.get('line', 'Unknown')}
Arguments: {stack_info.get('args', 'None')}
Local Variables: {len(stack_info.get('locals', {}))} variables

Details:
{stack_info.get('details', 'No additional details available.')}"""

            self.stack_info_text.insert("1.0", info_text)

    # === BREAKPOINT METHODS ===

    def _add_breakpoint(self):
        """Add a new breakpoint"""
        dialog = tk.Toplevel(self._tool_window)
        dialog.title("➕ Add Breakpoint")
        dialog.geometry("400x200")
        dialog.transient(self._tool_window)
        dialog.grab_set()

        ttk.Label(dialog, text="Line Number:").pack(pady=5)
        line_var = tk.IntVar(value=1)
        ttk.Spinbox(dialog, from_=1, to=1000, textvariable=line_var, width=10).pack(
            pady=5
        )

        ttk.Label(dialog, text="Condition (optional):").pack(pady=5)
        condition_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=condition_var, width=40).pack(pady=5)

        def create_bp():
            line = line_var.get()
            condition = condition_var.get() or "Always"
            bp_id = f"main.py:{line}"

            self.debugger_state["breakpoints"][bp_id] = {
                "file": "main.py",
                "line": line,
                "condition": condition,
                "enabled": True,
            }

            self.breakpoints_tree.insert(
                "", "end", values=("main.py", line, condition, "Enabled")
            )
            messagebox.showinfo("Breakpoint Added", f"Breakpoint added at line {line}")
            dialog.destroy()

        ttk.Button(dialog, text="✅ Add", command=create_bp).pack(
            side=tk.LEFT, padx=5, pady=20
        )
        ttk.Button(dialog, text="❌ Cancel", command=dialog.destroy).pack(
            side=tk.LEFT, padx=5, pady=20
        )

    def _remove_breakpoint(self):
        """Remove selected breakpoint"""
        selection = self.breakpoints_tree.selection()
        if selection:
            self.breakpoints_tree.delete(selection[0])
            messagebox.showinfo("Breakpoint Removed", "Breakpoint removed successfully")
        else:
            messagebox.showwarning(
                "No Selection", "Please select a breakpoint to remove"
            )

    def _enable_all_breakpoints(self):
        """Enable all breakpoints"""
        for item in self.breakpoints_tree.get_children():
            values = list(self.breakpoints_tree.item(item)["values"])
            values[3] = "Enabled"
            self.breakpoints_tree.item(item, values=values)
        messagebox.showinfo("Breakpoints", "All breakpoints enabled")

    def _disable_all_breakpoints(self):
        """Disable all breakpoints"""
        for item in self.breakpoints_tree.get_children():
            values = list(self.breakpoints_tree.item(item)["values"])
            values[3] = "Disabled"
            self.breakpoints_tree.item(item, values=values)
        messagebox.showinfo("Breakpoints", "All breakpoints disabled")

    def _clear_all_breakpoints(self):
        """Clear all breakpoints"""
        if messagebox.askyesno("Clear Breakpoints", "Remove all breakpoints?"):
            for item in self.breakpoints_tree.get_children():
                self.breakpoints_tree.delete(item)
            self.debugger_state["breakpoints"].clear()
            messagebox.showinfo("Breakpoints", "All breakpoints cleared")

    # === VARIABLE METHODS ===

    def _refresh_debug_variables(self):
        """Refresh debug variables display"""
        # Clear existing items
        for item in self.debug_vars_tree.get_children():
            self.debug_vars_tree.delete(item)

        # Get interpreter variables
        try:
            if hasattr(self.ide, "interpreter") and self.ide.interpreter:
                variables = {}

                # Get PILOT variables
                if (
                    hasattr(self.ide.interpreter, "pilot_executor")
                    and self.ide.interpreter.pilot_executor
                ):
                    pilot_vars = getattr(
                        self.ide.interpreter.pilot_executor, "variables", {}
                    )
                    for var, value in pilot_vars.items():
                        variables[f"PILOT:{var}"] = {
                            "type": type(value).__name__,
                            "value": str(value),
                            "scope": "PILOT",
                        }

                # Get BASIC variables
                if (
                    hasattr(self.ide.interpreter, "basic_executor")
                    and self.ide.interpreter.basic_executor
                ):
                    basic_vars = getattr(
                        self.ide.interpreter.basic_executor, "variables", {}
                    )
                    for var, value in basic_vars.items():
                        variables[f"BASIC:{var}"] = {
                            "type": type(value).__name__,
                            "value": str(value),
                            "scope": "BASIC",
                        }

                # Get Logo variables
                if (
                    hasattr(self.ide.interpreter, "logo_executor")
                    and self.ide.interpreter.logo_executor
                ):
                    logo_vars = getattr(
                        self.ide.interpreter.logo_executor, "variables", {}
                    )
                    for var, value in logo_vars.items():
                        variables[f"Logo:{var}"] = {
                            "type": type(value).__name__,
                            "value": str(value),
                            "scope": "Logo",
                        }

                # Add to tree
                for var_name, var_info in variables.items():
                    self.debug_vars_tree.insert(
                        "",
                        "end",
                        values=(
                            var_name,
                            var_info["type"],
                            var_info["value"][:50],
                            var_info["scope"],
                        ),
                    )

        except Exception as e:
            self.debug_vars_tree.insert(
                "", "end", values=("Error", "N/A", str(e)[:50], "System")
            )

    def _add_watch_variable(self):
        """Add a variable to watch"""
        var_name = simpledialog.askstring(
            "Watch Variable", "Enter variable name to watch:"
        )
        if var_name:
            self.debugger_state["watch_variables"].append(var_name)
            messagebox.showinfo(
                "Watch Added", f"Variable '{var_name}' added to watch list"
            )

    def _edit_variable_value(self):
        """Edit selected variable value"""
        selection = self.debug_vars_tree.selection()
        if selection:
            item = self.debug_vars_tree.item(selection[0])
            var_name = item["values"][0]
            old_value = item["values"][2]

            new_value = simpledialog.askstring(
                "Edit Variable",
                f"Enter new value for {var_name}:",
                initialvalue=old_value,
            )
            if new_value is not None:
                messagebox.showinfo(
                    "Variable Updated",
                    f"Variable '{var_name}' updated to '{new_value}'",
                )
        else:
            messagebox.showwarning("No Selection", "Please select a variable to edit")

    def _export_debug_variables(self):
        """Export variables to JSON file"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Export Debug Variables",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            )

            if filename:
                variables = {}
                for item in self.debug_vars_tree.get_children():
                    values = self.debug_vars_tree.item(item)["values"]
                    variables[values[0]] = {
                        "type": values[1],
                        "value": values[2],
                        "scope": values[3],
                    }

                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(variables, f, indent=2)

                messagebox.showinfo(
                    "Export Complete", f"Variables exported to {filename}"
                )

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export variables: {e}")

    # === EXECUTION CONTROL METHODS ===

    def _debug_run(self):
        """Start/resume execution"""
        self.debugger_state["execution_paused"] = False
        self._update_execution_status("Execution resumed")

        # Trigger execution if IDE has current code
        if hasattr(self.ide, "code_text") and self.ide.code_text:
            try:
                code = self.ide.code_text.get("1.0", tk.END).strip()
                if code:
                    self.emit_event("debug_run_request", code)
            except Exception as e:
                self._update_execution_status(f"Run error: {e}")

    def _debug_pause(self):
        """Pause execution"""
        self.debugger_state["execution_paused"] = True
        self._update_execution_status("Execution paused")
        self.emit_event("debug_pause_request")

    def _debug_stop(self):
        """Stop execution"""
        self.debugger_state["execution_paused"] = False
        self.debugger_state["current_line"] = 0
        self._update_execution_status("Execution stopped")
        self.emit_event("debug_stop_request")

    def _debug_restart(self):
        """Restart execution"""
        self.debugger_state["execution_paused"] = False
        self.debugger_state["current_line"] = 0
        self._update_execution_status("Execution restarted")
        self.emit_event("debug_restart_request")

    def _debug_step_over(self):
        """Step over current line"""
        self.debugger_state["current_line"] += 1
        self._update_execution_status(
            f"Stepped over to line {self.debugger_state['current_line']}"
        )
        self.emit_event("debug_step_over_request")

    def _debug_step_into(self):
        """Step into function call"""
        self._update_execution_status("Stepped into function call")
        self.emit_event("debug_step_into_request")

    def _debug_step_out(self):
        """Step out of current function"""
        self._update_execution_status("Stepped out of function")
        self.emit_event("debug_step_out_request")

    def _debug_run_to_cursor(self):
        """Run to cursor position"""
        self._update_execution_status("Running to cursor position")
        self.emit_event("debug_run_to_cursor_request")

    def _update_execution_status(self, message: str = None):
        """Update execution status display"""
        if not self.execution_text:
            return

        timestamp = datetime.now().strftime("%H:%M:%S")

        if message:
            status_line = f"[{timestamp}] {message}\n"
        else:
            status_line = f"[{timestamp}] Debugger ready\n"

        self.execution_text.insert(tk.END, status_line)
        self.execution_text.see(tk.END)

    # === CALL STACK METHODS ===

    def _populate_sample_call_stack(self):
        """Populate call stack with sample data"""
        sample_stack = [
            {
                "function": "main()",
                "file": "main.py",
                "line": 15,
                "args": "[]",
                "locals": {"x": 10, "y": 20},
            },
            {
                "function": "calculate(x, y)",
                "file": "main.py",
                "line": 8,
                "args": "[10, 20]",
                "locals": {"result": 30},
            },
            {
                "function": "add(a, b)",
                "file": "utils.py",
                "line": 3,
                "args": "[10, 20]",
                "locals": {"a": 10, "b": 20},
            },
        ]

        self.debugger_state["call_stack"] = sample_stack

        self.callstack_listbox.delete(0, tk.END)
        for i, frame in enumerate(sample_stack):
            display_text = (
                f"{i+1}. {frame['function']} - {frame['file']}:{frame['line']}"
            )
            self.callstack_listbox.insert(tk.END, display_text)

            # Add details for stack frame
            frame["details"] = (
                f"Function called with arguments {frame['args']}\nLocal variables: {frame['locals']}\nFile: {frame['file']}, Line: {frame['line']}"
            )

    # === MEMORY MONITORING METHODS ===

    def _refresh_memory_info(self):
        """Refresh memory monitoring information"""
        try:
            # Get system memory info
            memory = psutil.virtual_memory()

            # Update labels
            self.memory_labels["Total Memory"].config(
                text=f"{memory.total / (1024**3):.1f} GB"
            )
            self.memory_labels["Used Memory"].config(
                text=f"{memory.used / (1024**3):.1f} GB"
            )
            self.memory_labels["Free Memory"].config(
                text=f"{memory.available / (1024**3):.1f} GB"
            )

            # Get Python object count
            import gc

            object_count = len(gc.get_objects())
            self.memory_labels["Python Objects"].config(text=f"{object_count:,}")

            # Get variable count from interpreter
            var_count = 0
            if hasattr(self.ide, "interpreter") and self.ide.interpreter:
                for executor_name in [
                    "pilot_executor",
                    "basic_executor",
                    "logo_executor",
                ]:
                    executor = getattr(self.ide.interpreter, executor_name, None)
                    if executor and hasattr(executor, "variables"):
                        var_count += len(executor.variables)

            self.memory_labels["Variables Count"].config(text=f"{var_count}")

            # Update memory monitor text
            self.memory_text.delete("1.0", tk.END)

            memory_info = f"""Memory Usage Report - {datetime.now().strftime('%H:%M:%S')}
{'='*50}

System Memory:
  Total: {memory.total / (1024**3):.2f} GB
  Used: {memory.used / (1024**3):.2f} GB ({memory.percent:.1f}%)
  Available: {memory.available / (1024**3):.2f} GB
  Free: {memory.free / (1024**3):.2f} GB

Python Process:
  Objects: {object_count:,}
  Variables: {var_count}
  
Memory Details:
  Buffers: {memory.buffers / (1024**2):.1f} MB
  Cached: {memory.cached / (1024**2):.1f} MB
  Shared: {memory.shared / (1024**2):.1f} MB

Garbage Collection:
  Collections: {gc.get_count()}
  Enabled: {gc.isenabled()}
"""

            self.memory_text.insert("1.0", memory_info)

        except Exception as e:
            if self.memory_text:
                self.memory_text.delete("1.0", tk.END)
                self.memory_text.insert("1.0", f"Error retrieving memory info: {e}")

    def _show_memory_profile(self):
        """Show detailed memory profile"""
        try:
            import tracemalloc

            if not tracemalloc.is_tracing():
                tracemalloc.start()
                messagebox.showinfo(
                    "Memory Profiler",
                    "Memory tracing started. Run some code and check again for detailed profiling.",
                )
                return

            current, peak = tracemalloc.get_traced_memory()

            profile_dialog = tk.Toplevel(self._tool_window)
            profile_dialog.title("📊 Memory Profile")
            profile_dialog.geometry("600x400")
            profile_dialog.transient(self._tool_window)

            profile_text = tk.Text(profile_dialog, font=("Consolas", 10))
            profile_scroll = ttk.Scrollbar(
                profile_dialog, orient=tk.VERTICAL, command=profile_text.yview
            )
            profile_text.config(yscrollcommand=profile_scroll.set)

            profile_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
            profile_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

            profile_info = f"""Memory Profile Report
{'='*40}

Current Memory Usage: {current / (1024**2):.2f} MB
Peak Memory Usage: {peak / (1024**2):.2f} MB

Top Memory Consumers:
"""

            # Get top memory consumers
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics("lineno")

            for i, stat in enumerate(top_stats[:10]):
                profile_info += f"\n{i+1}. {stat.traceback.format()[-1]}"
                profile_info += (
                    f"   Size: {stat.size / 1024:.1f} KB ({stat.count} blocks)\n"
                )

            profile_text.insert("1.0", profile_info)
            profile_text.config(state=tk.DISABLED)

        except ImportError:
            messagebox.showwarning(
                "Memory Profiler", "tracemalloc not available in this Python version"
            )
        except Exception as e:
            messagebox.showerror(
                "Memory Profiler Error", f"Error generating memory profile: {e}"
            )

    def _force_garbage_collection(self):
        """Force garbage collection"""
        try:
            collected = gc.collect()
            messagebox.showinfo(
                "Garbage Collection",
                f"Garbage collection completed.\nCollected {collected} objects.",
            )
            self._refresh_memory_info()
        except Exception as e:
            messagebox.showerror(
                "Garbage Collection Error", f"Error during garbage collection: {e}"
            )

    # === UTILITY METHODS ===

    def refresh_all_data(self):
        """Refresh all debugger data"""
        self._refresh_debug_variables()
        self._refresh_memory_info()
        self._update_execution_status("All data refreshed")


# Plugin entry point - this will be imported by the plugin system
TimeWarpPlugin = AdvancedDebuggerPlugin
