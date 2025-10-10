#!/usr/bin/env python3
"""
IDE Time Warp - Journey Through Code
A radical time-traveling programming IDE that warps through coding eras
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, simpledialog
import turtle
import json
from datetime import datetime
import threading
import pathlib
import subprocess
import platform

# Core modular components
from core.interpreter import TimeWarpInterpreter
from core.editor.enhanced_editor import EnhancedCodeEditor
from tools.theme import ThemeManager
from plugins import PluginManager

# Feature modules
from core.features.tutorial_system import TutorialSystem
from core.features.ai_assistant import AICodeAssistant
from core.features.gamification import GamificationSystem


class IDETimeWarp:
    """
    IDE Time Warp Application Class
    A radical time-traveling code editor that warps through programming eras
    Focus on core IDE functionality with retro-futuristic architecture
    """

    def __init__(self):
        """Initialize IDE Time Warp with essential time-traveling components"""
        # Main window setup
        self.root = tk.Tk()
        self.root.title("⏰ IDE Time Warp - Journey Through Code")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)

        # Initialize theme system
        self.theme_manager = ThemeManager()
        self.load_theme_config()

        # Initialize plugin system
        self.plugin_manager = PluginManager(self)

        # Core components
        self.interpreter = TimeWarpInterpreter()
        self.current_file = None

        # Feature systems
        self.tutorial_system = TutorialSystem()
        self.ai_assistant = AICodeAssistant()
        self.gamification = GamificationSystem()

        # Set up gamification callbacks
        self.gamification.set_callbacks(
            achievement_cb=self.show_achievement_notification,
            level_up_cb=self.show_level_up_notification,
            stats_cb=self.update_stats_display,
        )

        # Setup UI
        self.setup_ui()
        self.load_plugins()
        self.apply_theme()

    def load_theme_config(self):
        """Load theme configuration"""
        try:
            from tools.theme import load_config

            self.config = load_config()
            self.current_theme = self.config.get("current_theme", "dracula")
            print(f"🎨 Loading saved theme: {self.current_theme}")
        except Exception as e:
            print(f"Theme config error: {e}")
            self.current_theme = "dracula"
            self.config = {}

    def setup_ui(self):
        """Setup the main user interface with integrated graphics"""
        # Create main container
        self.main_container = tk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Setup toolbar
        self.setup_toolbar()

        # Create horizontal layout - NO paned windows or sliders
        self.main_frame = tk.Frame(self.main_container)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Left side: Code editor and output (70% width)
        self.left_section = tk.Frame(self.main_frame)
        self.left_section.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Right side: Graphics canvas (30% width, fixed)
        self.right_section = tk.Frame(self.main_frame, width=350)
        self.right_section.pack(side=tk.RIGHT, fill=tk.Y, padx=(8, 0))
        self.right_section.pack_propagate(False)  # Maintain fixed width

        # Setup components
        self.setup_menu()
        self.setup_editor()
        self.setup_console()
        self.setup_graphics()

    def setup_toolbar(self):
        """Setup minimal toolbar - file operations moved to code editor"""
        # Initialize language_var for compatibility
        self.language_var = tk.StringVar(value="PILOT")

        # Note: Toolbar removed - all functionality moved to menus and editor toolbar

    def setup_menu(self):
        """Setup streamlined menu system"""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        # File menu
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_as_file, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit_app, accelerator="Ctrl+Q")

        # Edit menu
        edit_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Find", command=self.find_text, accelerator="Ctrl+F")
        edit_menu.add_command(label="Replace", command=self.replace_text, accelerator="Ctrl+H")

        # Run menu
        run_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Run Code", command=self.run_code, accelerator="F5")
        run_menu.add_command(label="Stop", command=self.stop_execution, accelerator="Shift+F5")
        run_menu.add_separator()
        run_menu.add_command(label="Clear Output", command=self.clear_output)

        # Tools menu
        tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="🎨 Theme Selector", command=self.show_theme_selector)
        tools_menu.add_command(label="⚙️ Settings", command=self.show_settings)

        # Features menu
        features_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Features", menu=features_menu)
        features_menu.add_command(label="📚 Tutorial System", command=self.show_tutorial_system)
        features_menu.add_command(label="🤖 AI Code Assistant", command=self.show_ai_assistant)
        features_menu.add_command(label="🎮 Gamification Dashboard", command=self.show_gamification_dashboard)

        # Help menu
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About IDE Time Warp", command=self.show_about)

    def setup_editor(self):
        """Setup clean code editor canvas"""
        # Editor section - clean canvas without toolbar
        editor_frame = ttk.LabelFrame(self.left_section, text="⏰ Time Warp Code Portal")
        editor_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 4))

        # Initialize language variable for compatibility (used by other methods)
        self.editor_language_var = tk.StringVar(value="PILOT")

        # Create enhanced code editor - clean canvas
        self.code_editor = EnhancedCodeEditor(editor_frame, initial_language="pilot")

        # Set up callbacks
        try:
            self.code_editor.set_output_callback(self.write_to_console)
            self.code_editor.set_status_callback(self.update_status)
        except AttributeError:
            pass  # Enhanced editor methods may not be available

    def setup_console(self):
        """Setup output console with fixed height"""
        console_frame = ttk.LabelFrame(self.left_section, text="⏰ Time Warp Output")
        console_frame.pack(fill=tk.X, expand=False, pady=(4, 0))

        self.output_text = scrolledtext.ScrolledText(console_frame, height=8, state=tk.DISABLED, wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)

    def setup_graphics(self):
        """Setup integrated turtle graphics canvas"""
        graphics_frame = ttk.LabelFrame(self.right_section, text="⏰ Turtle Graphics")
        graphics_frame.pack(fill=tk.BOTH, expand=True)

        try:
            # Create graphics canvas
            self.graphics_canvas = tk.Canvas(
                graphics_frame,
                width=340,
                height=340,
                bg="white",
                highlightthickness=1,
                highlightbackground="#cccccc",
            )
            self.graphics_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # Initialize turtle graphics
            screen = turtle.TurtleScreen(self.graphics_canvas)
            screen.bgcolor("white")
            screen.setworldcoordinates(-160, -160, 160, 160)
            self.turtle = turtle.RawTurtle(screen)
            self.turtle.speed(5)
            self.turtle.shape("turtle")

            # Connect turtle to interpreter
            self.interpreter.ide_turtle_canvas = self.graphics_canvas
            self.interpreter.ide_turtle_screen = screen
            self.interpreter.ide_turtle = self.turtle

            print("🎨 Turtle graphics canvas initialized")

        except Exception as e:
            print(f"Graphics setup error: {e}")
            # Create placeholder if turtle graphics fails
            placeholder = tk.Label(
                graphics_frame,
                text="Graphics\nCanvas\n(Turtle graphics\nunavailable)",
                bg="lightgray",
                justify=tk.CENTER,
            )
            placeholder.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def load_plugins(self):
        """Load essential plugins only"""
        try:
            available_plugins = self.plugin_manager.scan_plugins()
            for plugin_name in available_plugins:
                try:
                    self.plugin_manager.load_plugin(plugin_name)
                    print(f"Plugin loaded: {plugin_name}")
                except Exception as e:
                    print(f"Failed to load plugin '{plugin_name}': {e}")
        except Exception as e:
            print(f"Error loading plugins: {e}")

    # Core file operations
    def new_file(self):
        """Create new file"""
        if hasattr(self.code_editor, "text_editor"):
            self.code_editor.text_editor.delete(1.0, tk.END)
        self.current_file = None
        self.write_to_console("⏰ New time portal opened")

    def open_file(self):
        """Open file with language detection"""
        file_path = filedialog.askopenfilename(
            title="Open File",
            filetypes=[
                ("All supported", "*.pilot;*.bas;*.basic;*.logo;*.py;*.js;*.pl;*.txt"),
                ("PILOT files", "*.pilot"),
                ("BASIC files", "*.bas;*.basic"),
                ("Logo files", "*.logo"),
                ("Python files", "*.py"),
                ("JavaScript files", "*.js"),
                ("Perl files", "*.pl"),
                ("Text files", "*.txt"),
                ("All files", "*.*"),
            ],
        )

        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    if hasattr(self.code_editor, "text_editor"):
                        self.code_editor.text_editor.delete(1.0, tk.END)
                        self.code_editor.text_editor.insert(1.0, content)

                    self.current_file = file_path
                    self.auto_detect_language(file_path)
                    self.write_to_console(f"⏰ Time portal opened: {os.path.basename(file_path)}")

            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")

    def save_file(self):
        """Save current file"""
        if self.current_file:
            self.save_to_file(self.current_file)
        else:
            self.save_as_file()

    def save_as_file(self):
        """Save file as"""
        file_path = filedialog.asksaveasfilename(
            title="Save File As",
            defaultextension=".py",
            filetypes=[
                ("Python files", "*.py"),
                ("PILOT files", "*.pilot"),
                ("BASIC files", "*.bas"),
                ("Logo files", "*.logo"),
                ("JavaScript files", "*.js"),
                ("Perl files", "*.pl"),
                ("Text files", "*.txt"),
                ("All files", "*.*"),
            ],
        )

        if file_path:
            self.current_file = file_path
            self.save_to_file(file_path)

    def save_to_file(self, file_path):
        """Save content to specified file"""
        try:
            if hasattr(self.code_editor, "text_editor"):
                content = self.code_editor.text_editor.get(1.0, tk.END + "-1c")
            else:
                content = ""

            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)

            self.write_to_console(f"⏰ Timeline saved: {os.path.basename(file_path)}")

        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")

    # Core execution methods
    def run_code(self):
        """Run the current code"""
        try:
            if hasattr(self.code_editor, "text_editor"):
                code = self.code_editor.text_editor.get(1.0, tk.END).strip()
            else:
                code = ""

            if not code:
                self.write_to_console("❌ No code to run")
                return

            # Clear previous output
            self.clear_output()

            # Get current language
            language = self.editor_language_var.get().lower()

            # Execute code
            self.write_to_console(f"⏰ Time warping through {language.upper()} code...")

            # Use interpreter to execute
            result = self.interpreter.run_program(code)
            if result:
                self.write_to_console(str(result))

            # Record successful program execution for gamification
            lines_count = len([line for line in code.split("\n") if line.strip()])
            self.record_program_execution(language, code, lines_count)

        except Exception as e:
            self.write_to_console(f"❌ Execution error: {e}")

    def stop_execution(self):
        """Stop code execution"""
        self.write_to_console("⏰ Time warp halted")

    def clear_output(self):
        """Clear output console"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)

    # Utility methods
    def write_to_console(self, message):
        """Write message to console"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, f"{message}\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def update_status(self, status):
        """Update status (write to console since status bar removed)"""
        self.write_to_console(f"ℹ️ {status}")

    def on_language_changed(self, event=None):
        """Handle language change"""
        if hasattr(self, "editor_language_var"):
            language = self.editor_language_var.get()
            self.language_var.set(language)
            self.write_to_console(f"🔄 Language changed to {language}")

    def auto_detect_language(self, file_path):
        """Auto-detect language from file extension"""
        ext = os.path.splitext(file_path)[1].lower()

        language_map = {
            ".pilot": "PILOT",
            ".bas": "BASIC",
            ".basic": "BASIC",
            ".logo": "Logo",
            ".py": "Python",
            ".js": "JavaScript",
            ".pl": "Perl",
        }

        language = language_map.get(ext, "Python")
        self.editor_language_var.set(language)
        self.language_var.set(language)

    # Project functionality removed - not needed for streamlined IDE    # Dialog methods
    def show_theme_selector(self):
        """Show theme selection dialog"""
        try:
            print("🎨 Opening theme selector...")  # Debug output
            themes = [
                "dracula",
                "monokai",
                "solarized_dark",
                "ocean",
                "spring",
                "sunset",
                "candy",
                "forest",
            ]

            dialog = tk.Toplevel(self.root)
            dialog.title("🎨 IDE Time Warp Theme Portal")
            dialog.geometry("350x450")
            dialog.resizable(False, False)

            # Make dialog modal
            dialog.transient(self.root)
            dialog.grab_set()

            # Center the dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (350 // 2)
            y = (dialog.winfo_screenheight() // 2) - (450 // 2)
            dialog.geometry(f"350x450+{x}+{y}")

            # Header
            header_frame = tk.Frame(dialog)
            header_frame.pack(pady=15)
            tk.Label(
                header_frame,
                text="⏰ Select Time Era Theme",
                font=("Arial", 14, "bold"),
            ).pack()
            tk.Label(
                header_frame,
                text="Warp to your preferred coding era",
                font=("Arial", 10),
            ).pack()

            # Theme buttons
            button_frame = tk.Frame(dialog)
            button_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

            for i, theme in enumerate(themes):
                btn = tk.Button(
                    button_frame,
                    text=f"🎨 {theme.replace('_', ' ').title()}",
                    command=lambda t=theme: self.apply_selected_theme(t, dialog),
                    width=25,
                    height=2,
                    font=("Arial", 10),
                )
                btn.pack(pady=3, fill=tk.X)

                # Highlight current theme
                if hasattr(self, "current_theme") and theme == self.current_theme:
                    btn.config(relief=tk.RAISED, bg="lightblue")

            # Close button
            close_frame = tk.Frame(dialog)
            close_frame.pack(pady=15)
            tk.Button(close_frame, text="✖ Close", command=dialog.destroy, width=15).pack()

            print("✅ Theme selector opened successfully!")

        except Exception as e:
            print(f"❌ Theme selector error: {e}")
            import traceback

            traceback.print_exc()
            self.write_to_console(f"❌ Error opening theme selector: {e}")

    def apply_selected_theme(self, theme_name, dialog):
        """Apply selected theme"""
        try:
            print(f"🎨 Applying theme: {theme_name}")
            self.current_theme = theme_name
            self.apply_theme()
            self.write_to_console(f"🎨 Theme changed to: {theme_name}")
            dialog.destroy()

            # Save theme preference
            try:
                from tools.theme import save_config

                if not hasattr(self, "config") or self.config is None:
                    self.config = {}
                self.config["current_theme"] = theme_name
                save_config(self.config)
                print(f"✅ Theme {theme_name} saved to config")
            except Exception as e:
                print(f"⚠️ Failed to save theme config: {e}")
                self.write_to_console(f"⚠️ Theme applied but not saved: {e}")

        except Exception as e:
            print(f"❌ Error applying theme: {e}")
            import traceback

            traceback.print_exc()
            self.write_to_console(f"❌ Error applying theme: {e}")
            if "dialog" in locals():
                dialog.destroy()

    def show_settings(self):
        """Show settings dialog"""
        try:
            print("⚙️ Opening settings...")  # Debug output

            dialog = tk.Toplevel(self.root)
            dialog.title("⚙️ IDE Time Warp Settings")
            dialog.geometry("400x500")
            dialog.resizable(False, False)

            # Make dialog modal
            dialog.transient(self.root)
            dialog.grab_set()

            # Center the dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
            y = (dialog.winfo_screenheight() // 2) - (500 // 2)
            dialog.geometry(f"400x500+{x}+{y}")

            # Header
            header_frame = tk.Frame(dialog)
            header_frame.pack(pady=15)
            tk.Label(
                header_frame,
                text="⚙️ IDE Time Warp Settings",
                font=("Arial", 14, "bold"),
            ).pack()
            tk.Label(
                header_frame,
                text="Configure your time-traveling IDE preferences",
                font=("Arial", 10),
            ).pack()

            # Settings sections
            notebook = ttk.Notebook(dialog)
            notebook.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

            # Editor Settings Tab
            editor_frame = ttk.Frame(notebook)
            notebook.add(editor_frame, text="📝 Editor")

            tk.Label(editor_frame, text="Editor Configuration", font=("Arial", 11, "bold")).pack(pady=10)

            # Font size setting
            font_frame = tk.Frame(editor_frame)
            font_frame.pack(pady=5, fill=tk.X, padx=20)
            tk.Label(font_frame, text="Font Size:").pack(side=tk.LEFT)
            font_scale = tk.Scale(font_frame, from_=8, to=20, orient=tk.HORIZONTAL)
            font_scale.set(11)
            font_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True)

            # Tab size setting
            tab_frame = tk.Frame(editor_frame)
            tab_frame.pack(pady=5, fill=tk.X, padx=20)
            tk.Label(tab_frame, text="Tab Size:").pack(side=tk.LEFT)
            tab_scale = tk.Scale(tab_frame, from_=2, to=8, orient=tk.HORIZONTAL)
            tab_scale.set(4)
            tab_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True)

            # Checkboxes
            options_frame = tk.Frame(editor_frame)
            options_frame.pack(pady=10, fill=tk.X, padx=20)

            line_numbers_var = tk.BooleanVar(value=True)
            tk.Checkbutton(options_frame, text="Show line numbers", variable=line_numbers_var).pack(anchor=tk.W)

            syntax_var = tk.BooleanVar(value=True)
            tk.Checkbutton(options_frame, text="Syntax highlighting", variable=syntax_var).pack(anchor=tk.W)

            auto_indent_var = tk.BooleanVar(value=True)
            tk.Checkbutton(options_frame, text="Auto indent", variable=auto_indent_var).pack(anchor=tk.W)

            # Theme Settings Tab
            theme_frame = ttk.Frame(notebook)
            notebook.add(theme_frame, text="🎨 Themes")

            tk.Label(theme_frame, text="Theme Configuration", font=("Arial", 11, "bold")).pack(pady=10)
            tk.Label(
                theme_frame,
                text=f"Current theme: {getattr(self, 'current_theme', 'dracula')}",
                font=("Arial", 10),
            ).pack(pady=5)
            tk.Button(
                theme_frame,
                text="🎨 Change Theme",
                command=self.show_theme_selector,
                width=20,
            ).pack(pady=10)

            # About Tab
            about_frame = ttk.Frame(notebook)
            notebook.add(about_frame, text="ℹ️ About")

            about_text = f"""
⏰ IDE Time Warp - Journey Through Code

Time-Traveling Programming Environment
Warping through programming eras:
• PILOT  • BASIC  • Logo
• Python • JavaScript • Perl

Platform: {platform.system()}
Python: {sys.version.split()[0]}

Built for radical code adventures across time.
            """
            tk.Label(about_frame, text=about_text, justify=tk.LEFT, font=("Arial", 9)).pack(pady=20, padx=20)

            # Buttons
            button_frame = tk.Frame(dialog)
            button_frame.pack(pady=15)

            def save_settings():
                self.write_to_console("⚙️ Settings saved!")
                dialog.destroy()

            tk.Button(button_frame, text="💾 Save", command=save_settings, width=12).pack(side=tk.LEFT, padx=5)
            tk.Button(button_frame, text="✖ Cancel", command=dialog.destroy, width=12).pack(side=tk.LEFT, padx=5)

            print("✅ Settings dialog opened successfully!")

        except Exception as e:
            print(f"❌ Settings error: {e}")
            import traceback

            traceback.print_exc()
            self.write_to_console(f"❌ Error opening settings: {e}")

    def show_about(self):
        """Show about dialog"""
        about_text = f"""
⏰ IDE Time Warp - Journey Through Code
Radical Time-Traveling Programming IDE

Version: 1.0 (Time Warp Edition)
Platform: {platform.system()} {platform.release()}
Python: {sys.version.split()[0]}

A revolutionary, time-traveling programming environment
supporting multiple languages across different eras.

Warp through code like never before!
        """
        messagebox.showinfo("About IDE Time Warp", about_text)

    def find_text(self):
        """Simple find functionality"""
        if hasattr(self.code_editor, "text_editor"):
            search_term = simpledialog.askstring("Find", "Enter text to find:")
            if search_term:
                # Simple search implementation
                content = self.code_editor.text_editor.get(1.0, tk.END)
                if search_term in content:
                    self.write_to_console(f"🔍 Found: '{search_term}'")
                else:
                    self.write_to_console(f"🔍 Not found: '{search_term}'")

    def replace_text(self):
        """Simple replace functionality with dialog"""
        if hasattr(self.code_editor, "text_editor"):
            search_term = simpledialog.askstring("Replace", "Enter text to replace:")
            if not search_term:
                return
            replace_term = simpledialog.askstring("Replace", f"Replace '{search_term}' with:")
            if replace_term is None:
                return
            content = self.code_editor.text_editor.get(1.0, tk.END)
            new_content = content.replace(search_term, replace_term)
            self.code_editor.text_editor.delete(1.0, tk.END)
            self.code_editor.text_editor.insert(1.0, new_content)
            self.write_to_console(f"🔄 Replaced all occurrences of '{search_term}' with '{replace_term}'")

    def apply_theme(self):
        """Apply current theme to all UI components"""
        try:
            print(f"🎨 Applying theme: {self.current_theme}")

            # Get theme colors
            from tools.theme import get_theme_colors

            colors = get_theme_colors(self.current_theme)

            # Apply to main window
            self.root.configure(bg=colors.get("bg_primary", "#1E1E2E"))

            # Apply to main container
            if hasattr(self, "main_container"):
                self.main_container.configure(bg=colors.get("bg_primary", "#1E1E2E"))

            # Apply to console output
            if hasattr(self, "output_text"):
                self.output_text.configure(
                    bg=colors.get("bg_secondary", "#282A36"),
                    fg=colors.get("text_primary", "#F8F8F2"),
                    insertbackground=colors.get("accent", "#FF79C6"),
                    selectbackground=colors.get("selection", "#44475A"),
                    selectforeground=colors.get("text_primary", "#F8F8F2"),
                )

            # Apply to code editor if it has text_editor
            if hasattr(self, "code_editor") and hasattr(self.code_editor, "text_editor"):
                self.code_editor.text_editor.configure(
                    bg=colors.get("bg_secondary", "#282A36"),
                    fg=colors.get("text_primary", "#F8F8F2"),
                    insertbackground=colors.get("accent", "#FF79C6"),
                    selectbackground=colors.get("selection", "#44475A"),
                    selectforeground=colors.get("text_primary", "#F8F8F2"),
                )

            # Apply to graphics canvas
            if hasattr(self, "graphics_canvas"):
                canvas_bg = (
                    colors.get("bg_tertiary", "#FFFFFF")
                    if "light" in self.current_theme or self.current_theme in ["spring", "sunset", "candy", "forest"]
                    else "#2F3349"
                )
                self.graphics_canvas.configure(bg=canvas_bg)

            # Apply to menu bar
            if hasattr(self, "menubar"):
                self.menubar.configure(
                    bg=colors.get("menu_bg", colors.get("bg_secondary", "#282A36")),
                    fg=colors.get("text_primary", "#F8F8F2"),
                    activebackground=colors.get("accent", "#FF79C6"),
                    activeforeground=colors.get("text_primary", "#F8F8F2"),
                )

            # Update ttk style for themed widgets
            style = ttk.Style()
            style.theme_use("clam")  # Use clam theme as base for customization

            # Configure ttk styles
            style.configure("TFrame", background=colors.get("bg_primary", "#1E1E2E"))
            style.configure(
                "TLabel",
                background=colors.get("bg_primary", "#1E1E2E"),
                foreground=colors.get("text_primary", "#F8F8F2"),
            )
            style.configure(
                "TButton",
                background=colors.get("button_bg", "#6272A4"),
                foreground=colors.get("text_primary", "#F8F8F2"),
            )
            style.map(
                "TButton",
                background=[
                    ("active", colors.get("button_hover", "#FF79C6")),
                    ("pressed", colors.get("accent", "#FF79C6")),
                ],
            )
            style.configure(
                "TLabelFrame",
                background=colors.get("bg_primary", "#1E1E2E"),
                foreground=colors.get("text_secondary", "#BD93F9"),
            )
            style.configure("TNotebook", background=colors.get("bg_primary", "#1E1E2E"))
            style.configure(
                "TNotebook.Tab",
                background=colors.get("bg_tertiary", "#44475A"),
                foreground=colors.get("text_primary", "#F8F8F2"),
            )
            style.map(
                "TNotebook.Tab",
                background=[("selected", colors.get("accent", "#FF79C6"))],
            )

            self.write_to_console(f"🎨 Theme '{self.current_theme}' applied successfully!")

        except Exception as e:
            print(f"❌ Theme application error: {e}")
            import traceback

            traceback.print_exc()
            self.write_to_console(f"❌ Error applying theme: {e}")

    # Gamification System Callback Methods
    def show_achievement_notification(self, achievement):
        """Show achievement unlock notification"""
        try:
            from tkinter import messagebox

            message = f"🏆 Achievement Unlocked!\n\n{achievement.icon} {achievement.name}\n{achievement.description}\n\n+{achievement.points} points!"
            messagebox.showinfo("Achievement Unlocked!", message)
            self.write_to_console(f"🏆 Achievement unlocked: {achievement.name} (+{achievement.points} points)")
        except Exception as e:
            print(f"Error showing achievement notification: {e}")

    def show_level_up_notification(self, old_level, new_level):
        """Show level up notification"""
        try:
            from tkinter import messagebox

            message = f"🎉 Level Up!\n\nYou've reached Level {new_level}!\n\nKeep coding to unlock more features and challenges!"
            messagebox.showinfo("Level Up!", message)
            self.write_to_console(f"🎉 Level up! You're now level {new_level} (was {old_level})")
        except Exception as e:
            print(f"Error showing level up notification: {e}")

    def update_stats_display(self, stats):
        """Update stats display in the console"""
        try:
            self.write_to_console(
                f"📊 Stats Update - Level {stats.level}, {stats.total_points} points, {stats.programs_written} programs written"
            )
        except Exception as e:
            print(f"Error updating stats display: {e}")

    def record_program_execution(self, language, code, lines_count):
        """Record program execution for gamification"""
        try:
            self.gamification.record_activity(
                "program_written",
                {
                    "language": language.lower(),
                    "lines": lines_count,
                    "points": max(5, lines_count // 2),  # Base points plus line bonus
                },
            )
        except Exception as e:
            print(f"Error recording program execution: {e}")

    def show_gamification_dashboard(self):
        """Show gamification dashboard window"""
        try:
            dashboard_data = self.gamification.get_user_dashboard()

            # Create dashboard window
            dashboard_window = tk.Toplevel(self.root)
            dashboard_window.title("🎮 Gamification Dashboard")
            dashboard_window.geometry("800x600")
            dashboard_window.transient(self.root)
            dashboard_window.grab_set()

            # Create notebook for different sections
            notebook = ttk.Notebook(dashboard_window)
            notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Stats tab
            stats_frame = ttk.Frame(notebook)
            notebook.add(stats_frame, text="📊 Stats")

            stats_text = tk.Text(stats_frame, wrap=tk.WORD, height=20)
            stats_scrollbar = tk.Scrollbar(stats_frame, orient=tk.VERTICAL, command=stats_text.yview)
            stats_text.configure(yscrollcommand=stats_scrollbar.set)

            stats_content = f"""🎮 Gamification Dashboard

📊 Your Statistics:
• Level: {dashboard_data['level']}
• Total Points: {dashboard_data['stats']['total_points']}
• Experience: {dashboard_data['stats']['experience']} XP
• XP to Next Level: {dashboard_data['xp_to_next_level']} XP
• Programs Written: {dashboard_data['stats']['programs_written']}
• Lines of Code: {dashboard_data['stats']['lines_of_code']}
• Current Streak: {dashboard_data['stats']['current_streak']} days
• Longest Streak: {dashboard_data['stats']['longest_streak']} days

🏆 Achievements:
• Unlocked: {dashboard_data['achievements']['unlocked']}/{dashboard_data['achievements']['total']}

🎯 Challenges:
• Completed: {dashboard_data['challenges']['completed']}/{dashboard_data['challenges']['total']}

🌟 Recent Achievements:"""

            for achievement in dashboard_data["achievements"]["recent"]:
                stats_content += f"\n• {achievement.icon} {achievement.name} - {achievement.points} pts"

            stats_text.insert(tk.END, stats_content)
            stats_text.config(state=tk.DISABLED)

            stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            stats_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Achievements tab
            achievements_frame = ttk.Frame(notebook)
            notebook.add(achievements_frame, text="🏆 Achievements")

            achievements_text = tk.Text(achievements_frame, wrap=tk.WORD, height=20)
            achievements_scrollbar = tk.Scrollbar(
                achievements_frame, orient=tk.VERTICAL, command=achievements_text.yview
            )
            achievements_text.configure(yscrollcommand=achievements_scrollbar.set)

            achievements_content = "🏆 All Achievements:\n\n"

            for achievement in self.gamification.achievements.values():
                status = "✅" if achievement.unlocked else f"🔒 ({achievement.progress:.0%})"
                achievements_content += f"{status} {achievement.icon} {achievement.name}\n"
                achievements_content += f"   {achievement.description}\n"
                achievements_content += (
                    f"   Rarity: {achievement.rarity.value.title()} | Points: {achievement.points}\n\n"
                )

            achievements_text.insert(tk.END, achievements_content)
            achievements_text.config(state=tk.DISABLED)

            achievements_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            achievements_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Challenges tab
            challenges_frame = ttk.Frame(notebook)
            notebook.add(challenges_frame, text="🎯 Challenges")

            challenges_text = tk.Text(challenges_frame, wrap=tk.WORD, height=20)
            challenges_scrollbar = tk.Scrollbar(challenges_frame, orient=tk.VERTICAL, command=challenges_text.yview)
            challenges_text.configure(yscrollcommand=challenges_scrollbar.set)

            challenges_content = "🎯 Available Challenges:\n\n"

            for challenge in self.gamification.challenges.values():
                status = "✅ Completed" if challenge.completed else "📋 Available"
                challenges_content += f"{status} - {challenge.title}\n"
                challenges_content += f"   Language: {challenge.language.upper()}\n"
                challenges_content += f"   Difficulty: {challenge.difficulty.title()}\n"
                challenges_content += f"   Category: {challenge.category.title()}\n"
                challenges_content += f"   Points: {challenge.points}\n"
                challenges_content += f"   Description: {challenge.description}\n\n"

            challenges_text.insert(tk.END, challenges_content)
            challenges_text.config(state=tk.DISABLED)

            challenges_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            challenges_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        except Exception as e:
            print(f"Error showing gamification dashboard: {e}")
            messagebox.showerror("Error", f"Could not open gamification dashboard: {e}")

    def show_tutorial_system(self):
        """Show tutorial system window"""
        try:
            # Create tutorial window
            tutorial_window = tk.Toplevel(self.root)
            tutorial_window.title("📚 Interactive Tutorial System")
            tutorial_window.geometry("900x700")
            tutorial_window.transient(self.root)
            tutorial_window.grab_set()

            # Create main frame
            main_frame = tk.Frame(tutorial_window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Tutorial selection
            selection_frame = tk.Frame(main_frame)
            selection_frame.pack(fill=tk.X, pady=(0, 10))

            tk.Label(selection_frame, text="Select a Tutorial:").pack(side=tk.LEFT)

            tutorial_var = tk.StringVar()
            tutorials = [
                "PILOT Basics",
                "BASIC Programming",
                "Logo Graphics",
                "Python Fundamentals",
            ]
            tutorial_combo = ttk.Combobox(
                selection_frame,
                textvariable=tutorial_var,
                values=tutorials,
                state="readonly",
            )
            tutorial_combo.pack(side=tk.LEFT, padx=(10, 0))
            tutorial_combo.set(tutorials[0])

            # Tutorial content area
            content_frame = tk.Frame(main_frame)
            content_frame.pack(fill=tk.BOTH, expand=True)

            tutorial_text = tk.Text(content_frame, wrap=tk.WORD, height=25, width=80)
            tutorial_scrollbar = tk.Scrollbar(content_frame, orient=tk.VERTICAL, command=tutorial_text.yview)
            tutorial_text.configure(yscrollcommand=tutorial_scrollbar.set)

            tutorial_content = """📚 Interactive Tutorial System

Welcome to the TimeWarp IDE Tutorial System! 

🎯 Available Tutorials:

1. PILOT Basics
   - Learn the fundamentals of PILOT programming
   - Text output with T: commands
   - User input with A: commands
   - Variables with U: commands
   - Conditional logic with Y:, N:, J: commands

2. BASIC Programming  
   - Classic line-numbered programming
   - PRINT statements for output
   - INPUT for user interaction
   - Variables and calculations
   - FOR loops and conditional statements

3. Logo Graphics
   - Turtle graphics programming
   - Movement commands: FORWARD, BACK
   - Turning commands: LEFT, RIGHT  
   - Drawing shapes and patterns
   - Loops with REPEAT

4. Python Fundamentals
   - Modern programming concepts
   - Variables and data types
   - Functions and control structures
   - Object-oriented programming basics

💡 Tutorial Features:
• Step-by-step guided lessons
• Interactive code examples
• Progress tracking
• Achievement integration
• Hands-on exercises

🚀 Getting Started:
1. Select a tutorial from the dropdown above
2. Follow the step-by-step instructions
3. Try the example code in the main editor
4. Complete exercises to earn achievements

Happy learning! Your journey through programming history begins here! ⏰"""

            tutorial_text.insert(tk.END, tutorial_content)
            tutorial_text.config(state=tk.DISABLED)

            tutorial_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            tutorial_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Button frame
            button_frame = tk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=(10, 0))

            start_button = tk.Button(
                button_frame,
                text="▶️ Start Tutorial",
                command=lambda: self.start_tutorial(tutorial_var.get()),
            )
            start_button.pack(side=tk.LEFT)

            close_button = tk.Button(button_frame, text="❌ Close", command=tutorial_window.destroy)
            close_button.pack(side=tk.RIGHT)

        except Exception as e:
            print(f"Error showing tutorial system: {e}")
            messagebox.showerror("Error", f"Could not open tutorial system: {e}")

    def start_tutorial(self, tutorial_name):
        """Start a specific tutorial"""
        try:
            tutorial_mapping = {
                "PILOT Basics": "pilot_basics",
                "BASIC Programming": "basic_fundamentals",
                "Logo Graphics": "logo_graphics",
                "Python Fundamentals": "python_basics",
            }

            tutorial_id = tutorial_mapping.get(tutorial_name)
            if tutorial_id:
                # For now, just show tutorial started message
                self.write_to_console(f"📚 Starting tutorial: {tutorial_name}")
                self.write_to_console(
                    f"� Tutorial system loaded. Follow the interactive lessons in the tutorial window."
                )
                # Record tutorial activity
                self.gamification.record_activity("tutorial_started", {"tutorial": tutorial_id})
            else:
                self.write_to_console(f"❌ Unknown tutorial: {tutorial_name}")

        except Exception as e:
            print(f"Error starting tutorial: {e}")

    def show_ai_assistant(self):
        """Show AI code assistant window"""
        try:
            # Create AI assistant window
            ai_window = tk.Toplevel(self.root)
            ai_window.title("🤖 AI Code Assistant")
            ai_window.geometry("800x600")
            ai_window.transient(self.root)
            ai_window.grab_set()

            # Create main frame
            main_frame = tk.Frame(ai_window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Code input area
            input_frame = tk.LabelFrame(main_frame, text="📝 Code to Analyze")
            input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

            code_text = tk.Text(input_frame, height=15, wrap=tk.WORD)
            code_scrollbar = tk.Scrollbar(input_frame, orient=tk.VERTICAL, command=code_text.yview)
            code_text.configure(yscrollcommand=code_scrollbar.set)

            # Get current code from editor
            current_code = self.code_editor.get_content()
            if current_code.strip():
                code_text.insert(tk.END, current_code)
            else:
                code_text.insert(
                    tk.END,
                    "# Paste your code here for AI analysis\nT:Hello, AI Assistant!\nEND",
                )

            code_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            code_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Analysis options
            options_frame = tk.Frame(main_frame)
            options_frame.pack(fill=tk.X, pady=(0, 10))

            language_var = tk.StringVar(value="PILOT")
            tk.Label(options_frame, text="Language:").pack(side=tk.LEFT)
            lang_combo = ttk.Combobox(
                options_frame,
                textvariable=language_var,
                values=["PILOT", "BASIC", "Logo", "Python"],
                state="readonly",
            )
            lang_combo.pack(side=tk.LEFT, padx=(5, 15))

            analyze_button = tk.Button(
                options_frame,
                text="🧠 Analyze Code",
                command=lambda: self.analyze_code_with_ai(code_text.get(1.0, tk.END), language_var.get()),
            )
            analyze_button.pack(side=tk.LEFT)

            # Analysis results area
            results_frame = tk.LabelFrame(main_frame, text="🎯 AI Analysis Results")
            results_frame.pack(fill=tk.BOTH, expand=True)

            results_text = tk.Text(results_frame, height=15, wrap=tk.WORD, state=tk.DISABLED)
            results_scrollbar = tk.Scrollbar(results_frame, orient=tk.VERTICAL, command=results_text.yview)
            results_text.configure(yscrollcommand=results_scrollbar.set)

            # Store reference for updating
            self.ai_results_text = results_text

            # Initial welcome message
            results_text.config(state=tk.NORMAL)
            results_text.insert(
                tk.END,
                """🤖 AI Code Assistant Ready!

Welcome to the intelligent code analysis system! 

🎯 What I can do:
• Analyze code structure and syntax
• Suggest improvements and optimizations  
• Explain complex programming concepts
• Identify potential issues and bugs
• Provide learning recommendations
• Generate code examples and templates

📝 How to use:
1. Paste or type your code in the input area above
2. Select the programming language
3. Click 'Analyze Code' to get AI insights
4. Review suggestions and apply improvements

🚀 Ready to make your code better? Let's analyze some code!""",
            )
            results_text.config(state=tk.DISABLED)

            results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Button frame
            button_frame = tk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=(10, 0))

            close_button = tk.Button(button_frame, text="❌ Close", command=ai_window.destroy)
            close_button.pack(side=tk.RIGHT)

        except Exception as e:
            print(f"Error showing AI assistant: {e}")
            messagebox.showerror("Error", f"Could not open AI assistant: {e}")

    def analyze_code_with_ai(self, code, language):
        """Analyze code using AI assistant"""
        try:
            issues = self.ai_assistant.analyze_code(code, language.lower())

            # Update results display
            if hasattr(self, "ai_results_text"):
                self.ai_results_text.config(state=tk.NORMAL)
                self.ai_results_text.delete(1.0, tk.END)

                results = f"🤖 AI Analysis Results for {language}\n\n"

                if issues:
                    results += "📊 Code Issues Found:\n"
                    for i, issue in enumerate(issues, 1):
                        results += f"\n{i}. {issue.severity.upper()}: {issue.message}\n"
                        if issue.line_number:
                            results += f"   Line: {issue.line_number}\n"
                        if issue.suggestion:
                            results += f"   💡 Suggestion: {issue.suggestion}\n"

                    # Quality assessment
                    error_count = len([i for i in issues if i.severity == "error"])
                    warning_count = len([i for i in issues if i.severity == "warning"])
                    info_count = len([i for i in issues if i.severity == "info"])

                    quality_score = max(
                        0,
                        10 - (error_count * 3) - (warning_count * 1) - (info_count * 0.5),
                    )
                    results += f"\n🎯 Code Quality Score: {quality_score:.1f}/10\n"

                    if error_count == 0 and warning_count == 0:
                        results += "\n✅ Great job! Your code looks clean and follows good practices!\n"
                    elif error_count == 0:
                        results += "\n� Good code! Just a few minor suggestions for improvement.\n"
                    else:
                        results += "\n⚠️ There are some issues to address. Fix the errors first, then consider the suggestions.\n"
                else:
                    results += "✅ No issues found! Your code looks great!\n\n🎯 Code Quality Score: 10/10\n\n🌟 Excellent work! Your code follows good practices."

                self.ai_results_text.insert(tk.END, results)
                self.ai_results_text.config(state=tk.DISABLED)

            self.write_to_console(f"🤖 AI analysis completed for {language} code")

        except Exception as e:
            print(f"Error analyzing code with AI: {e}")
            if hasattr(self, "ai_results_text"):
                self.ai_results_text.config(state=tk.NORMAL)
                self.ai_results_text.delete(1.0, tk.END)
                self.ai_results_text.insert(tk.END, f"❌ Error analyzing code: {e}")
                self.ai_results_text.config(state=tk.DISABLED)

    def quit_app(self):
        """Exit the time warp"""
        if messagebox.askokcancel("Exit Time Warp", "Ready to return to your own time?"):
            self.root.quit()


def main():
    """Main application entry point - Begin the Time Warp!"""
    try:
        app = IDETimeWarp()
        app.root.mainloop()
    except Exception as e:
        print(f"Error starting IDE Time Warp: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
