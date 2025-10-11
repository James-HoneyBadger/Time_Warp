"""
Educational and Debugging Components for Time_Warp IDE
Contains tutorial, exercise, version control, and debugging functionality.
"""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime


class EducationalTutorials:
    """Provides guided tutorials for learning Time_Warp programming"""

    def __init__(self, ide):
        self.ide = ide
        self.current_tutorial = None
        self.tutorial_step = 0

    def start_tutorial(self, tutorial_id):
        """Start a specific tutorial"""
        messagebox.showinfo("Tutorial", f"Starting tutorial: {tutorial_id}")


class ExerciseMode:
    """Provides coding exercises and challenges"""

    def __init__(self, ide):
        self.ide = ide
        self.current_exercise = None

    def start_exercise(self, exercise_id):
        """Start a coding exercise"""
        messagebox.showinfo("Exercise", f"Starting exercise: {exercise_id}")


class VersionControlSystem:
    """Simple version control for Time_Warp projects"""

    def __init__(self, ide):
        self.ide = ide
        self.history = []
        self.current_version = -1

    def save_version(self, comment=""):
        """Save current state as a new version"""
        content = self.ide.editor.get("1.0", tk.END)
        version = {
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "comment": comment,
        }
        self.history.append(version)
        self.current_version = len(self.history) - 1


class AdvancedDebugger:
    """Enhanced debugger with step-through execution, variable inspection, and call stack visualization"""

    def __init__(self, ide):
        self.ide = ide
        self.breakpoints = set()
        self.debugging = False
        self.current_line = 0
        self.step_mode = False
        self.call_stack = []
        self.variable_watches = set()
        self.debug_windows = {}
        # Defer setup_debug_tags until editor is available
        self.tags_setup = False

    def setup_debug_tags(self):
        """Setup text tags for debugging visualization"""
        if not hasattr(self.ide, "editor") or not self.ide.editor:
            return  # Editor not ready yet

        self.ide.editor.tag_configure(
            "breakpoint", background="#FFE6E6", foreground="#CC0000"
        )
        self.ide.editor.tag_configure(
            "current_line",
            background="#E6F3FF",
            foreground="#0066CC",
            relief="raised",
            borderwidth=1,
        )
        self.ide.editor.tag_configure(
            "call_stack_line", background="#F0F8E6", foreground="#336600"
        )
        self.tags_setup = True

    def toggle_breakpoint(self, line_number):
        """Toggle breakpoint at specified line"""
        if line_number in self.breakpoints:
            self.breakpoints.remove(line_number)
            self.ide.editor.tag_remove(
                "breakpoint", f"{line_number}.0", f"{line_number}.end"
            )
        else:
            self.breakpoints.add(line_number)
            self.ide.editor.tag_add(
                "breakpoint", f"{line_number}.0", f"{line_number}.end"
            )

        # Sync with interpreter
        self.sync_breakpoints_with_interpreter()

    def sync_breakpoints_with_interpreter(self):
        """Synchronize breakpoints with the interpreter"""
        try:
            if hasattr(self.ide, "interpreter") and self.ide.interpreter is not None:
                # Clear interpreter breakpoints
                self.ide.interpreter.breakpoints.clear()
                # Add all breakpoints (convert to zero-based)
                for line_num in self.breakpoints:
                    self.ide.interpreter.breakpoints.add(line_num - 1)
        except Exception as e:
            print(f"Error syncing breakpoints: {e}")

    def start_debug_session(self):
        """Start a debugging session"""
        self.debugging = True
        self.step_mode = True
        self.call_stack.clear()

        # Show debug windows
        self.show_variables_window()
        self.show_call_stack_window()

        # Update status
        if hasattr(self.ide, "status_label"):
            self.ide.status_label.config(
                text="🐛 Debug Mode - Ready to step through code"
            )

    def stop_debug_session(self):
        """Stop the debugging session"""
        self.debugging = False
        self.step_mode = False
        self.current_line = 0

        # Clear debug highlighting
        self.ide.editor.tag_remove("current_line", "1.0", tk.END)
        self.ide.editor.tag_remove("call_stack_line", "1.0", tk.END)

        # Close debug windows
        self.close_debug_windows()

        # Update status
        if hasattr(self.ide, "status_label"):
            self.ide.status_label.config(text="✨ Ready to Code!")

    def step_over(self):
        """Execute next line (step over)"""
        if not self.debugging:
            self.start_debug_session()

        # This would integrate with the interpreter to execute one line
        if hasattr(self.ide, "interpreter") and self.ide.interpreter:
            try:
                # Set step mode in interpreter
                self.ide.interpreter.debug_mode = True
                self.ide.interpreter.step_mode = True

                # Execute one step
                # This is a simplified implementation
                self.highlight_current_line(self.current_line + 1)
                self.current_line += 1

                # Update variable watches
                self.update_variable_watches()

            except Exception as e:
                print(f"Step over error: {e}")

    def step_into(self):
        """Step into function/subroutine calls"""
        if not self.debugging:
            self.start_debug_session()

        # Similar to step_over but follows into subroutines
        self.step_over()  # Simplified implementation

    def step_out(self):
        """Step out of current function/subroutine"""
        if not self.debugging:
            return

        # Execute until return from current call level
        if self.call_stack:
            target_level = len(self.call_stack) - 1
            # Continue execution until we're back at target level
            self.continue_execution()

    def continue_execution(self):
        """Continue execution until next breakpoint"""
        if not self.debugging:
            return

        self.step_mode = False
        # This would tell interpreter to run until breakpoint
        if hasattr(self.ide, "interpreter") and self.ide.interpreter:
            self.ide.interpreter.step_mode = False

    def highlight_current_line(self, line_number):
        """Highlight the currently executing line"""
        # Clear previous highlighting
        self.ide.editor.tag_remove("current_line", "1.0", tk.END)

        # Highlight current line
        if line_number > 0:
            self.ide.editor.tag_add(
                "current_line", f"{line_number}.0", f"{line_number}.end"
            )

            # Scroll to current line
            self.ide.editor.see(f"{line_number}.0")

        self.current_line = line_number

    def add_variable_watch(self, var_name):
        """Add a variable to the watch list"""
        self.variable_watches.add(var_name)
        self.update_variable_watches()

    def remove_variable_watch(self, var_name):
        """Remove a variable from the watch list"""
        self.variable_watches.discard(var_name)
        self.update_variable_watches()

    def update_variable_watches(self):
        """Update the variable watch window"""
        if "variables" in self.debug_windows:
            try:
                window = self.debug_windows["variables"]
                text_widget = window.children["!text"]

                text_widget.delete("1.0", tk.END)
                text_widget.insert("1.0", "=== Variable Watches ===\n\n")

                if hasattr(self.ide, "interpreter") and self.ide.interpreter:
                    for var_name in sorted(self.variable_watches):
                        value = self.ide.interpreter.variables.get(
                            var_name, "undefined"
                        )
                        text_widget.insert(tk.END, f"{var_name}: {value}\n")

                    text_widget.insert(tk.END, "\n=== All Variables ===\n\n")
                    for var_name, value in sorted(
                        self.ide.interpreter.variables.items()
                    ):
                        text_widget.insert(tk.END, f"{var_name}: {value}\n")

            except Exception as e:
                print(f"Error updating variable watches: {e}")

    def show_variables_window(self):
        """Show the variables inspection window"""
        if "variables" in self.debug_windows:
            return  # Already open

        window = tk.Toplevel(self.ide.root)
        window.title("Variables Inspector")
        window.geometry("300x400")

        # Create text widget with scrollbar
        frame = tk.Frame(window)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        text_widget = tk.Text(frame, wrap=tk.WORD, font=("Consolas", 10))
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.config(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add watch controls
        controls_frame = tk.Frame(window)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(controls_frame, text="Watch Variable:").pack(side=tk.LEFT)
        watch_entry = tk.Entry(controls_frame)
        watch_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        def add_watch():
            var_name = watch_entry.get().strip()
            if var_name:
                self.add_variable_watch(var_name)
                watch_entry.delete(0, tk.END)

        tk.Button(controls_frame, text="Add Watch", command=add_watch).pack(
            side=tk.RIGHT
        )

        # Bind Enter key to add watch
        watch_entry.bind("<Return>", lambda e: add_watch())

        self.debug_windows["variables"] = window
        self.update_variable_watches()

        # Handle window closing
        window.protocol(
            "WM_DELETE_WINDOW", lambda: self.close_debug_window("variables")
        )

    def show_call_stack_window(self):
        """Show the call stack window"""
        if "call_stack" in self.debug_windows:
            return  # Already open

        window = tk.Toplevel(self.ide.root)
        window.title("Call Stack")
        window.geometry("400x300")

        # Create listbox for call stack
        frame = tk.Frame(window)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        listbox = tk.Listbox(frame, font=("Consolas", 10))
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=listbox.yview)
        listbox.config(yscrollcommand=scrollbar.set)

        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.debug_windows["call_stack"] = window

        # Handle window closing
        window.protocol(
            "WM_DELETE_WINDOW", lambda: self.close_debug_window("call_stack")
        )

        # Update call stack display
        self.update_call_stack_display()

    def update_call_stack_display(self):
        """Update the call stack display"""
        if "call_stack" in self.debug_windows:
            try:
                window = self.debug_windows["call_stack"]
                listbox = window.children["!frame"].children["!listbox"]

                listbox.delete(0, tk.END)
                for i, frame_info in enumerate(self.call_stack):
                    listbox.insert(tk.END, f"{i}: {frame_info}")

            except Exception as e:
                print(f"Error updating call stack: {e}")

    def close_debug_window(self, window_name):
        """Close a specific debug window"""
        if window_name in self.debug_windows:
            self.debug_windows[window_name].destroy()
            del self.debug_windows[window_name]

    def close_debug_windows(self):
        """Close all debug windows"""
        for window in list(self.debug_windows.values()):
            try:
                window.destroy()
            except:
                pass
        self.debug_windows.clear()
