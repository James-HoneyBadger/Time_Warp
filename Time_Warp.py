#!/usr/bin/env python3
"""
Time_Warp IDE - Simple Educational Programming Environment

A minimal Tkinter-based IDE for running multi-language programs through the Time_Warp interpreter.
Supports PILOT, BASIC, Logo, Pascal, Prolog, Forth, Perl, Python, and JavaScript execution.

Features:
- Simple text editor with Courier font
- One-click program execution
- Integrated interpreter with 9+ language support
- Turtle graphics for visual languages
- Educational error messages

Usage:
    python Time_Warp.py

The IDE provides a basic text editing interface where users can write and execute
programs in multiple programming languages with immediate visual feedback.
"""

import tkinter as tk
from tkinter import messagebox
from core.interpreter import Time_WarpInterpreter


class TimeWarpApp:
    """
    Main application class for the Time_Warp IDE.

    Creates a simple GUI with:
    - Text area for code editing
    - Run button for program execution
    - Integrated Time_Warp interpreter for multi-language support
    """

    def __init__(self, root):
        """
        Initialize the Time_Warp IDE application.

        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Time_Warp IDE v1.1")
        self.root.geometry("800x600")  # Set reasonable default size

        # Create main text editing area
        self.text_area = tk.Text(
            root,
            wrap="word",
            font=("Courier", 12),
            undo=True,  # Enable undo/redo
            padx=10,
            pady=10,
        )
        self.text_area.pack(expand=True, fill="both")

        # Create run button at bottom
        self.run_button = tk.Button(
            root,
            text="▶ Run Program",
            command=self.run_program,
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            height=2,
        )
        self.run_button.pack(side="bottom", fill="x", padx=10, pady=10)

        # Initialize the Time_Warp interpreter
        self.interpreter = Time_WarpInterpreter()

        # Bind keyboard shortcuts
        self.root.bind("<F5>", lambda e: self.run_program())
        self.root.bind("<Control-r>", lambda e: self.run_program())

        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def run_program(self):
        """
        Execute the program currently in the text area.

        Gets the code from the text widget, validates it's not empty,
        and runs it through the Time_Warp interpreter.
        """
        program_code = self.text_area.get("1.0", "end").strip()

        if not program_code:
            messagebox.showwarning(
                "No Code",
                "Please enter a program to run.\n\nTry copying one of the examples from the README.md file.",
            )
            return

        try:
            # Clear any previous output in interpreter
            # Run the program through the interpreter
            self.interpreter.run_program(program_code)

            # Show success message
            messagebox.showinfo(
                "Program Complete",
                "Program execution finished!\n\nCheck the console output for results.",
            )

        except Exception as e:
            messagebox.showerror(
                "Execution Error",
                f"An error occurred while running the program:\n\n{str(e)}",
            )

    def on_closing(self):
        """Handle window close event."""
        if messagebox.askokcancel("Quit", "Do you want to quit Time_Warp IDE?"):
            self.root.destroy()


def main():
    """
    Main entry point for the Time_Warp IDE application.

    Creates the Tkinter root window and starts the application.
    """
    root = tk.Tk()
    app = TimeWarpApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
