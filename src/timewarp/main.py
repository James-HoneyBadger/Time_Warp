#!/usr/bin/env python3
"""
Time_Warp IDE - Enhanced Multi-Tab Editor
Updated main application with new features:
- Multi-tab code editor
- File explorer panel
- Enhanced graphics canvas
- Better error handling
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

# Import theme configuration functions
from .utils.theme import (
    load_config,
    save_config,
    ThemeManager,
    available_themes,
    get_theme_preview,
    get_config_file,
)

# Import core components
try:
    from .core.interpreter import Time_WarpInterpreter

    CORE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Core components not available: {e}")
    CORE_AVAILABLE = False

# Import plugins (from root level)
try:
    import sys
    import os

    # Add root directory to path for plugins
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)
    from plugins import PluginManager

    PLUGINS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Plugin system not available: {e}")
    PLUGINS_AVAILABLE = False

# Import GUI components
try:
    from .gui.components.multi_tab_editor import MultiTabEditor
    from .gui.components.enhanced_graphics_canvas import EnhancedGraphicsCanvas

    ENHANCED_GRAPHICS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Enhanced components not available: {e}")
    ENHANCED_GRAPHICS_AVAILABLE = False

# Error handling and feature modules
try:
    from .core.enhanced_error_handler import EnhancedErrorHandler, ErrorHighlighter
    from .core.features.tutorial_system import TutorialSystem
    from .core.features.ai_assistant import AICodeAssistant
    from .core.features.gamification import GamificationSystem

    FEATURES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Feature modules not available: {e}")
    FEATURES_AVAILABLE = False


class Time_WarpIDE:
    """
    Time_Warp IDE - Enhanced Educational Programming Environment
    New features: Multi-tab editor, File explorer, Enhanced graphics, Better errors
    """

    def __init__(self):
        """Initialize Time_Warp IDE"""
        print("🚀 Starting Time_Warp IDE 1.2...")
        print("⏰ Enhanced Educational Programming Environment")
        print("🔥 New: Multi-tab editor, Enhanced graphics, Theme selector!")

        # Initialize main window
        self.root = tk.Tk()
        self._setup_window()

        # Hide window during initialization to prevent theme flash
        self.root.withdraw()

        # Initialize core systems
        self.theme_manager = ThemeManager()
        self.current_theme = "forest"  # Default theme

        # Initialize plugin manager if available
        if PLUGINS_AVAILABLE:
            self.plugin_manager = PluginManager(self)
        else:
            self.plugin_manager = None

        # Initialize interpreter
        self.interpreter = Time_WarpInterpreter()

        # Initialize execution tracking
        self.execution_thread = None
        self.stop_execution_flag = False

        # Setup UI
        self.setup_ui()

        # Initialize other components
        self.load_theme_config()

        # Apply any saved settings (editor fonts, line numbers, etc.)
        try:
            self.apply_saved_settings()
        except Exception:
            pass

        # Setup keyboard shortcuts
        self.setup_keyboard_shortcuts()

        # Initialize features
        self.init_features()

        # Apply initial theme (after all UI components are created)
        self.apply_theme()

        # Show window now that theme is applied
        self.root.deiconify()

        # Ensure theme is applied to multi-tab editor specifically
        if hasattr(self, "multi_tab_editor"):
            try:
                colors = self.theme_manager.get_colors()
                self.multi_tab_editor.apply_theme(colors)
                print("✅ Initial theme applied to multi-tab editor")
            except Exception as e:
                print(f"⚠️ Failed to apply initial theme to editor: {e}")

        # Load plugins
        self.load_plugins()

        print("🚀 Time_Warp IDE 1.2 - Clean two-panel layout ready!")

        # Handle any initialization errors gracefully

    def load_theme_config(self):
        """Load theme configuration"""
        try:
            cfg = getattr(self.theme_manager, "config", {}) or {}
            self.current_theme = cfg.get("current_theme", "forest")
            print(f"🎨 Loaded theme: {self.current_theme}")
            # Log config path and key values for debugging
            try:
                cfg_path = get_config_file()
                snippet = {
                    "current_theme": self.current_theme,
                    "font_family": cfg.get("font_family"),
                    "editor_line_numbers": cfg.get("editor_settings", {}).get(
                        "line_numbers"
                    ),
                }
                print(f"🔍 Config path: {cfg_path} | keys: {snippet}")
                # Write a small startup log for debugging
                try:
                    log_file = cfg_path.parent / "startup.log"
                    with open(log_file, "a", encoding="utf-8") as lf:
                        lf.write(
                            f"{datetime.now().isoformat()} - Loaded config: {snippet}\n"
                        )
                except Exception:
                    pass
            except Exception:
                pass
        except Exception as e:
            print(f"⚠️ Theme loading error: {e}")
            self.current_theme = "forest"

    def apply_saved_settings(self):
        """Apply saved editor and general settings from ThemeManager.config.

        This method is safe to call after UI initialization; it will attempt to
        apply font settings and editor flags to any already-created editor tabs.
        """
        try:
            cfg = getattr(self.theme_manager, "config", {}) or {}

            # Editor settings
            editor_cfg = (
                cfg.get("editor_settings", {})
                if isinstance(cfg.get("editor_settings", {}), dict)
                else {}
            )

            font_family = cfg.get("font_family") or editor_cfg.get("font_family")
            font_size = cfg.get("font_size") or editor_cfg.get("font_size")

            if font_family is None:
                font_family = "Consolas"
            if font_size is None:
                font_size = 11

            # Apply to existing editor tabs if present
            if hasattr(self, "multi_tab_editor") and self.multi_tab_editor:
                wrap_mode = tk.WORD if editor_cfg.get("word_wrap", False) else tk.NONE
                for tab in self.multi_tab_editor.tabs.values():
                    try:
                        if hasattr(tab, "text_editor"):
                            tab.text_editor.configure(
                                font=(font_family, int(font_size)), wrap=wrap_mode
                            )
                        # Line numbers handling if supported by tab
                        if hasattr(tab, "line_numbers"):
                            if editor_cfg.get("line_numbers", True):
                                try:
                                    tab.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
                                except Exception:
                                    pass
                            else:
                                try:
                                    tab.line_numbers.pack_forget()
                                except Exception:
                                    pass
                    except Exception:
                        pass

            # Store remember flags on instance for later use
            self.remember_tabs = bool(cfg.get("remember_tabs", True))
            self.auto_save = bool(cfg.get("auto_save", False))

        except Exception as e:
            print(f"⚠️ Failed to apply saved settings: {e}")

    def _setup_window(self):
        """Setup main window properties"""
        self.root.title("⏰ Time Warp IDE - Journey Through Code")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)

        # Set window icon if available
        try:
            # Try to set an icon (optional)
            pass
        except Exception:
            pass

    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts - delegates to setup_keybindings"""
        self.setup_keybindings()

    def init_features(self):
        """Initialize additional features"""
        try:
            # Initialize error handler
            self.error_handler = EnhancedErrorHandler()

            # Simplified feature initialization for 1.1
            # Advanced features will be added in future versions

        except Exception as e:
            print(f"⚠️ Feature initialization error: {e}")

    def setup_ui(self):
        """Setup the enhanced UI with clean two-panel layout"""
        # Create main container with two-panel layout (editor + graphics/output)
        self.main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left panel: Code Editor (takes most space)
        self.editor_panel = ttk.Frame(self.main_container)
        try:
            self.main_container.add(self.editor_panel, weight=3, minsize=600)
        except Exception:
            self.main_container.add(self.editor_panel, weight=3)

        # Right panel: Graphics and Output
        self.graphics_output_panel = ttk.Frame(self.main_container, width=400)
        try:
            self.main_container.add(self.graphics_output_panel, weight=1, minsize=350)
        except Exception:
            self.main_container.add(self.graphics_output_panel, weight=1)

        # Setup components
        self.setup_menu()
        self.setup_multi_tab_editor()
        self.setup_output_graphics_panel()

    def setup_menu(self):
        """Setup enhanced menu system"""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        # File menu
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(
            label="📄 New File", command=self.new_file, accelerator="Ctrl+N"
        )
        file_menu.add_command(
            label="📂 Open File", command=self.open_file, accelerator="Ctrl+O"
        )
        file_menu.add_command(
            label="📁 Open Folder", command=self.open_folder, accelerator="Ctrl+Shift+O"
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="💾 Save", command=self.save_file, accelerator="Ctrl+S"
        )
        file_menu.add_command(
            label="💾 Save As", command=self.save_as_file, accelerator="Ctrl+Shift+S"
        )
        file_menu.add_command(
            label="💾 Save All", command=self.save_all_files, accelerator="Ctrl+Alt+S"
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="❌ Close Tab", command=self.close_current_tab, accelerator="Ctrl+W"
        )
        file_menu.add_command(
            label="🚪 Exit", command=self.quit_app, accelerator="Ctrl+Q"
        )

        # Edit menu
        edit_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(
            label="🔍 Find", command=self.find_text, accelerator="Ctrl+F"
        )
        edit_menu.add_command(
            label="🔁 Replace", command=self.replace_text, accelerator="Ctrl+H"
        )
        edit_menu.add_separator()
        edit_menu.add_command(label="↩️ Undo", accelerator="Ctrl+Z")
        edit_menu.add_command(label="↪️ Redo", accelerator="Ctrl+Y")

        # View menu (NEW)
        view_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(
            label="🔍 Zoom In", command=self.zoom_in, accelerator="Ctrl++"
        )
        view_menu.add_command(
            label="🔍 Zoom Out", command=self.zoom_out, accelerator="Ctrl+-"
        )
        view_menu.add_command(
            label="🔍 Reset Zoom", command=self.reset_zoom, accelerator="Ctrl+0"
        )
        view_menu.add_separator()
        view_menu.add_command(
            label="🎨 Toggle Graphics Panel", command=self.toggle_graphics_panel
        )
        view_menu.add_separator()

        # Theme settings moved to Tools menu (use Tools -> Theme Settings...)

        # Run menu
        run_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(
            label="▶️ Run Code", command=self.run_code, accelerator="F5"
        )
        run_menu.add_command(
            label="⏹️ Stop", command=self.stop_execution, accelerator="Shift+F5"
        )
        run_menu.add_separator()
        run_menu.add_command(label="🗑️ Clear Output", command=self.clear_output)
        run_menu.add_command(label="🗑️ Clear Graphics", command=self.clear_graphics)

        # Tools menu
        tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="⚙️ Settings", command=self.show_settings)
        tools_menu.add_command(
            label="🔌 Plugin Manager", command=self.show_plugin_manager
        )

        # Features menu
        features_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Features", menu=features_menu)
        features_menu.add_command(
            label="📚 Tutorial System", command=self.show_tutorial_system
        )
        features_menu.add_command(
            label="🤖 AI Assistant", command=self.show_ai_assistant
        )
        features_menu.add_command(
            label="🎮 Gamification", command=self.show_gamification_dashboard
        )
        features_menu.add_separator()
        features_menu.add_command(
            label="📝 Code Templates", command=self.show_code_templates
        )
        features_menu.add_command(
            label="🔍 Code Analyzer", command=self.show_code_analyzer
        )
        features_menu.add_command(
            label="📊 Learning Progress", command=self.show_learning_progress
        )

        # Help menu
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="📖 Documentation", command=self.show_documentation)
        help_menu.add_command(
            label="🆘 Quick Help", command=self.show_quick_help, accelerator="F1"
        )
        help_menu.add_separator()

    def setup_multi_tab_editor(self):
        """Setup multi-tab code editor"""
        # Editor with status bar
        editor_frame = ttk.Frame(self.editor_panel)
        editor_frame.pack(fill=tk.BOTH, expand=True)

        # Multi-tab editor
        self.multi_tab_editor = MultiTabEditor(
            editor_frame, language_callback=self.update_language_indicator
        )

        # Status bar for editor
        status_frame = ttk.Frame(editor_frame)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_label = ttk.Label(
            status_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        # Language indicator
        self.language_label = ttk.Label(
            status_frame, text="TW PILOT", relief=tk.SUNKEN, width=12
        )
        self.language_label.pack(side=tk.RIGHT, padx=2)

        # Initialize language indicator
        self.root.after_idle(self.update_language_indicator)
        # end of setup_multi_tab_editor

    def setup_output_graphics_panel(self):
        """Setup right panel with output and graphics"""
        # Create notebook for output and graphics
        self.graphics_notebook = ttk.Notebook(self.graphics_output_panel)
        self.graphics_notebook.pack(fill=tk.BOTH, expand=True)

        # Output tab
        output_frame = ttk.Frame(self.graphics_notebook)
        self.graphics_notebook.add(output_frame, text="📺 Output")

        self.output_text = scrolledtext.ScrolledText(
            output_frame, state=tk.DISABLED, wrap=tk.WORD, font=("Consolas", 10)
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Connect interpreter to output widget with custom handler
        # Create a custom output handler that respects our GUI's disabled state
        class OutputHandler:
            def __init__(self, gui_instance):
                self.gui = gui_instance

            def insert(self, position, text):
                # Use the GUI's write_to_console method which handles state properly
                self.gui.write_to_console(text)

            def see(self, position):
                # Already handled by write_to_console
                pass

        self.interpreter.output_widget = OutputHandler(self)

        # Graphics tab
        graphics_frame = ttk.Frame(self.graphics_notebook)
        self.graphics_notebook.add(graphics_frame, text="🎨 Graphics")

        # Enhanced graphics canvas
        if ENHANCED_GRAPHICS_AVAILABLE:
            self.enhanced_graphics = EnhancedGraphicsCanvas(graphics_frame, 380, 300)

            # Connect to interpreter (using correct interface)
            try:
                # Set the ide_turtle_canvas that the interpreter expects
                self.interpreter.ide_turtle_canvas = self.enhanced_graphics.get_canvas()

                # Don't set turtle_graphics here - let interpreter initialize it properly
                # The interpreter's init_turtle_graphics() method will handle the full initialization
            except AttributeError:
                print("⚠️ Turtle graphics integration needs updating")
        else:
            # Fallback to basic canvas
            self.basic_canvas = tk.Canvas(
                graphics_frame,
                width=380,
                height=300,
                bg="white",
                highlightthickness=1,
                highlightbackground="#cccccc",
            )
            self.basic_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # Basic turtle setup
            import turtle

            screen = turtle.TurtleScreen(self.basic_canvas)
            screen.bgcolor("white")
            turtle_obj = turtle.RawTurtle(screen)
            turtle_obj.speed(5)
            turtle_obj.shape("turtle")

            # Set the ide_turtle_canvas for interpreter compatibility
            self.interpreter.ide_turtle_canvas = self.basic_canvas

    def setup_keybindings(self):
        """Setup keyboard shortcuts"""
        keybindings = {
            "<Control-n>": self.new_file,
            "<Control-o>": self.open_file,
            "<Control-s>": self.save_file,
            "<Control-Shift-S>": self.save_as_file,
            "<Control-w>": self.close_current_tab,
            "<Control-q>": self.quit_app,
            "<F5>": self.run_code,
            "<Shift-F5>": self.stop_execution,
            "<Control-f>": self.find_text,
            "<Control-h>": self.replace_text,
            "<F1>": self.show_quick_help,
            "<Control-plus>": self.zoom_in,
            "<Control-minus>": self.zoom_out,
            "<Control-0>": self.reset_zoom,
        }

        for key, command in keybindings.items():
            self.root.bind(key, lambda e, cmd=command: cmd())

    # File operations
    def new_file(self):
        """Create new file in editor"""
        self.multi_tab_editor.new_tab()
        # Reapply theme to ensure new tab gets proper colors
        self.apply_theme()
        self.update_status("New file created")

    def open_file(self):
        """Open file dialog and load file"""
        file_path = filedialog.askopenfilename(
            title="Open File",
            filetypes=[
                ("All Time_Warp files", "*.py *.js *.pilot *.bas *.logo *.pl"),
                ("Python files", "*.py"),
                ("TW BASIC files", "*.bas"),
                ("TW Logo files", "*.logo"),
                ("TW PILOT files", "*.pilot"),
                ("JavaScript files", "*.js"),
                ("Perl files", "*.pl"),
                ("All files", "*.*"),
            ],
        )
        if file_path:
            self.multi_tab_editor.open_file(file_path)
            # Reapply theme to ensure new tab gets proper colors
            self.apply_theme()
            self.update_status(f"Opened: {os.path.basename(file_path)}")

    def open_folder(self):
        """Open folder for reference"""
        folder_path = filedialog.askdirectory(title="Select Working Directory")
        if folder_path:
            os.chdir(folder_path)
            self.update_status(f"Working directory: {os.path.basename(folder_path)}")

    def save_file(self):
        """Save current file"""
        if self.multi_tab_editor.save_active_tab():
            self.update_status("File saved")
        else:
            self.update_status("Save cancelled")

    def save_as_file(self):
        """Save current file with new name"""
        if self.multi_tab_editor.save_active_tab_as():
            self.update_status("File saved as new name")
        else:
            self.update_status("Save as cancelled")

    def save_all_files(self):
        """Save all open files"""
        saved_count = 0
        for tab in self.multi_tab_editor.tabs.values():
            if tab.is_modified:
                if tab.save_file():
                    saved_count += 1
        self.update_status(f"Saved {saved_count} files")

    def close_current_tab(self):
        """Close current tab"""
        self.multi_tab_editor.close_tab()

    # Editor operations
    def find_text(self):
        """Show find dialog"""
        if not self.multi_tab_editor.active_tab:
            self.update_status("No active tab to search")
            return

        search_term = simpledialog.askstring("Find", "Enter text to find:")
        if search_term:
            text_widget = self.multi_tab_editor.active_tab.text_editor

            # Clear previous search highlights
            text_widget.tag_remove("search_highlight", "1.0", tk.END)

            # Search for the term
            start_pos = "1.0"
            found_positions = []

            while True:
                pos = text_widget.search(search_term, start_pos, tk.END)
                if not pos:
                    break
                found_positions.append(pos)
                # Highlight the found text
                end_pos = f"{pos}+{len(search_term)}c"
                text_widget.tag_add("search_highlight", pos, end_pos)
                start_pos = end_pos

            # Configure highlight style
            text_widget.tag_configure(
                "search_highlight", background="yellow", foreground="black"
            )

            if found_positions:
                # Move to first occurrence
                text_widget.see(found_positions[0])
                text_widget.mark_set("insert", found_positions[0])
                self.update_status(
                    f"Found {len(found_positions)} occurrence(s) of '{search_term}'"
                )
            else:
                self.update_status(f"'{search_term}' not found")
        else:
            self.update_status("Search cancelled")

    def replace_text(self):
        """Show replace dialog"""
        if not self.multi_tab_editor.active_tab:
            self.update_status("No active tab for replacement")
            return

        # Create replace dialog window
        replace_window = tk.Toplevel(self.root)
        replace_window.title("Find and Replace")
        replace_window.geometry("400x150")
        replace_window.resizable(False, False)

        # Center the window
        replace_window.transient(self.root)
        replace_window.grab_set()

        # Find field
        tk.Label(replace_window, text="Find:").grid(
            row=0, column=0, sticky="w", padx=10, pady=5
        )
        find_entry = tk.Entry(replace_window, width=30)
        find_entry.grid(row=0, column=1, padx=10, pady=5)
        find_entry.focus()

        # Replace field
        tk.Label(replace_window, text="Replace with:").grid(
            row=1, column=0, sticky="w", padx=10, pady=5
        )
        replace_entry = tk.Entry(replace_window, width=30)
        replace_entry.grid(row=1, column=1, padx=10, pady=5)

        # Button frame
        button_frame = tk.Frame(replace_window)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        def do_find():
            search_term = find_entry.get()
            if search_term and self.multi_tab_editor.active_tab:
                text_widget = self.multi_tab_editor.active_tab.text_editor
                text_widget.tag_remove("search_highlight", "1.0", tk.END)

                pos = text_widget.search(search_term, "insert", tk.END)
                if pos:
                    end_pos = f"{pos}+{len(search_term)}c"
                    text_widget.tag_add("search_highlight", pos, end_pos)
                    text_widget.tag_configure(
                        "search_highlight", background="yellow", foreground="black"
                    )
                    text_widget.see(pos)
                    text_widget.mark_set("insert", pos)
                    self.update_status(f"Found '{search_term}'")
                else:
                    self.update_status(f"'{search_term}' not found")

        def do_replace():
            search_term = find_entry.get()
            replace_term = replace_entry.get()
            if search_term and self.multi_tab_editor.active_tab:
                text_widget = self.multi_tab_editor.active_tab.text_editor
                content = text_widget.get("1.0", tk.END)
                new_content = content.replace(search_term, replace_term)

                if content != new_content:
                    text_widget.delete("1.0", tk.END)
                    text_widget.insert("1.0", new_content)
                    count = content.count(search_term)
                    self.update_status(f"Replaced {count} occurrence(s)")
                    self.multi_tab_editor.active_tab.is_modified = True
                    self.multi_tab_editor.active_tab.update_tab_title()
                else:
                    self.update_status("No replacements made")
                replace_window.destroy()

        # Buttons
        tk.Button(button_frame, text="Find Next", command=do_find).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(button_frame, text="Replace All", command=do_replace).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(button_frame, text="Cancel", command=replace_window.destroy).pack(
            side=tk.LEFT, padx=5
        )

    # View operations
    def zoom_in(self):
        """Zoom in graphics canvas"""
        if hasattr(self.enhanced_graphics, "zoom_in"):
            self.enhanced_graphics.zoom_in()

    def zoom_out(self):
        """Zoom out graphics canvas"""
        if hasattr(self.enhanced_graphics, "zoom_out"):
            self.enhanced_graphics.zoom_out()

    def reset_zoom(self):
        """Reset graphics canvas zoom"""
        if hasattr(self.enhanced_graphics, "zoom_fit"):
            self.enhanced_graphics.zoom_fit()

    def toggle_graphics_panel(self):
        """Toggle graphics panel visibility"""
        try:
            if hasattr(self, "graphics_output_panel"):
                # Check current state
                if self.graphics_output_panel.winfo_viewable():
                    # Hide the panel by removing it from the container
                    self.main_container.forget(self.graphics_output_panel)
                    self.update_status("Graphics panel hidden")
                else:
                    # Show the panel by adding it back
                    try:
                        self.main_container.add(
                            self.graphics_output_panel, weight=1, minsize=350
                        )
                    except Exception:
                        self.main_container.add(self.graphics_output_panel, weight=1)
                    self.update_status("Graphics panel shown")
            else:
                self.update_status("Graphics panel not available")
        except Exception as e:
            self.update_status(f"Panel toggle error: {e}")

    # Execution operations
    def run_code(self):
        """Run code from active tab"""
        code = self.multi_tab_editor.get_active_content()
        if not code.strip():
            self.update_status("No code to run")
            return

        # Detect language from active tab
        active_tab = self.multi_tab_editor.active_tab
        if active_tab:
            language = active_tab.language
        else:
            language = "python"  # Default

        self.update_status(f"Running {language.upper()} code...")

        # Clear previous output
        self.clear_output()

        # Reset stop flag
        self.stop_execution_flag = False

        # Run code in a separate thread for better responsiveness
        def run_in_thread():
            try:
                self.write_to_console(f"▶️ Starting {language.upper()} execution...\n")

                # Execute code using the interpreter for all supported languages
                try:
                    # Check for stop flag
                    if self.stop_execution_flag:
                        self.write_to_console("🛑 Execution stopped by user\n")
                        return

                    # Use the interpreter's run_program method which handles all languages
                    result = self.interpreter.run_program(
                        code, language=language.lower()
                    )

                    if result is None:
                        # If run_program returns None, it means the language isn't supported yet
                        self.write_to_console(
                            f"🔧 {language.upper()} language support coming soon!\n"
                        )
                        self.write_to_console(
                            f"Currently supported: TW PILOT, TW BASIC, TW Logo, Python, JavaScript, Perl\n"
                        )
                        result = False

                except Exception as e:
                    self.write_to_console(
                        f"❌ {language.upper()} Execution Error: {str(e)}\n"
                    )
                    result = False

                if not self.stop_execution_flag:
                    if result:
                        self.write_to_console(
                            f"✅ {language.upper()} execution completed\n"
                        )
                        self.root.after(
                            0,
                            lambda: self.update_status(
                                f"{language.upper()} code executed successfully"
                            ),
                        )

                        # Force graphics update for Logo programs
                        if language.lower() == "logo":
                            self.root.after(0, self.update_graphics_display)
                    else:
                        self.write_to_console(
                            f"❌ {language.upper()} execution failed\n"
                        )
                        self.root.after(
                            0,
                            lambda: self.update_status(
                                f"{language.upper()} execution failed"
                            ),
                        )

            except Exception as e:
                self.write_to_console(f"💥 Execution error: {str(e)}\n")
                self.root.after(
                    0, lambda: self.update_status(f"Execution error: {str(e)}")
                )

        # Start execution thread
        self.execution_thread = threading.Thread(target=run_in_thread, daemon=True)
        self.execution_thread.start()

    def stop_execution(self):
        """Stop code execution"""
        try:
            # If there's an active execution thread, try to stop it
            if (
                hasattr(self, "execution_thread")
                and self.execution_thread
                and self.execution_thread.is_alive()
            ):
                # Set a stop flag for graceful termination
                if hasattr(self, "stop_execution_flag"):
                    self.stop_execution_flag = True

                self.write_to_console("🛑 Execution stop requested...\n")
                self.update_status("Stopping execution...")

                # Give thread a moment to stop gracefully
                import time

                time.sleep(0.1)

                if self.execution_thread.is_alive():
                    self.write_to_console(
                        "⚠️ Force stopping execution (may not work for all code)\n"
                    )

                self.update_status("Execution stopped")
            else:
                self.write_to_console("ℹ️ No active execution to stop\n")
                self.update_status("No running code to stop")

        except Exception as e:
            self.update_status(f"Stop execution error: {e}")

    def clear_output(self):
        """Clear output console"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.update_status("Output cleared")

    def clear_graphics(self):
        """Clear graphics canvas"""
        if ENHANCED_GRAPHICS_AVAILABLE and hasattr(self, "enhanced_graphics"):
            if hasattr(self.enhanced_graphics, "clear_canvas"):
                self.enhanced_graphics.clear_canvas()
        elif hasattr(self, "basic_canvas"):
            self.basic_canvas.delete("all")
            # Reset turtle to center
            if (
                hasattr(self.interpreter, "turtle_graphics")
                and self.interpreter.turtle_graphics
            ):
                screen = self.interpreter.turtle_graphics.get("screen")
                turtle_obj = self.interpreter.turtle_graphics.get("turtle")
                if screen and turtle_obj:
                    turtle_obj.home()
                    screen.update()

    def update_graphics_display(self):
        """Force update of graphics display after Logo execution"""
        try:
            if ENHANCED_GRAPHICS_AVAILABLE and hasattr(self, "enhanced_graphics"):
                # Update enhanced graphics canvas
                canvas = self.enhanced_graphics.get_canvas()
                if canvas:
                    canvas.update_idletasks()
                    canvas.update()
            elif hasattr(self, "basic_canvas"):
                # Update basic turtle graphics
                if (
                    hasattr(self.interpreter, "turtle_graphics")
                    and self.interpreter.turtle_graphics
                ):
                    screen = self.interpreter.turtle_graphics.get("screen")
                    if screen:
                        screen.update()
                        print("🎨 Graphics display updated")
                # Also update the canvas widget
                self.basic_canvas.update_idletasks()
        except Exception as e:
            print(f"⚠️ Graphics update error: {e}")

    # Utility methods
    def write_to_console(self, text: str):
        """Write text to output console"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def update_status(self, message: str):
        """Update status bar"""
        if hasattr(self, "status_label"):
            self.status_label.config(text=message)
            # Clear after 3 seconds
            self.root.after(3000, lambda: self.status_label.config(text="Ready"))

    def detect_language_from_extension(self, filename: str) -> str:
        """Detect language from file extension"""
        if not filename:
            return "Text"

        filename = filename.lower()
        if filename.endswith(".pilot"):
            return "TW PILOT"
        elif filename.endswith(".bas") or filename.endswith(".basic"):
            return "TW BASIC"
        elif filename.endswith(".logo"):
            return "TW Logo"
        elif filename.endswith(".py"):
            return "Python"
        elif filename.endswith(".js"):
            return "JavaScript"
        elif filename.endswith(".pl"):
            return "Perl"
        # Removed .jtc and .time_warp extensions - these were TempleCode remnants
        else:
            return "Text"

    def detect_language_from_content(self, content: str) -> str:
        """Detect language from code content"""
        if not content:
            return "Text"

        content_lower = content.lower()
        lines = content.split("\n")

        # Check for line numbers (TW BASIC)
        has_line_numbers = any(
            line.strip() and line.strip()[0].isdigit() for line in lines[:5]
        )
        if has_line_numbers and any(
            word in content_lower for word in ["print", "let", "goto", "if"]
        ):
            return "TW BASIC"

        # Check for PILOT commands
        pilot_commands = ["t:", "a:", "j:", "y:", "n:", "c:", "e:", "m:"]
        if any(cmd in content_lower for cmd in pilot_commands):
            return "TW PILOT"

        # Check for Logo commands
        logo_commands = [
            "forward",
            "back",
            "left",
            "right",
            "penup",
            "pendown",
            "repeat",
        ]
        if any(cmd in content_lower for cmd in logo_commands):
            return "TW Logo"

        # Check for Python
        python_keywords = ["def ", "import ", "from ", "class ", "if __name__"]
        if any(keyword in content_lower for keyword in python_keywords):
            return "Python"

        # Check for JavaScript
        js_keywords = ["function", "var ", "let ", "const ", "document.", "window."]
        if any(keyword in content_lower for keyword in js_keywords):
            return "JavaScript"

        return "Text"

    def update_language_indicator(self):
        """Update the language indicator based on current tab"""
        try:
            if hasattr(self, "language_label") and hasattr(self, "multi_tab_editor"):
                active_tab = self.multi_tab_editor.active_tab
                if active_tab:
                    # Get filename from tab's file_path or filename attribute
                    filename = (
                        getattr(active_tab, "file_path", "")
                        or getattr(active_tab, "filename", "")
                        or ""
                    )
                    content = self.multi_tab_editor.get_active_content() or ""

                    # Try extension first, then content
                    detected_lang = self.detect_language_from_extension(filename)
                    if detected_lang == "Text" and content:
                        detected_lang = self.detect_language_from_content(content)

                    # Update the label
                    self.language_label.config(text=f"Lang: {detected_lang}")
                    print(f"🔄 Language updated to: {detected_lang}")

                    # Update editor syntax highlighting if needed
                    if hasattr(active_tab, "apply_syntax_highlighting"):
                        active_tab.apply_syntax_highlighting()
                else:
                    self.language_label.config(text="Lang: None")
        except Exception as e:
            print(f"⚠️ Language indicator update error: {e}")

    # Feature system methods (placeholder implementations)
    def show_tutorial_system(self):
        """Show interactive tutorial system"""
        try:
            # Create tutorial window
            tutorial_window = tk.Toplevel(self.root)
            tutorial_window.title("📚 Time_Warp IDE Tutorial System")
            tutorial_window.geometry("800x600")
            tutorial_window.transient(self.root)
            tutorial_window.grab_set()

            # Apply current theme to tutorial window
            self.apply_theme_to_window(tutorial_window)

            # Create notebook for tutorial categories
            notebook = ttk.Notebook(tutorial_window)
            notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # TW Overview Tutorial
            basic_frame = ttk.Frame(notebook)
            notebook.add(basic_frame, text="� TW Overview")

            basic_text = tk.Text(basic_frame, wrap=tk.WORD, font=("Consolas", 11))
            basic_scrollbar = ttk.Scrollbar(
                basic_frame, orient=tk.VERTICAL, command=basic_text.yview
            )
            basic_text.configure(yscrollcommand=basic_scrollbar.set)

            basic_content = """� TIME_WARP IDE OVERVIEW

Welcome to Time_Warp IDE - Your Gateway to Programming History!

⏰ Time_Warp bridges the gap between vintage programming languages and modern development, offering an educational environment where you can explore the evolution of programming paradigms.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 OUR MISSION
To make programming history accessible, educational, and fun through interactive learning experiences that span from 1960s educational languages to modern scripting.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 SUPPORTED LANGUAGES OVERVIEW

1. 🚁 TW PILOT (1962) - Educational Programming
   • Designed for teaching programming concepts
   • English-like syntax for beginners
   • Commands: T: (Type), A: (Accept), J: (Jump), Y: (Yes), N: (No)
   • Perfect for: Learning basic programming logic

2. 🔢 TW BASIC (1964) - Classic Line-Numbered Programming
   • Traditional BASIC with line numbers
   • Commands: PRINT, INPUT, LET, GOTO, IF...THEN, FOR...NEXT
   • Perfect for: Understanding structured programming

3. 🐢 TW Logo (1967) - Turtle Graphics Programming
   • Visual programming with turtle graphics
   • Commands: FORWARD, BACK, LEFT, RIGHT, PENUP, PENDOWN
   • Perfect for: Learning geometry and visual programming

4. 📚 TW Pascal (1970) - Structured Programming
   • Strongly typed, procedural language
   • Features: Records, pointers, procedures, functions
   • Perfect for: Learning data structures and algorithms

5. 🧠 TW Prolog (1972) - Logic Programming
   • Declarative programming paradigm
   • Based on formal logic and predicate calculus
   • Perfect for: AI, expert systems, and logical reasoning

6. ⚡ TW Forth (1970) - Stack-Based Programming
   • Concatenative, stack-based language
   • Extremely efficient and low-level
   • Perfect for: Embedded systems and real-time programming

7. 🐍 Python (1991) - Modern Scripting
   • High-level, interpreted language
   • Extensive standard library and ecosystem
   • Perfect for: Web development, data science, automation

8. 🌐 JavaScript (1995) - Web Programming
   • Prototype-based scripting language
   • Essential for web development
   • Perfect for: Interactive web applications

9. 💎 Perl (1987) - Text Processing
   • Powerful text manipulation capabilities
   • "Swiss Army knife" of scripting languages
   • Perfect for: System administration and text processing

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎮 UNIQUE FEATURES

✨ Multi-Language Environment
• Switch between languages seamlessly
• Compare programming paradigms
• Understand language evolution

🎨 Integrated Graphics
• Turtle graphics for visual programming
• Real-time drawing and animation
• Export capabilities

🤖 AI-Powered Assistance
• Context-aware code suggestions
• Language-specific help
• Debugging assistance

📚 Interactive Tutorials
• Step-by-step learning modules
• Comprehensive language guides
• Progress tracking

🏆 Gamification System
• Achievement badges
• Skill progression
• Programming challenges

🔧 Code Analysis Tools
• Syntax checking
• Performance profiling
• Code quality metrics

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 LEARNING PATH RECOMMENDED

BEGINNER (Start Here):
1. TW PILOT - Learn basic programming concepts
2. TW Logo - Discover visual programming
3. TW BASIC - Master structured programming

INTERMEDIATE:
4. TW Pascal - Explore data structures
5. TW Python - Modern programming practices
6. TW JavaScript - Web development basics

ADVANCED:
7. TW Prolog - Logic programming paradigm
8. TW Forth - Low-level programming concepts
9. TW Perl - Advanced text processing

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 WHY TIME_WARP?

• 🕰️ Historical Context: Understand how programming evolved
• 🎓 Educational Focus: Designed for learning and teaching
• 🔄 Paradigm Diversity: Experience different programming approaches
• 🎮 Interactive Learning: Visual feedback and gamification
• 🌍 Community Driven: Open source and collaborative
• 🚀 Future Ready: Modern IDE features with historical languages

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 GETTING STARTED

1. Choose Your First Language
   • New to programming? Start with TW PILOT
   • Visual learner? Try TW Logo
   • Traditional approach? Begin with TW BASIC

2. Explore the Interface
   • Multi-tab editor for multiple files
   • Integrated graphics canvas
   • Output console for results

3. Learn Through Examples
   • Use the AI Assistant for help
   • Browse code templates
   • Complete tutorial challenges

4. Track Your Progress
   • View achievements in Gamification Dashboard
   • Monitor learning progress
   • Set personal goals

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Happy coding through time! ⏰✨

Remember: Every programming language teaches you something unique about computation. Time_Warp IDE helps you discover the rich history and diverse paradigms that shaped modern programming."""

            basic_text.insert(tk.END, basic_content)
            basic_text.config(state=tk.DISABLED)

            basic_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            basic_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # PILOT Language Tutorial
            pilot_frame = ttk.Frame(notebook)
            notebook.add(pilot_frame, text="🚁 TW PILOT Language")

            pilot_text = tk.Text(pilot_frame, wrap=tk.WORD, font=("Consolas", 11))
            pilot_scrollbar = ttk.Scrollbar(
                pilot_frame, orient=tk.VERTICAL, command=pilot_text.yview
            )
            pilot_text.configure(yscrollcommand=pilot_scrollbar.set)

            pilot_content = """🚁 PILOT LANGUAGE TUTORIAL

PILOT is perfect for interactive learning!

BASIC COMMANDS:
• T: - Type (display text)
• A: - Accept (get user input)
• J: - Jump (go to label)
• Y: - Yes (conditional jump)
• N: - No (conditional jump)

EXAMPLES:

1. HELLO WORLD:
   T:Hello, World!
   T:Welcome to PILOT programming!

2. INTERACTIVE PROGRAM:
   T:What's 2 + 2?
   A:
   M:4
   Y:T:Correct! Well done!
   N:T:Try again. The answer is 4.

3. SIMPLE QUIZ:
   *START
   T:What language was created in 1962?
   A:
   M:PILOT
   Y:J(CORRECT)
   T:Wrong! It was PILOT.
   J(END)
   *CORRECT
   T:Excellent! You know your programming history!
   *END
   T:Thanks for playing!

4. TURTLE GRAPHICS:
   Use these commands to draw:
   FORWARD 100    - Move forward
   BACK 50        - Move backward
   LEFT 90        - Turn left
   RIGHT 45       - Turn right
   PENUP          - Stop drawing
   PENDOWN        - Start drawing

TRY IT NOW:
Copy any example above into the editor and press F5!"""

            pilot_text.insert(tk.END, pilot_content)
            pilot_text.config(state=tk.DISABLED)

            pilot_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            pilot_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # BASIC Language Tutorial
            basic_lang_frame = ttk.Frame(notebook)
            notebook.add(basic_lang_frame, text="📊 TW BASIC Language")

            basic_lang_text = tk.Text(
                basic_lang_frame, wrap=tk.WORD, font=("Consolas", 11)
            )
            basic_lang_scrollbar = ttk.Scrollbar(
                basic_lang_frame, orient=tk.VERTICAL, command=basic_lang_text.yview
            )
            basic_lang_text.configure(yscrollcommand=basic_lang_scrollbar.set)

            basic_lang_content = """📊 BASIC LANGUAGE TUTORIAL

BASIC uses line numbers and is great for structured programs!

ESSENTIAL COMMANDS:
• PRINT - Display text or values
• INPUT - Get user input
• LET - Assign values to variables
• IF...THEN - Conditional statements
• FOR...NEXT - Loops
• GOTO - Jump to line number
• END - End program

EXAMPLES:

1. SIMPLE CALCULATOR:
   10 PRINT "Simple Calculator"
   20 PRINT "Enter first number:"
   30 INPUT A
   40 PRINT "Enter second number:"
   50 INPUT B
   60 LET C = A + B
   70 PRINT "Sum is: "; C
   80 END

2. COUNTING LOOP:
   10 FOR I = 1 TO 10
   20 PRINT "Count: "; I
   30 NEXT I
   40 PRINT "Done counting!"
   50 END

3. GUESSING GAME:
   10 LET N = INT(RND * 100) + 1
   20 PRINT "Guess my number (1-100):"
   30 INPUT G
   40 IF G = N THEN GOTO 80
   50 IF G < N THEN PRINT "Too low!"
   60 IF G > N THEN PRINT "Too high!"
   70 GOTO 30
   80 PRINT "Correct! The number was "; N
   90 END

4. GRAPHICS DEMO:
   10 FOR I = 1 TO 360 STEP 10
   20 FORWARD 50
   30 RIGHT I
   40 NEXT I
   50 END

VARIABLES:
• Use A, B, C for numbers
• Use A$, B$, C$ for text (strings)
• Arrays: DIM A(100) for 100 numbers"""

            basic_lang_text.insert(tk.END, basic_lang_content)
            basic_lang_text.config(state=tk.DISABLED)

            basic_lang_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            basic_lang_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Logo Language Tutorial
            logo_frame = ttk.Frame(notebook)
            notebook.add(logo_frame, text="🐢 TW Logo Language")

            logo_text = tk.Text(logo_frame, wrap=tk.WORD, font=("Consolas", 11))
            logo_scrollbar = ttk.Scrollbar(
                logo_frame, orient=tk.VERTICAL, command=logo_text.yview
            )
            logo_text.configure(yscrollcommand=logo_scrollbar.set)

            logo_content = """🐢 LOGO LANGUAGE TUTORIAL

Logo is perfect for graphics and turtle programming!

TURTLE COMMANDS:
• FORWARD (FD) - Move forward
• BACK (BK) - Move backward  
• LEFT (LT) - Turn left
• RIGHT (RT) - Turn right
• PENUP (PU) - Stop drawing
• PENDOWN (PD) - Start drawing
• HOME - Return to center
• CLEARSCREEN (CS) - Clear screen

EXAMPLES:

1. DRAW A SQUARE:
   FORWARD 100
   RIGHT 90
   FORWARD 100
   RIGHT 90
   FORWARD 100
   RIGHT 90
   FORWARD 100
   RIGHT 90

2. DRAW A TRIANGLE:
   FORWARD 100
   LEFT 120
   FORWARD 100
   LEFT 120
   FORWARD 100
   LEFT 120

3. SPIRAL PATTERN:
   REPEAT 36 [FORWARD 100 RIGHT 170]

4. FLOWER PATTERN:
   REPEAT 36 [
     REPEAT 4 [FORWARD 50 RIGHT 90]
     RIGHT 10
   ]

5. COLORFUL DESIGN:
   SETPENCOLOR "RED"
   REPEAT 8 [FORWARD 100 RIGHT 45]
   SETPENCOLOR "BLUE"
   REPEAT 8 [FORWARD 80 LEFT 45]

PROCEDURES (Functions):
   TO SQUARE :SIZE
     REPEAT 4 [FORWARD :SIZE RIGHT 90]
   END
   
   # Then use it:
   SQUARE 50
   SQUARE 100

TIPS:
• Watch the turtle move in the graphics panel
• Try different colors and patterns
• Use REPEAT for loops
• Create your own procedures with TO...END"""

            logo_text.insert(tk.END, logo_content)
            logo_text.config(state=tk.DISABLED)

            logo_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            logo_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # TW Pascal Tutorial
            pascal_frame = ttk.Frame(notebook)
            notebook.add(pascal_frame, text="📚 TW Pascal")

            pascal_text = tk.Text(pascal_frame, wrap=tk.WORD, font=("Consolas", 11))
            pascal_scrollbar = ttk.Scrollbar(
                pascal_frame, orient=tk.VERTICAL, command=pascal_text.yview
            )
            pascal_text.configure(yscrollcommand=pascal_scrollbar.set)

            pascal_content = """📚 PASCAL LANGUAGE TUTORIAL

Pascal is a strongly typed, procedural programming language designed for teaching structured programming and data structures.

HISTORY & DESIGN PHILOSOPHY:
• Created by Niklaus Wirth in 1970
• Designed for education and system programming
• Influenced languages like Ada, Modula-2, and Oberon
• Emphasizes structured programming and data typing

BASIC SYNTAX:
• Case-sensitive language
• Statements end with semicolons (;)
• Programs have clear structure with BEGIN...END blocks
• Strong type checking prevents many runtime errors

PROGRAM STRUCTURE:
program HelloWorld;
begin
    writeln('Hello, World!');
end.

DATA TYPES:
• Integer: whole numbers (-32768 to 32767)
• Real: floating-point numbers
• Boolean: true/false values
• Char: single characters
• String: text strings

EXAMPLES:

1. HELLO WORLD:
program HelloWorld;
begin
    writeln('Hello, World!');
    writeln('Welcome to Pascal programming!');
end.

2. VARIABLES AND INPUT:
program UserGreeting;
var
    name: string;
    age: integer;
begin
    write('What is your name? ');
    readln(name);
    write('How old are you? ');
    readln(age);
    writeln('Hello, ', name, '! You are ', age, ' years old.');
end.

3. CONDITIONAL STATEMENTS:
program NumberCheck;
var
    num: integer;
begin
    write('Enter a number: ');
    readln(num);
    if num > 0 then
        writeln('Positive number')
    else if num < 0 then
        writeln('Negative number')
    else
        writeln('Zero');
end.

4. LOOPS:
program Counting;
var
    i: integer;
begin
    writeln('Counting to 10:');
    for i := 1 to 10 do
        write(i, ' ');
    writeln;

    writeln('Even numbers:');
    i := 2;
    while i <= 10 do
    begin
        write(i, ' ');
        i := i + 2;
    end;
    writeln;
end.

5. PROCEDURES AND FUNCTIONS:
program MathOperations;
var
    a, b: integer;

function Add(x, y: integer): integer;
begin
    Add := x + y;
end;

procedure DisplayResult(op: string; result: integer);
begin
    writeln(op, ' = ', result);
end;

begin
    a := 10;
    b := 5;
    DisplayResult('Addition', Add(a, b));
    DisplayResult('Subtraction', a - b);
    DisplayResult('Multiplication', a * b);
end.

6. ARRAYS:
program ArrayDemo;
var
    numbers: array[1..5] of integer;
    i: integer;
begin
    // Initialize array
    for i := 1 to 5 do
        numbers[i] := i * 10;

    // Display array
    writeln('Array contents:');
    for i := 1 to 5 do
        write(numbers[i], ' ');
    writeln;
end.

7. RECORDS (STRUCTS):
program StudentRecord;
type
    Student = record
        name: string;
        age: integer;
        grade: real;
    end;

var
    student1: Student;

begin
    student1.name := 'Alice';
    student1.age := 20;
    student1.grade := 95.5;

    writeln('Student Information:');
    writeln('Name: ', student1.name);
    writeln('Age: ', student1.age);
    writeln('Grade: ', student1.grade:4:1);
end.

8. FILE OPERATIONS:
program FileDemo;
var
    infile, outfile: text;
    line: string;
begin
    // Write to file
    assign(outfile, 'output.txt');
    rewrite(outfile);
    writeln(outfile, 'Hello from Pascal!');
    writeln(outfile, 'This is a test file.');
    close(outfile);

    // Read from file
    assign(infile, 'output.txt');
    reset(infile);
    while not eof(infile) do
    begin
        readln(infile, line);
        writeln('Read: ', line);
    end;
    close(infile);
end.

KEY FEATURES:
• Strong typing prevents type errors
• Clear program structure with begin/end blocks
• Procedures and functions for modular code
• Records for complex data structures
• File I/O capabilities
• Pointers for dynamic memory management

PROGRAMMING PARADIGMS:
• Procedural programming
• Structured programming
• Modular design
• Top-down design approach

COMMON USES:
• Educational programming
• System programming
• Compiler development
• Database applications
• Scientific computing

TIPS FOR SUCCESS:
• Always declare variables before use
• Use meaningful variable names
• Structure programs with proper indentation
• Test programs with various inputs
• Use procedures to organize code

Pascal teaches disciplined programming practices that are valuable in any language!"""

            pascal_text.insert(tk.END, pascal_content)
            pascal_text.config(state=tk.DISABLED)

            pascal_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            pascal_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # TW Prolog Tutorial
            prolog_frame = ttk.Frame(notebook)
            notebook.add(prolog_frame, text="🧠 TW Prolog")

            prolog_text = tk.Text(prolog_frame, wrap=tk.WORD, font=("Consolas", 11))
            prolog_scrollbar = ttk.Scrollbar(
                prolog_frame, orient=tk.VERTICAL, command=prolog_text.yview
            )
            prolog_text.configure(yscrollcommand=prolog_scrollbar.set)

            prolog_content = """🧠 PROLOG LANGUAGE TUTORIAL

Prolog is a logic programming language based on formal logic and predicate calculus. It's particularly powerful for AI, expert systems, and symbolic computation.

HISTORY & DESIGN PHILOSOPHY:
• Created by Alain Colmerauer and Philippe Roussel in 1972
• Based on Robinson's resolution principle
• Designed for natural language processing and AI research
• Uses declarative programming paradigm

CORE CONCEPTS:
• Facts: Statements that are unconditionally true
• Rules: Conditional statements (if-then relationships)
• Queries: Questions you ask the system
• Unification: Pattern matching and variable binding
• Backtracking: Automatic search through possibilities

BASIC SYNTAX:
• Facts end with a period (.)
• Rules use :- (if) operator
• Variables start with uppercase letters
• Constants and predicates start with lowercase
• Lists use square brackets: [1, 2, 3]

EXAMPLES:

1. BASIC FACTS:
% Facts about people
person(alice).
person(bob).
person(charlie).

% Facts about relationships
parent(alice, bob).
parent(bob, charlie).

% Facts about likes
likes(alice, reading).
likes(bob, swimming).
likes(charlie, games).

2. SIMPLE QUERIES:
?- person(alice).        % Is alice a person? (yes)
?- parent(alice, bob).   % Is alice parent of bob? (yes)
?- likes(alice, X).      % What does alice like? (reading)

3. RULES:
% Define grandparent relationship
grandparent(X, Z) :- parent(X, Y), parent(Y, Z).

% Define sibling relationship
sibling(X, Y) :- parent(Z, X), parent(Z, Y), X \\= Y.

% Define ancestor relationship (recursive)
ancestor(X, Y) :- parent(X, Y).
ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).

4. LISTS AND RECURSION:
% Length of a list
list_length([], 0).
list_length([_|Tail], Length) :-
    list_length(Tail, TailLength),
    Length is TailLength + 1.

% Sum of list elements
sum_list([], 0).
sum_list([Head|Tail], Sum) :-
    sum_list(Tail, TailSum),
    Sum is Head + TailSum.

% Check if element is in list
member(X, [X|_]).
member(X, [_|Tail]) :- member(X, Tail).

5. MATHEMATICAL RELATIONS:
% Factorial
factorial(0, 1).
factorial(N, Result) :-
    N > 0,
    N1 is N - 1,
    factorial(N1, Result1),
    Result is N * Result1.

% Fibonacci
fib(0, 0).
fib(1, 1).
fib(N, Result) :-
    N > 1,
    N1 is N - 1,
    N2 is N - 2,
    fib(N1, Result1),
    fib(N2, Result2),
    Result is Result1 + Result2.

6. EXPERT SYSTEM EXAMPLE:
% Animal classification expert system
mammal(X) :- has_fur(X), gives_milk(X).
bird(X) :- has_feathers(X), lays_eggs(X).
reptile(X) :- has_scales(X), cold_blooded(X).

% Facts about animals
has_fur(cat).
has_fur(dog).
gives_milk(cat).
gives_milk(dog).

has_feathers(sparrow).
lays_eggs(sparrow).

has_scales(snake).
cold_blooded(snake).

% Classification queries:
?- mammal(cat).      % yes
?- bird(sparrow).    % yes
?- reptile(snake).   % yes

7. NATURAL LANGUAGE PROCESSING:
% Simple English sentence parser
sentence(S) :- noun_phrase(NP), verb_phrase(VP), append(NP, VP, S).

noun_phrase([Det, N]) :- determiner(Det), noun(N).
verb_phrase([V, NP]) :- verb(V), noun_phrase(NP).

determiner([the]).
determiner([a]).

noun([cat]).
noun([dog]).
noun([mat]).

verb([sat]).
verb([chased]).

% Parse: "the cat sat on the mat"
?- sentence([the, cat, sat, on, the, mat]).

8. SOLVING PUZZLES:
% Eight queens problem (simplified 4x4 version)
queens([]).
queens([Q|Qs]) :- queens(Qs), member(Q, [1,2,3,4]), safe(Q, Qs, 1).

safe(_, [], _).
safe(Q, [Q1|Qs], D) :- Q \\=\\= Q1, abs(Q - Q1) \\=\\= D, safe(Q, Qs, D + 1).

% Find solution: ?- queens([A,B,C,D]).

9. DATABASE QUERIES:
% Employee database
employee(john, manager, 75000).
employee(sarah, developer, 65000).
employee(mike, designer, 55000).

department(manager, engineering).
department(developer, engineering).
department(designer, design).

% Queries
?- employee(Name, Position, Salary), Salary > 60000.
?- employee(Name, _, _), department(_, Dept).

KEY FEATURES:
• Declarative programming (what, not how)
• Automatic backtracking and search
• Pattern matching and unification
• Recursive definitions
• Built-in theorem prover

PROGRAMMING PARADIGMS:
• Logic programming
• Declarative programming
• Constraint programming
• Symbolic computation

COMMON USES:
• Artificial Intelligence
• Expert systems
• Natural language processing
• Automated theorem proving
• Database query systems
• Puzzle solving
• Knowledge representation

PROLOG THINKING:
• Think in terms of relationships and rules
• Let Prolog handle the "how" - you specify the "what"
• Use recursion for repetitive structures
• Facts are your knowledge base
• Rules define relationships and inferences

TIPS FOR SUCCESS:
• Start with simple facts and queries
• Understand unification and backtracking
• Use meaningful predicate names
• Test rules with various queries
• Think declaratively, not procedurally

Prolog will change how you think about programming - it's a paradigm shift worth experiencing!"""

            prolog_text.insert(tk.END, prolog_content)
            prolog_text.config(state=tk.DISABLED)

            prolog_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            prolog_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # TW Forth Tutorial
            forth_frame = ttk.Frame(notebook)
            notebook.add(forth_frame, text="⚡ TW Forth")

            forth_text = tk.Text(forth_frame, wrap=tk.WORD, font=("Consolas", 11))
            forth_scrollbar = ttk.Scrollbar(
                forth_frame, orient=tk.VERTICAL, command=forth_text.yview
            )
            forth_text.configure(yscrollcommand=forth_scrollbar.set)

            forth_content = """⚡ FORTH LANGUAGE TUTORIAL

Forth is a stack-based, concatenative programming language known for its efficiency, extensibility, and low-level control. It's widely used in embedded systems and real-time applications.

HISTORY & DESIGN PHILOSOPHY:
• Created by Charles H. Moore in 1970
• Designed for efficiency and low resource usage
• Influenced by earlier languages like Lisp and APL
• "Forth" stands for "Fourth-generation language"

STACK-BASED ARCHITECTURE:
• All operations work on a data stack
• Parameters passed via stack manipulation
• Results returned on the stack
• No variables in traditional sense (though available)

BASIC CONCEPTS:
• Words: Functions/subroutines in Forth
• Stack: LIFO data structure for parameters/results
• Dictionary: Collection of defined words
• Colon definitions: User-defined words (: word-name ... ;)
• Immediate execution vs. compilation

STACK OPERATIONS:
• DUP: Duplicate top stack item
• DROP: Remove top stack item
• SWAP: Exchange top two items
• OVER: Copy second item to top
• ROT: Rotate top three items

EXAMPLES:

1. BASIC ARITHMETIC:
5 3 + .     \\ 8 (5 + 3 = 8)
10 4 - .    \\ 6 (10 - 4 = 6)
3 4 * .     \\ 12 (3 * 4 = 12)
15 3 / .    \\ 5 (15 / 3 = 5)

2. STACK MANIPULATION:
5 DUP . .   \\ 5 5 (duplicate and print both)
1 2 3 . . . \\ 3 2 1 (print in reverse order)
4 5 SWAP . . \\ 4 5 (swap and print)

3. FIRST WORDS:
: SQUARE DUP * ;     \\ Define square function
5 SQUARE .           \\ 25

: CUBE DUP DUP * * ; \\ Define cube function
3 CUBE .             \\ 27

4. VARIABLES AND CONSTANTS:
VARIABLE COUNTER    \\ Define variable
10 COUNTER !        \\ Store 10 in COUNTER
COUNTER @ .         \\ Retrieve and print: 10

CONSTANT PI 314     \\ Define constant (314/100 = 3.14)
PI .                \\ 314

5. LOOPS:
10 0 DO I . LOOP    \\ Print 0 1 2 ... 9

: COUNT-DOWN
    BEGIN
        DUP .       \\ Print current value
        1 -         \\ Decrement
        DUP 0 <     \\ Check if negative
    UNTIL           \\ Exit when true
    DROP            \\ Remove final negative value
;

10 COUNT-DOWN       \\ 10 9 8 7 6 5 4 3 2 1 0

6. CONDITIONALS:
: IS-EVEN?
    2 MOD 0 = IF
        ." Even" CR
    ELSE
        ." Odd" CR
    THEN
;

4 IS-EVEN?          \\ Even
7 IS-EVEN?          \\ Odd

: COMPARE
    2DUP < IF       \\ Compare top two items
        ." Less than" CR
    ELSE 2DUP > IF
        ." Greater than" CR
    ELSE
        ." Equal" CR
    THEN THEN
    2DROP           \\ Clean up stack
;

5 3 COMPARE         \\ Greater than

7. STRINGS:
: HELLO ." Hello, World!" CR ;

HELLO               \\ Hello, World!

S" Forth is fun!" TYPE CR    \\ Print string

8. ARRAYS:
CREATE ARRAY 10 CELLS ALLOT   \\ Create array of 10 cells

: STORE-ARRAY ( value index -- )
    CELLS ARRAY + !           \\ Store value at index
;

: FETCH-ARRAY ( index -- value )
    CELLS ARRAY + @           \\ Fetch value from index
;

42 0 STORE-ARRAY              \\ Store 42 at index 0
0 FETCH-ARRAY .              \\ 42

9. RECURSION:
: FACTORIAL
    DUP 1 > IF
        DUP 1 - RECURSE *    \\ Recursive call
    ELSE
        DROP 1               \\ Base case: 0! = 1! = 1
    THEN
;

5 FACTORIAL .               \\ 120

10. GRAPHICS EXAMPLE:
: DRAW-SQUARE ( size -- )
    DUP FORWARD 90 RIGHT    \\ Repeat 4 times
    DUP FORWARD 90 RIGHT
    DUP FORWARD 90 RIGHT
         FORWARD 90 RIGHT
    DROP
;

\\ Draw nested squares
100 DRAW-SQUARE
50 DRAW-SQUARE

11. LOW-LEVEL CONTROL:
HEX                    \\ Switch to hexadecimal
: PORT-OUT ( value port -- )
    OUT             \\ Output to port (system dependent)
;

DEC                    \\ Back to decimal

12. EXTENSIBLE COMPILER:
: CONSTANT ( "name" value -- )
    CREATE ,       \\ Create word and store value
    DOES> @        \\ Runtime: fetch value
;

13 PI CONSTANT MY-PI   \\ Define constant
MY-PI .               \\ Print value

KEY FEATURES:
• Extremely efficient and fast
• Minimal memory footprint
• Extensible language (write your own compiler)
• Direct hardware access
• Interactive development
• Threaded code for efficiency

PROGRAMMING PARADIGMS:
• Concatenative programming
• Stack-based programming
• Interactive programming
• Metaprogramming

COMMON USES:
• Embedded systems
• Real-time applications
• Robotics control
• Scientific instruments
• Bootloaders and firmware
• Industrial automation
• Spacecraft control systems

FORTH PHILOSOPHY:
• Keep it simple and minimal
• Build complex systems from simple primitives
• Interactive development and testing
• Direct control over hardware
• "If you want it done right, do it yourself"

TIPS FOR SUCCESS:
• Always know what's on the stack
• Use .S frequently to inspect stack
• Build incrementally and test often
• Learn stack manipulation thoroughly
• Think in terms of data flow
• Use meaningful word names

Forth will teach you to think about programming at the lowest level while maintaining high-level abstractions. It's a unique paradigm that rewards deep understanding!"""

            forth_text.insert(tk.END, forth_content)
            forth_text.config(state=tk.DISABLED)

            forth_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            forth_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Close button
            close_btn = ttk.Button(
                tutorial_window, text="Close Tutorial", command=tutorial_window.destroy
            )
            close_btn.pack(pady=10)

            print("📚 Tutorial system opened")

        except Exception as e:
            messagebox.showerror(
                "Tutorial Error", f"Failed to open tutorial system:\n{str(e)}"
            )
            print(f"❌ Tutorial system error: {e}")

    def show_ai_assistant(self):
        """Show AI coding assistant"""
        try:
            # Create AI assistant window
            ai_window = tk.Toplevel(self.root)
            ai_window.title("🤖 AI Coding Assistant")
            ai_window.geometry("700x500")
            ai_window.transient(self.root)
            ai_window.grab_set()

            # Apply current theme
            self.apply_theme_to_window(ai_window)

            # Create main frame
            main_frame = ttk.Frame(ai_window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Title
            title_label = ttk.Label(
                main_frame, text="🤖 AI Coding Assistant", font=("Arial", 14, "bold")
            )
            title_label.pack(pady=(0, 10))

            # Create notebook for different AI features
            notebook = ttk.Notebook(main_frame)
            notebook.pack(fill=tk.BOTH, expand=True)

            # Code Helper Tab
            helper_frame = ttk.Frame(notebook)
            notebook.add(helper_frame, text="💡 Code Helper")

            # Language selection
            lang_frame = ttk.Frame(helper_frame)
            lang_frame.pack(fill=tk.X, pady=(0, 10))

            ttk.Label(lang_frame, text="Language:").pack(side=tk.LEFT)
            lang_var = tk.StringVar(value="TW PILOT")
            lang_combo = ttk.Combobox(
                lang_frame,
                textvariable=lang_var,
                values=["TW PILOT", "TW BASIC", "TW Logo", "Python"],
                state="readonly",
                width=10,
            )
            lang_combo.pack(side=tk.LEFT, padx=(5, 0))

            # Query input
            ttk.Label(helper_frame, text="Ask the AI:").pack(anchor=tk.W, pady=(0, 5))
            query_text = tk.Text(helper_frame, height=3, wrap=tk.WORD)
            query_text.pack(fill=tk.X, pady=(0, 10))
            query_text.insert(tk.END, "How do I draw a circle in Logo?")

            # Response area
            ttk.Label(helper_frame, text="AI Response:").pack(anchor=tk.W, pady=(0, 5))
            response_text = tk.Text(
                helper_frame, height=15, wrap=tk.WORD, font=("Consolas", 10)
            )
            response_scrollbar = ttk.Scrollbar(
                helper_frame, orient=tk.VERTICAL, command=response_text.yview
            )
            response_text.configure(yscrollcommand=response_scrollbar.set)

            response_frame = ttk.Frame(helper_frame)
            response_frame.pack(fill=tk.BOTH, expand=True)
            response_text.pack(
                in_=response_frame, side=tk.LEFT, fill=tk.BOTH, expand=True
            )
            response_scrollbar.pack(in_=response_frame, side=tk.RIGHT, fill=tk.Y)

            def ask_ai():
                """Generate AI response based on query"""
                query = query_text.get("1.0", tk.END).strip()
                language = lang_var.get()

                # Simple AI responses based on common questions
                responses = {
                    "PILOT": {
                        "hello": "T:Hello, World!\nT:Welcome to PILOT programming!\n\nThis displays two lines of text.",
                        "input": "T:What's your name?\nA:\nT:Nice to meet you!\n\nA: accepts user input",
                        "loop": "Use labels and J: (Jump) for loops:\n*START\nT:Count: $COUNT\nC:COUNT + 1\nY(START):COUNT < 10",
                        "graphics": "FORWARD 100  # Move forward\nRIGHT 90     # Turn right\nFORWARD 50   # Draw a line",
                    },
                    "BASIC": {
                        "hello": '10 PRINT "Hello, World!"\n20 END\n\nThis prints text and ends the program.',
                        "input": '10 PRINT "Enter your name:"\n20 INPUT N$\n30 PRINT "Hello "; N$; "!"\n40 END',
                        "loop": '10 FOR I = 1 TO 10\n20 PRINT "Count: "; I\n30 NEXT I\n40 END',
                        "graphics": "10 FOR I = 1 TO 4\n20 FORWARD 100\n30 RIGHT 90\n40 NEXT I\n50 END",
                    },
                    "Logo": {
                        "circle": "REPEAT 360 [FORWARD 1 RIGHT 1]\n\nThis draws a circle by moving forward 1 unit and turning right 1 degree, repeated 360 times.",
                        "square": "REPEAT 4 [FORWARD 100 RIGHT 90]\n\nDraws a square with 100-unit sides.",
                        "spiral": "REPEAT 100 [FORWARD :I RIGHT 91]\n\nCreates a spiral pattern.",
                        "flower": "REPEAT 36 [\n  REPEAT 4 [FORWARD 50 RIGHT 90]\n  RIGHT 10\n]\n\nDraws a flower pattern with 36 squares.",
                    },
                    "Pascal": {
                        "hello": 'program HelloWorld;\nbegin\n  writeln(\'Hello, World!\');\nend.\n\nThis is a complete Pascal program.',
                        "input": 'program GetName;\nvar\n  name: string;\nbegin\n  write(\'Enter your name: \');\n  readln(name);\n  writeln(\'Hello, \', name);\nend.',
                        "loop": 'program CountToTen;\nvar\n  i: integer;\nbegin\n  for i := 1 to 10 do\n    writeln(i);\nend.',
                        "function": 'program Factorial;\nfunction fact(n: integer): integer;\nbegin\n  if n <= 1 then\n    fact := 1\n  else\n    fact := n * fact(n-1);\nend;\nbegin\n  writeln(fact(5));\nend.',
                    },
                    "Prolog": {
                        "hello": 'hello :- write(\'Hello, World!\'), nl.\n\nQuery: ?- hello.\n\nThis defines a predicate that writes "Hello, World!".',
                        "facts": 'parent(john, mary).\nparent(mary, ann).\n\nQuery: ?- parent(john, mary).\n\nThis defines family relationships.',
                        "rules": 'ancestor(X, Y) :- parent(X, Y).\nancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).\n\nThis defines recursive ancestor relationships.',
                        "query": '?- ancestor(john, ann).\n\nThis queries if john is an ancestor of ann.',
                    },
                    "Forth": {
                        "hello": ': HELLO ." Hello, World!" CR ;\nHELLO\n\nThis defines and calls a word that prints "Hello, World!".',
                        "stack": '5 3 + .     \\ Result: 8\n10 4 - .    \\ Result: 6\n3 4 * .     \\ Result: 12',
                        "word": ': SQUARE DUP * ;\n5 SQUARE .   \\ Result: 25\n\nThis defines a word that squares a number.',
                        "loop": '10 0 DO I . LOOP    \\ Prints 0 1 2 ... 9\n\nThis counts from 0 to 9.',
                    },
                    "Python": {
                        "hello": 'print("Hello, World!")\n\nSimple text output in Python.',
                        "input": 'name = input("What\'s your name? ")\nprint(f"Hello, {name}!")',
                        "loop": 'for i in range(1, 11):\n    print(f"Count: {i}")',
                        "function": 'def greet(name):\n    return f"Hello, {name}!"\n\nprint(greet("World"))',
                    },
                }

                # Generate response
                lang_responses = responses.get(language, {})
                response = "I'd be happy to help! Here are some examples:\n\n"

                # Check for keywords in query
                query_lower = query.lower()
                if "hello" in query_lower or "world" in query_lower:
                    response += lang_responses.get(
                        "hello", "Try: print('Hello, World!')"
                    )
                elif "input" in query_lower or "name" in query_lower:
                    response += lang_responses.get(
                        "input", "Use input() to get user input"
                    )
                elif "loop" in query_lower or "repeat" in query_lower:
                    response += lang_responses.get("loop", "Use loops to repeat code")
                elif "circle" in query_lower and language == "Logo":
                    response += lang_responses.get(
                        "circle", "Use REPEAT to draw circles"
                    )
                elif "square" in query_lower and language == "Logo":
                    response += lang_responses.get("square", "Use REPEAT 4 for squares")
                elif "function" in query_lower and language == "Python":
                    response += lang_responses.get(
                        "function", "Use def to create functions"
                    )
                else:
                    # General help
                    response += f"For {language} programming:\n\n"
                    if language == "PILOT":
                        response += "• T: - Display text\n• A: - Get input\n• J: - Jump to label\n• M: - Match input"
                    elif language == "BASIC":
                        response += "• PRINT - Display text\n• INPUT - Get input\n• FOR...NEXT - Loops\n• IF...THEN - Conditions"
                    elif language == "Logo":
                        response += "• FORWARD/BACK - Move turtle\n• LEFT/RIGHT - Turn turtle\n• REPEAT - Loop commands\n• PENUP/PENDOWN - Control drawing"
                    elif language == "Pascal":
                        response += "• program...end. - Program structure\n• var - Variable declarations\n• begin...end - Code blocks\n• writeln/readln - I/O operations"
                    elif language == "Prolog":
                        response += "• Facts: Define relationships\n• Rules: Define inferences\n• Queries: Ask questions\n• :- (neck) - Rule definition"
                    elif language == "Forth":
                        response += "• : word ; - Define words\n• DUP DROP SWAP - Stack operations\n• . - Print top of stack\n• CR - Carriage return"
                    elif language == "Python":
                        response += "• print() - Display text\n• input() - Get input\n• for/while - Loops\n• if/elif/else - Conditions"

                response += f"\n\n💡 Try running this code in Time_Warp IDE!"

                response_text.delete("1.0", tk.END)
                response_text.insert(tk.END, response)

            # Ask button
            ask_btn = ttk.Button(helper_frame, text="Ask AI", command=ask_ai)
            ask_btn.pack(pady=10)

            # Code Examples Tab
            examples_frame = ttk.Frame(notebook)
            notebook.add(examples_frame, text="📝 Examples")

            examples_text = tk.Text(examples_frame, wrap=tk.WORD, font=("Consolas", 10))
            examples_scrollbar = ttk.Scrollbar(
                examples_frame, orient=tk.VERTICAL, command=examples_text.yview
            )
            examples_text.configure(yscrollcommand=examples_scrollbar.set)

            examples_content = """📝 CODE EXAMPLES FOR ALL LANGUAGES

🚁 PILOT EXAMPLES:
-------------------
Simple Greeting:
T:Hello! What's your name?
A:
T:Nice to meet you, $INPUT!

Quiz Program:
T:What's 5 + 3?
A:
M:8
Y:T:Correct!
N:T:Try again!

🔢 BASIC EXAMPLES:
------------------
Calculator:
10 INPUT "First number: "; A
20 INPUT "Second number: "; B
30 PRINT "Sum: "; A + B
40 END

Counting Game:
10 FOR I = 1 TO 5
20 PRINT "Count: "; I
30 FOR J = 1 TO 1000: NEXT J
40 NEXT I
50 END

🐢 LOGO EXAMPLES:
-----------------
House Drawing:
REPEAT 4 [FORWARD 100 RIGHT 90]
FORWARD 100
RIGHT 30
FORWARD 100
RIGHT 120
FORWARD 100
RIGHT 30

Colorful Pattern:
REPEAT 8 [
  SETPENCOLOR "RED"
  FORWARD 100
  RIGHT 45
  SETPENCOLOR "BLUE"
  FORWARD 50
]

� PASCAL EXAMPLES:
-------------------
Hello World:
program HelloWorld;
begin
  writeln('Hello, World!');
end.

Factorial Function:
program Factorial;
function fact(n: integer): integer;
begin
  if n <= 1 then
    fact := 1
  else
    fact := n * fact(n-1);
end;
begin
  writeln(fact(5));
end.

🔍 PROLOG EXAMPLES:
-------------------
Family Tree:
parent(john, mary).
parent(mary, ann).
ancestor(X, Y) :- parent(X, Y).
ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).

Query: ?- ancestor(john, ann).

Eight Queens:
queens([]).
queens([Q|Qs]) :- queens(Qs), member(Q, [1,2,3,4]), safe(Q, Qs, 1).
safe(_, [], _).
safe(Q, [Q1|Qs], D) :- Q \\=\\= Q1, abs(Q - Q1) \\=\\= D, safe(Q, Qs, D + 1).

⚡ FORTH EXAMPLES:
-----------------
Stack Operations:
5 3 + .     \\ 8
10 4 - .    \\ 6
3 4 * .     \\ 12

Word Definition:
: SQUARE DUP * ;
5 SQUARE .   \\ 25

Loop:
10 0 DO I . LOOP    \\ 0 1 2 ... 9

�🐍 PYTHON EXAMPLES:
-------------------
File Reader:
with open("test.txt", "r") as file:
    content = file.read()
    print(content)

Simple Game:
import random
number = random.randint(1, 100)
guess = int(input("Guess (1-100): "))
if guess == number:
    print("Correct!")
else:
    print(f"Wrong! It was {number}")

💡 TIP: Copy any example and paste it into Time_Warp IDE!"""

            examples_text.insert(tk.END, examples_content)
            examples_text.config(state=tk.DISABLED)

            examples_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            examples_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Close button
            close_btn = ttk.Button(
                main_frame, text="Close Assistant", command=ai_window.destroy
            )
            close_btn.pack(pady=10)

            # Initial AI response
            ask_ai()

            print("🤖 AI Assistant opened")

        except Exception as e:
            messagebox.showerror(
                "AI Assistant Error", f"Failed to open AI assistant:\n{str(e)}"
            )
            print(f"❌ AI Assistant error: {e}")

    def show_gamification_dashboard(self):
        """Show gamification and achievement dashboard"""
        try:
            # Create gamification window
            game_window = tk.Toplevel(self.root)
            game_window.title("🎮 Gamification Dashboard")
            game_window.geometry("800x600")
            game_window.transient(self.root)
            game_window.grab_set()

            # Apply current theme
            self.apply_theme_to_window(game_window)

            # Create main frame
            main_frame = ttk.Frame(game_window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Title
            title_label = ttk.Label(
                main_frame,
                text="🎮 Time_Warp IDE Gamification",
                font=("Arial", 16, "bold"),
            )
            title_label.pack(pady=(0, 20))

            # Create notebook for different sections
            notebook = ttk.Notebook(main_frame)
            notebook.pack(fill=tk.BOTH, expand=True)

            # Achievements Tab
            achievements_frame = ttk.Frame(notebook)
            notebook.add(achievements_frame, text="🏆 Achievements")

            # Achievement list
            achievements_text = tk.Text(
                achievements_frame, wrap=tk.WORD, font=("Arial", 11)
            )
            achievements_scrollbar = ttk.Scrollbar(
                achievements_frame, orient=tk.VERTICAL, command=achievements_text.yview
            )
            achievements_text.configure(yscrollcommand=achievements_scrollbar.set)

            achievements_content = """🏆 ACHIEVEMENT SYSTEM

Welcome to Time_Warp IDE's Learning Journey! Complete challenges to unlock achievements and level up your programming skills!

🥇 BEGINNER ACHIEVEMENTS:
▣ First Steps - Run your first program in any language
▣ Hello World - Create a "Hello, World!" program
▣ Code Explorer - Try all 7 programming languages (PILOT, BASIC, Logo, Python, Pascal, Prolog, Forth)
▣ File Master - Save and load 5 different programs
▣ Theme Collector - Try all 8 available themes

🥈 INTERMEDIATE ACHIEVEMENTS:
▣ Loop Master - Write 3 different types of loops
▣ Graphics Artist - Create 5 turtle graphics programs
▣ Problem Solver - Fix 10 code errors using the error messages
▣ Speed Coder - Write a program in under 2 minutes
▣ Multi-Tab Pro - Work with 5 tabs simultaneously

🥉 ADVANCED ACHIEVEMENTS:
▣ Language Polyglot - Write the same program in all 7 languages
▣ Graphics Wizard - Create complex geometric patterns
▣ Code Optimizer - Improve program efficiency by 50%
▣ Teaching Assistant - Help others learn programming concepts
▣ Innovation Award - Create something completely original

🌟 SPECIAL ACHIEVEMENTS:
▣ Retro Programmer - Master PILOT language commands
▣ BASIC Pioneer - Create advanced BASIC programs with graphics
▣ Logo Legend - Draw intricate patterns and designs
▣ Python Expert - Use advanced Python features
▣ Pascal Structured - Master structured programming with procedures
▣ Prolog Logic Master - Create complex logic programs with rules
▣ Forth Stack Wizard - Master stack-based programming techniques
▣ Time_Warp Master - Unlock all other achievements

📊 CURRENT PROGRESS:
• Programs Run: 0/100 ⭐
• Languages Used: 0/7 🔤
• Files Saved: 0/50 💾
• Themes Tried: 1/8 🎨
• Errors Fixed: 0/25 🔧

🎯 DAILY CHALLENGES:
• Today: Write a program that draws your initials
• Bonus: Use at least 3 different colors
• Reward: +50 XP and "Artist" badge

💡 TIPS TO EARN ACHIEVEMENTS:
1. Experiment with different languages regularly
2. Save your work frequently
3. Try new themes to keep things fresh
4. Don't be afraid to make mistakes - they help you learn!
5. Share your cool programs with others

🔥 STREAK COUNTER: 0 days
Keep coding daily to build your streak!"""

            achievements_text.insert(tk.END, achievements_content)
            achievements_text.config(state=tk.DISABLED)

            achievements_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            achievements_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Progress Tab
            progress_frame = ttk.Frame(notebook)
            notebook.add(progress_frame, text="📊 Progress")

            # Create progress indicators
            progress_main = ttk.Frame(progress_frame)
            progress_main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            # Level display
            level_frame = ttk.LabelFrame(progress_main, text="Your Level", padding=10)
            level_frame.pack(fill=tk.X, pady=(0, 20))

            ttk.Label(
                level_frame,
                text="🌟 Level 1: Novice Programmer",
                font=("Arial", 14, "bold"),
            ).pack()
            ttk.Label(level_frame, text="XP: 0 / 100", font=("Arial", 12)).pack()

            # Progress bar
            level_progress = ttk.Progressbar(
                level_frame, length=300, mode="determinate"
            )
            level_progress["value"] = 0
            level_progress.pack(pady=10)

            # Stats
            stats_frame = ttk.LabelFrame(progress_main, text="Statistics", padding=10)
            stats_frame.pack(fill=tk.X, pady=(0, 20))

            stats_grid = ttk.Frame(stats_frame)
            stats_grid.pack(fill=tk.X)

            # Left column
            left_stats = ttk.Frame(stats_grid)
            left_stats.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            ttk.Label(
                left_stats, text="📝 Programs Written: 0", font=("Arial", 11)
            ).pack(anchor=tk.W, pady=2)
            ttk.Label(left_stats, text="🚀 Programs Run: 0", font=("Arial", 11)).pack(
                anchor=tk.W, pady=2
            )
            ttk.Label(left_stats, text="💾 Files Saved: 0", font=("Arial", 11)).pack(
                anchor=tk.W, pady=2
            )
            ttk.Label(
                left_stats, text="🔤 Languages Used: 0/7", font=("Arial", 11)
            ).pack(anchor=tk.W, pady=2)

            # Right column
            right_stats = ttk.Frame(stats_grid)
            right_stats.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            ttk.Label(
                right_stats, text="🏆 Achievements: 0/25", font=("Arial", 11)
            ).pack(anchor=tk.W, pady=2)
            ttk.Label(
                right_stats, text="🎨 Themes Tried: 1/8", font=("Arial", 11)
            ).pack(anchor=tk.W, pady=2)
            ttk.Label(
                right_stats, text="🔥 Current Streak: 0 days", font=("Arial", 11)
            ).pack(anchor=tk.W, pady=2)
            ttk.Label(
                right_stats, text="⏱️ Time Coding: 0 minutes", font=("Arial", 11)
            ).pack(anchor=tk.W, pady=2)

            # Language proficiency
            proficiency_frame = ttk.LabelFrame(
                progress_main, text="Language Proficiency", padding=10
            )
            proficiency_frame.pack(fill=tk.X)

            languages = [
                ("🚁 PILOT", 0),
                ("🔢 BASIC", 0),
                ("🐢 Logo", 0),
                ("🐍 Python", 0),
                ("📘 Pascal", 0),
                ("🧠 Prolog", 0),
                ("📚 Forth", 0),
            ]

            for lang, level in languages:
                lang_frame = ttk.Frame(proficiency_frame)
                lang_frame.pack(fill=tk.X, pady=2)

                ttk.Label(lang_frame, text=lang, width=15).pack(side=tk.LEFT)
                prog = ttk.Progressbar(lang_frame, length=200, mode="determinate")
                prog["value"] = level
                prog.pack(side=tk.LEFT, padx=(10, 5))
                ttk.Label(lang_frame, text=f"{level}%").pack(side=tk.LEFT)

            # Challenges Tab
            challenges_frame = ttk.Frame(notebook)
            notebook.add(challenges_frame, text="🎯 Challenges")

            challenges_text = tk.Text(
                challenges_frame, wrap=tk.WORD, font=("Arial", 11)
            )
            challenges_scrollbar = ttk.Scrollbar(
                challenges_frame, orient=tk.VERTICAL, command=challenges_text.yview
            )
            challenges_text.configure(yscrollcommand=challenges_scrollbar.set)

            challenges_content = """🎯 PROGRAMMING CHALLENGES

Ready to test your skills? Complete these challenges to earn XP and achievements!

🟢 BEGINNER CHALLENGES (10 XP each):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Hello Universe
   • Write "Hello, Universe!" in PILOT
   • Bonus: Add your name to the greeting

2. Simple Math
   • Create a BASIC program that adds two numbers
   • Let the user input both numbers

3. Square Dance
   • Draw a square using Logo commands
   • Make it exactly 100 units per side

4. Color Explorer
   • Try 3 different pen colors in Logo
   • Draw something with each color

5. Input Master
   • Get user's name and age in any language
   • Display a personalized message

🟡 INTERMEDIATE CHALLENGES (25 XP each):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
6. Pattern Maker
   • Create a repeating geometric pattern
   • Use at least 5 different shapes

7. Quiz Master
   • Build a 5-question quiz in PILOT
   • Keep score and show final results

8. Loop Artist
   • Use FOR loops to create nested patterns
   • Try both BASIC and Logo

9. Number Guesser
   • Create a guessing game with hints
   • "Too high", "Too low", "Correct!"

10. Multi-Language
    • Write the same program in 3 different languages
    • Try Pascal, Prolog, or Forth for a challenge!

🔴 ADVANCED CHALLENGES (50 XP each):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
11. Fractal Explorer
    • Draw a recursive pattern
    • Make it at least 3 levels deep

12. Animation Creator
    • Create moving graphics
    • Use timing and redrawing

13. Code Golf
    • Solve a problem in minimum lines
    • Every character counts!

14. Teaching Tool
    • Create a program that teaches others
    • Include interactive examples

15. Innovation Challenge
    • Create something completely unique
    • Surprise us with your creativity!

16. Pascal Procedures
    • Write a Pascal program with custom procedures
    • Use functions to organize your code

17. Prolog Logic Puzzle
    • Create a logic puzzle in Prolog
    • Use facts and rules to solve problems

18. Forth Stack Master
    • Write a complex Forth program using the stack
    • Manipulate data efficiently on the stack

19. Structured Code
    • Convert a simple program to structured Pascal
    • Use proper procedures and functions

20. Logic Programming
    • Solve a real-world problem with Prolog rules
    • Create a knowledge base and queries

🏆 WEEKLY CHALLENGES:
━━━━━━━━━━━━━━━━━━━━
This Week: "Retro Game Recreation"
• Recreate a classic game like Pong or Snake
• Use any Time_Warp language
• Deadline: End of week
• Reward: 100 XP + Special Badge

💡 CHALLENGE TIPS:
• Start with easier challenges first
• Don't hesitate to experiment
• Learn from your mistakes
• Ask for help when needed
• Have fun while learning!

🎖️ COMPLETION REWARDS:
• 5 challenges: "Challenge Accepted" badge
• 10 challenges: "Problem Solver" badge  
• 15 challenges: "Challenge Master" badge
• All challenges: "Time_Warp Champion" title"""

            challenges_text.insert(tk.END, challenges_content)
            challenges_text.config(state=tk.DISABLED)

            challenges_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            challenges_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Close button
            close_btn = ttk.Button(
                main_frame, text="Close Dashboard", command=game_window.destroy
            )
            close_btn.pack(pady=10)

            print("🎮 Gamification dashboard opened")

        except Exception as e:
            messagebox.showerror(
                "Gamification Error",
                f"Failed to open gamification dashboard:\n{str(e)}",
            )
            print(f"❌ Gamification error: {e}")

    def show_code_templates(self):
        """Show code templates for quick programming"""
        try:
            # Create templates window
            templates_window = tk.Toplevel(self.root)
            templates_window.title("📝 Code Templates")
            templates_window.geometry("800x600")
            templates_window.transient(self.root)
            templates_window.grab_set()

            # Apply current theme
            self.apply_theme_to_window(templates_window)

            # Create main frame
            main_frame = ttk.Frame(templates_window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Title
            title_label = ttk.Label(
                main_frame, text="📝 Code Templates", font=("Arial", 14, "bold")
            )
            title_label.pack(pady=(0, 10))

            # Language selection
            lang_frame = ttk.Frame(main_frame)
            lang_frame.pack(fill=tk.X, pady=(0, 10))

            ttk.Label(lang_frame, text="Language:").pack(side=tk.LEFT)
            lang_var = tk.StringVar(value="TW PILOT")
            lang_combo = ttk.Combobox(
                lang_frame,
                textvariable=lang_var,
                values=["TW PILOT", "TW BASIC", "TW Logo", "Python"],
                state="readonly",
                width=10,
            )
            lang_combo.pack(side=tk.LEFT, padx=(5, 20))

            # Template categories
            ttk.Label(lang_frame, text="Category:").pack(side=tk.LEFT)
            category_var = tk.StringVar(value="Basic")
            category_combo = ttk.Combobox(
                lang_frame,
                textvariable=category_var,
                values=["Basic", "Loops", "Graphics", "Games", "Math"],
                state="readonly",
                width=10,
            )
            category_combo.pack(side=tk.LEFT, padx=(5, 0))

            # Templates display
            templates_text = tk.Text(
                main_frame, height=25, wrap=tk.NONE, font=("Consolas", 10)
            )
            templates_scrollbar_y = ttk.Scrollbar(
                main_frame, orient=tk.VERTICAL, command=templates_text.yview
            )
            templates_scrollbar_x = ttk.Scrollbar(
                main_frame, orient=tk.HORIZONTAL, command=templates_text.xview
            )
            templates_text.configure(
                yscrollcommand=templates_scrollbar_y.set,
                xscrollcommand=templates_scrollbar_x.set,
            )

            # Template data
            templates = {
                "PILOT": {
                    "Basic": """📝 PILOT BASIC TEMPLATES

1. Hello World Program:
T:Hello, World!
T:Welcome to PILOT programming!

2. User Input:
T:What's your name?
A:
T:Hello, $INPUT!

3. Simple Quiz:
T:What's 2 + 2?
A:
M:4
Y:T:Correct!
N:T:Try again!

4. Conditional Jump:
T:Are you ready? (yes/no)
A:
M:yes
Y:J(START)
T:Come back when ready!
E:
*START
T:Let's begin!""",
                    "Loops": """🔄 PILOT LOOP TEMPLATES

1. Counting Loop:
C:COUNT = 1
*LOOP
T:Count: $COUNT
C:COUNT + 1
Y(LOOP):COUNT <= 10

2. Menu Loop:
*MENU
T:Choose: 1) Start 2) Help 3) Exit
A:
M:1
Y:J(START)
M:2
Y:J(HELP)
M:3
Y:J(EXIT)
J(MENU)

3. Quiz Loop:
C:SCORE = 0
*QUESTION
T:Question: What's the capital of France?
A:
M:Paris
Y:C:SCORE + 1
T:Score: $SCORE
J(QUESTION)""",
                    "Graphics": """🎨 PILOT GRAPHICS TEMPLATES

1. Simple Drawing:
PENDOWN
FORWARD 100
RIGHT 90
FORWARD 100

2. Square Pattern:
REPEAT 4
  FORWARD 100
  RIGHT 90
END

3. Spiral:
C:SIZE = 10
*SPIRAL
FORWARD $SIZE
RIGHT 91
C:SIZE + 5
Y(SPIRAL):SIZE < 200""",
                    "Games": """🎮 PILOT GAME TEMPLATES

1. Number Guessing Game:
C:NUMBER = RND(100) + 1
C:TRIES = 0
*GUESS
T:Guess my number (1-100):
A:
C:TRIES + 1
Y(HIGH):INPUT > NUMBER
Y(LOW):INPUT < NUMBER
T:Correct in $TRIES tries!
E:
*HIGH
T:Too high!
J(GUESS)
*LOW
T:Too low!
J(GUESS)

2. Simple Adventure:
T:You're in a dark room.
T:Go (n)orth or (s)outh?
A:
M:n
Y:J(NORTH)
M:s
Y:J(SOUTH)
*NORTH
T:You found a treasure!
*SOUTH
T:You found a monster!""",
                    "Math": """🔢 PILOT MATH TEMPLATES

1. Calculator:
T:Enter first number:
A:
C:A = INPUT
T:Enter second number:
A:
C:B = INPUT
C:SUM = A + B
T:Sum: $SUM

2. Multiplication Table:
T:Which table? (1-12)
A:
C:NUM = INPUT
C:I = 1
*TABLE
C:RESULT = NUM * I
T:$NUM x $I = $RESULT
C:I + 1
Y(TABLE):I <= 12""",
                },
                "BASIC": {
                    "Basic": """📝 BASIC BASIC TEMPLATES

1. Hello World:
10 PRINT "Hello, World!"
20 END

2. User Input:
10 PRINT "What's your name?"
20 INPUT N$
30 PRINT "Hello "; N$; "!"
40 END

3. Simple Math:
10 INPUT "First number: "; A
20 INPUT "Second number: "; B
30 PRINT "Sum: "; A + B
40 END

4. Conditional:
10 INPUT "Enter a number: "; N
20 IF N > 0 THEN PRINT "Positive"
30 IF N < 0 THEN PRINT "Negative"
40 IF N = 0 THEN PRINT "Zero"
50 END""",
                    "Loops": """🔄 BASIC LOOP TEMPLATES

1. FOR Loop:
10 FOR I = 1 TO 10
20 PRINT "Count: "; I
30 NEXT I
40 END

2. WHILE Loop:
10 LET N = 1
20 WHILE N <= 5
30 PRINT N
40 LET N = N + 1
50 WEND
60 END

3. Nested Loops:
10 FOR I = 1 TO 3
20 FOR J = 1 TO 3
30 PRINT I; "x"; J; "="; I*J
40 NEXT J
50 NEXT I
60 END""",
                    "Graphics": """🎨 BASIC GRAPHICS TEMPLATES

1. Square:
10 FOR I = 1 TO 4
20 FORWARD 100
30 RIGHT 90
40 NEXT I
50 END

2. Colorful Pattern:
10 FOR C = 1 TO 8
20 SETCOLOR C
30 FORWARD 50
40 RIGHT 45
50 NEXT C
60 END

3. Spiral:
10 FOR I = 1 TO 50
20 FORWARD I * 2
30 RIGHT 91
40 NEXT I
50 END""",
                    "Games": """🎮 BASIC GAME TEMPLATES

1. Guessing Game:
10 LET N = INT(RND * 100) + 1
20 LET T = 0
30 PRINT "Guess my number (1-100):"
40 INPUT G
50 LET T = T + 1
60 IF G = N THEN GOTO 100
70 IF G < N THEN PRINT "Too low!"
80 IF G > N THEN PRINT "Too high!"
90 GOTO 40
100 PRINT "Correct in "; T; " tries!"
110 END

2. Rock Paper Scissors:
10 PRINT "Rock (1), Paper (2), Scissors (3):"
20 INPUT P
30 LET C = INT(RND * 3) + 1
40 PRINT "Computer chose: "; C
50 IF P = C THEN PRINT "Tie!"
60 IF (P=1 AND C=3) OR (P=2 AND C=1) OR (P=3 AND C=2) THEN PRINT "You win!"
70 IF (C=1 AND P=3) OR (C=2 AND P=1) OR (C=3 AND P=2) THEN PRINT "You lose!"
80 END""",
                    "Math": """🔢 BASIC MATH TEMPLATES

1. Area Calculator:
10 PRINT "Rectangle area calculator"
20 INPUT "Length: "; L
30 INPUT "Width: "; W
40 PRINT "Area: "; L * W
50 END

2. Prime Checker:
10 INPUT "Enter a number: "; N
20 LET P = 1
30 FOR I = 2 TO SQR(N)
40 IF N MOD I = 0 THEN P = 0
50 NEXT I
60 IF P = 1 THEN PRINT N; " is prime"
70 IF P = 0 THEN PRINT N; " is not prime"
80 END""",
                },
                "Logo": {
                    "Basic": """📝 LOGO BASIC TEMPLATES

1. Hello World:
PRINT [Hello, World!]

2. Simple Drawing:
FORWARD 100
RIGHT 90
FORWARD 100

3. User Input:
PRINT [What's your name?]
MAKE "NAME READWORD
PRINT (SENTENCE [Hello] :NAME)

4. Repeat Pattern:
REPEAT 4 [FORWARD 100 RIGHT 90]""",
                    "Loops": """🔄 LOGO LOOP TEMPLATES

1. Square with Repeat:
REPEAT 4 [FORWARD 100 RIGHT 90]

2. Nested Repeat:
REPEAT 8 [
  REPEAT 4 [FORWARD 50 RIGHT 90]
  RIGHT 45
]

3. Variable Loop:
MAKE "SIZE 10
REPEAT 20 [
  FORWARD :SIZE
  RIGHT 90
  MAKE "SIZE :SIZE + 5
]""",
                    "Graphics": """🎨 LOGO GRAPHICS TEMPLATES

1. Colorful Square:
SETPENCOLOR "RED"
REPEAT 4 [FORWARD 100 RIGHT 90]

2. Flower Pattern:
REPEAT 36 [
  REPEAT 4 [FORWARD 50 RIGHT 90]
  RIGHT 10
]

3. Spiral:
REPEAT 100 [FORWARD REPCOUNT RIGHT 91]

4. Star:
REPEAT 5 [FORWARD 100 RIGHT 144]

5. Circle:
REPEAT 360 [FORWARD 1 RIGHT 1]""",
                    "Games": """🎮 LOGO GAME TEMPLATES

1. Random Walker:
REPEAT 100 [
  FORWARD 10
  RIGHT RANDOM 360
]

2. Maze Generator:
TO MAZE
  REPEAT 4 [
    FORWARD 50
    IF RANDOM 2 = 0 [RIGHT 90] [LEFT 90]
  ]
END

3. Target Practice:
TO TARGET
  REPEAT 5 [
    SETPENCOLOR RANDOM 8
    CIRCLE 20 + (REPCOUNT * 10)
  ]
END""",
                    "Math": """🔢 LOGO MATH TEMPLATES

1. Multiplication Visualization:
TO TIMES :A :B
  REPEAT :A [
    REPEAT :B [FORWARD 10 RIGHT 90 FORWARD 10 LEFT 90]
    BACK :B * 10
    RIGHT 90
    FORWARD 10
    LEFT 90
  ]
END

2. Fibonacci Spiral:
TO FIBONACCI :N
  IF :N < 2 [FORWARD :N STOP]
  FIBONACCI :N - 1
  RIGHT 90
  FIBONACCI :N - 2
END

3. Geometric Series:
MAKE "SIZE 100
REPEAT 10 [
  FORWARD :SIZE
  RIGHT 90
  MAKE "SIZE :SIZE * 0.8
]""",
                },
                "Python": {
                    "Basic": """📝 PYTHON BASIC TEMPLATES

1. Hello World:
print("Hello, World!")

2. User Input:
name = input("What's your name? ")
print(f"Hello, {name}!")

3. Variables and Math:
a = int(input("First number: "))
b = int(input("Second number: "))
print(f"Sum: {a + b}")

4. Conditional:
number = int(input("Enter a number: "))
if number > 0:
    print("Positive")
elif number < 0:
    print("Negative")
else:
    print("Zero")""",
                    "Loops": """🔄 PYTHON LOOP TEMPLATES

1. For Loop:
for i in range(1, 11):
    print(f"Count: {i}")

2. While Loop:
count = 1
while count <= 5:
    print(count)
    count += 1

3. List Iteration:
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(f"I like {fruit}")

4. Nested Loop:
for i in range(1, 4):
    for j in range(1, 4):
        print(f"{i} x {j} = {i*j}")""",
                    "Graphics": """🎨 PYTHON GRAPHICS TEMPLATES

1. Turtle Square:
import turtle
t = turtle.Turtle()
for i in range(4):
    t.forward(100)
    t.right(90)

2. Colorful Spiral:
import turtle
t = turtle.Turtle()
colors = ["red", "blue", "green", "yellow"]
for i in range(100):
    t.color(colors[i % 4])
    t.forward(i)
    t.right(91)

3. Star Pattern:
import turtle
t = turtle.Turtle()
for i in range(5):
    t.forward(100)
    t.right(144)""",
                    "Games": """🎮 PYTHON GAME TEMPLATES

1. Number Guessing:
import random
number = random.randint(1, 100)
tries = 0
while True:
    guess = int(input("Guess (1-100): "))
    tries += 1
    if guess == number:
        print(f"Correct in {tries} tries!")
        break
    elif guess < number:
        print("Too low!")
    else:
        print("Too high!")

2. Rock Paper Scissors:
import random
choices = ["rock", "paper", "scissors"]
computer = random.choice(choices)
player = input("rock, paper, or scissors? ").lower()
print(f"Computer chose: {computer}")
if player == computer:
    print("Tie!")
elif (player == "rock" and computer == "scissors") or \\
     (player == "paper" and computer == "rock") or \\
     (player == "scissors" and computer == "paper"):
    print("You win!")
else:
    print("You lose!")""",
                    "Math": """🔢 PYTHON MATH TEMPLATES

1. Prime Checker:
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

number = int(input("Enter a number: "))
if is_prime(number):
    print(f"{number} is prime")
else:
    print(f"{number} is not prime")

2. Factorial Calculator:
def factorial(n):
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)

num = int(input("Enter a number: "))
print(f"{num}! = {factorial(num)}")""",
                },
            "TW Pascal": {
                "Basic": """📝 TW PASCAL BASIC TEMPLATES

1. Hello World Program:
program HelloWorld;
begin
  writeln('Hello, World!');
end.

2. User Input Program:
program UserInput;
var
  name: string;
begin
  write('What is your name? ');
  readln(name);
  writeln('Hello, ', name, '!');
end.

3. Variables and Constants:
program VariablesDemo;
const
  PI = 3.14159;
var
  radius, area: real;
begin
  radius := 5.0;
  area := PI * radius * radius;
  writeln('Area of circle: ', area:0:2);
end.

4. Conditional Statements:
program ConditionalDemo;
var
  number: integer;
begin
  write('Enter a number: ');
  readln(number);
  if number > 0 then
    writeln('Positive number')
  else if number < 0 then
    writeln('Negative number')
  else
    writeln('Zero');
end.""",
                "Loops": """🔄 TW PASCAL LOOP TEMPLATES

1. For Loop:
program ForLoopDemo;
var
  i: integer;
begin
  for i := 1 to 10 do
    writeln('Count: ', i);
end.

2. While Loop:
program WhileLoopDemo;
var
  count: integer;
begin
  count := 1;
  while count <= 5 do
  begin
    writeln('Count: ', count);
    count := count + 1;
  end;
end.

3. Repeat Until Loop:
program RepeatLoopDemo;
var
  number: integer;
begin
  repeat
    write('Enter a positive number: ');
    readln(number);
  until number > 0;
  writeln('Thank you for entering: ', number);
end.

4. Nested Loops:
program NestedLoopsDemo;
var
  i, j: integer;
begin
  for i := 1 to 3 do
  begin
    for j := 1 to 3 do
      write(i, ' x ', j, ' = ', i*j, '  ');
    writeln;
  end;
end.""",
                "Graphics": """🎨 TW PASCAL GRAPHICS TEMPLATES

1. Simple Drawing:
program SimpleDrawing;
begin
  // Move turtle forward and turn
  forward(100);
  right(90);
  forward(100);
  right(90);
  forward(100);
  right(90);
  forward(100);
end.

2. Square Pattern:
program SquarePattern;
var
  i: integer;
begin
  for i := 1 to 4 do
  begin
    forward(100);
    right(90);
  end;
end.

3. Colorful Spiral:
program ColorfulSpiral;
var
  i: integer;
begin
  for i := 1 to 100 do
  begin
    setcolor(i mod 8);
    forward(i);
    right(91);
  end;
end.

4. Star Pattern:
program StarPattern;
var
  i: integer;
begin
  for i := 1 to 5 do
  begin
    forward(100);
    right(144);
  end;
end.""",
                "Games": """🎮 TW PASCAL GAME TEMPLATES

1. Number Guessing Game:
program GuessingGame;
var
  number, guess, tries: integer;
begin
  randomize;
  number := random(100) + 1;
  tries := 0;
  writeln('Guess my number (1-100)!');
  repeat
    write('Your guess: ');
    readln(guess);
    tries := tries + 1;
    if guess < number then
      writeln('Too low!')
    else if guess > number then
      writeln('Too high!')
    else
      writeln('Correct in ', tries, ' tries!');
  until guess = number;
end.

2. Simple Calculator:
program Calculator;
var
  a, b, result: real;
  operation: char;
begin
  write('Enter first number: ');
  readln(a);
  write('Enter operation (+, -, *, /): ');
  readln(operation);
  write('Enter second number: ');
  readln(b);
  
  case operation of
    '+': result := a + b;
    '-': result := a - b;
    '*': result := a * b;
    '/': if b <> 0 then result := a / b else result := 0;
  end;
  
  writeln('Result: ', result:0:2);
end.""",
                "Math": """🔢 TW PASCAL MATH TEMPLATES

1. Factorial Calculator:
program FactorialCalc;
function factorial(n: integer): longint;
begin
  if n <= 1 then
    factorial := 1
  else
    factorial := n * factorial(n - 1);
end;

var
  num: integer;
begin
  write('Enter a number: ');
  readln(num);
  writeln(num, '! = ', factorial(num));
end.

2. Prime Number Checker:
program PrimeChecker;
function isPrime(n: integer): boolean;
var
  i: integer;
begin
  isPrime := true;
  if n < 2 then
    isPrime := false
  else
    for i := 2 to trunc(sqrt(n)) do
      if n mod i = 0 then
        isPrime := false;
end;

var
  number: integer;
begin
  write('Enter a number: ');
  readln(number);
  if isPrime(number) then
    writeln(number, ' is prime')
  else
    writeln(number, ' is not prime');
end.

3. Fibonacci Sequence:
program Fibonacci;
function fibonacci(n: integer): longint;
begin
  if n <= 1 then
    fibonacci := n
  else
    fibonacci := fibonacci(n-1) + fibonacci(n-2);
end;

var
  i: integer;
begin
  for i := 0 to 10 do
    write(fibonacci(i), ' ');
  writeln;
end.""",
            },
            "TW Prolog": {
                "Basic": """📝 TW PROLOG BASIC TEMPLATES

1. Hello World Program:
hello_world :- write('Hello, World!'), nl.

2. Simple Facts and Rules:
% Facts
parent(john, mary).
parent(mary, susan).
parent(peter, mary).

% Rules
grandparent(X, Y) :- parent(X, Z), parent(Z, Y).
sibling(X, Y) :- parent(Z, X), parent(Z, Y), X \\= Y.

% Queries:
% ?- grandparent(john, susan).
% ?- sibling(mary, peter).

3. Family Relationships:
% Facts
male(john).
male(peter).
female(mary).
female(susan).

% Rules
father(X, Y) :- male(X), parent(X, Y).
mother(X, Y) :- female(X), parent(X, Y).

4. List Operations:
% Basic list operations
first_element([H|_], H).
last_element([X], X).
last_element([_|T], X) :- last_element(T, X).

% Query: ?- first_element([1,2,3], X).""",
                "Loops": """🔄 TW PROLOG LOOP TEMPLATES

1. Recursive Counting:
count_to(N) :- 
  N > 0, 
  write(N), nl, 
  N1 is N - 1, 
  count_to(N1).
count_to(0) :- write('Done!'), nl.

% Query: ?- count_to(5).

2. List Processing:
print_list([]).
print_list([H|T]) :- 
  write(H), nl, 
  print_list(T).

% Query: ?- print_list([apple, banana, cherry]).

3. Factorial with Recursion:
factorial(0, 1).
factorial(N, F) :- 
  N > 0, 
  N1 is N - 1, 
  factorial(N1, F1), 
  F is N * F1.

% Query: ?- factorial(5, Result).

4. Fibonacci Sequence:
fib(0, 0).
fib(1, 1).
fib(N, F) :- 
  N > 1, 
  N1 is N - 1, 
  N2 is N - 2, 
  fib(N1, F1), 
  fib(N2, F2), 
  F is F1 + F2.

% Query: ?- fib(8, Result).""",
                "Graphics": """🎨 TW PROLOG GRAPHICS TEMPLATES

1. Simple Turtle Graphics:
% Draw a square
draw_square :- 
  forward(100), 
  right(90), 
  draw_square.
draw_square :- !.  % Cut to prevent infinite recursion

% Better version with counter
draw_square(N) :- 
  N > 0, 
  forward(100), 
  right(90), 
  N1 is N - 1, 
  draw_square(N1).
draw_square(0).

% Query: ?- draw_square(4).

2. Spiral Pattern:
draw_spiral(Size) :- 
  Size < 200, 
  forward(Size), 
  right(91), 
  NewSize is Size + 5, 
  draw_spiral(NewSize).
draw_spiral(200).

% Query: ?- draw_spiral(10).

3. Tree Fractal:
draw_tree(0) :- !.
draw_tree(Depth) :- 
  forward(50), 
  right(30), 
  Depth1 is Depth - 1, 
  draw_tree(Depth1), 
  back(50), 
  left(60), 
  draw_tree(Depth1), 
  back(50), 
  right(30).

% Query: ?- draw_tree(5).""",
                "Games": """🎮 TW PROLOG GAME TEMPLATES

1. Number Guessing Game:
guess_number :- 
  random(1, 101, Number), 
  write('Guess my number (1-100): '), nl, 
  play_game(Number, 0).

play_game(Number, Tries) :- 
  read(Guess), 
  (Guess = Number -> 
    NewTries is Tries + 1, 
    write('Correct in '), write(NewTries), write(' tries!'), nl
  ; Guess < Number -> 
    write('Too low! Try again: '), nl, 
    NewTries is Tries + 1, 
    play_game(Number, NewTries)
  ; Guess > Number -> 
    write('Too high! Try again: '), nl, 
    NewTries is Tries + 1, 
    play_game(Number, NewTries)
  ).

2. Rock Paper Scissors:
beat(rock, scissors).
beat(scissors, paper).
beat(paper, rock).

play_rps :- 
  write('Rock, paper, or scissors? '), 
  read(Player), 
  random_member([rock, paper, scissors], Computer), 
  write('Computer chose: '), write(Computer), nl, 
  (beat(Player, Computer) -> 
    write('You win!')
  ; beat(Computer, Player) -> 
    write('Computer wins!')
  ; write('Tie!')
  ), nl.""",
                "Math": """🔢 TW PROLOG MATH TEMPLATES

1. Prime Number Checker:
is_prime(2).
is_prime(N) :- 
  N > 2, 
  N mod 2 \\= 0, 
  \\+ has_factor(N, 3).

has_factor(N, F) :- 
  F * F =< N, 
  (N mod F =:= 0 ; 
   F2 is F + 2, 
   has_factor(N, F2)).

% Query: ?- is_prime(17).

2. Greatest Common Divisor:
gcd(X, 0, X) :- X > 0.
gcd(X, Y, G) :- 
  Y > 0, 
  R is X mod Y, 
  gcd(Y, R, G).

% Query: ?- gcd(48, 18, Result).

3. List Sum:
sum_list([], 0).
sum_list([H|T], Sum) :- 
  sum_list(T, Rest), 
  Sum is H + Rest.

% Query: ?- sum_list([1,2,3,4,5], Sum).

4. Power Function:
power(_, 0, 1).
power(Base, Exp, Result) :- 
  Exp > 0, 
  Exp1 is Exp - 1, 
  power(Base, Exp1, Partial), 
  Result is Base * Partial.

% Query: ?- power(2, 8, Result).""",
            },
            "TW Forth": {
                "Basic": """📝 TW FORTH BASIC TEMPLATES

1. Hello World Program:
: HELLO   ." Hello, World!" CR ;

HELLO

2. Simple Arithmetic:
5 3 + . CR    \\ Prints 8
10 4 - . CR   \\ Prints 6
3 7 * . CR    \\ Prints 21
15 3 / . CR   \\ Prints 5

3. Variables and Constants:
variable COUNTER
10 COUNTER !
COUNTER @ . CR    \\ Prints 10

constant PI 314
PI 100 / . CR     \\ Prints 3 (integer division)

4. Stack Operations:
1 2 3 .S CR    \\ Shows stack: 1 2 3
DUP .S CR      \\ Duplicates top: 1 2 3 3
DROP .S CR     \\ Removes top: 1 2 3
SWAP .S CR     \\ Swaps top two: 1 3 2""",
                "Loops": """🔄 TW FORTH LOOP TEMPLATES

1. DO LOOP:
: COUNT-TO   ( n -- )
  1+ 1 DO I . LOOP CR ;
  
10 COUNT-TO    \\ Prints 1 2 3 4 5 6 7 8 9 10

2. BEGIN UNTIL Loop:
variable N
: COUNT-DOWN   ( n -- )
  BEGIN DUP . 1- DUP 0< UNTIL DROP CR ;
  
5 COUNT-DOWN   \\ Prints 5 4 3 2 1 0

3. BEGIN WHILE REPEAT:
: FACTORIAL   ( n -- n! )
  DUP 1 > IF
    DUP 1- RECURSE *
  THEN ;
  
5 FACTORIAL . CR   \\ Prints 120

4. Nested Loops:
: MULT-TABLE   ( n -- )
  1+ 1 DO
    1+ 1 DO
      I J * 3 .R SPACE
    LOOP CR
  LOOP ;
  
3 MULT-TABLE""",
                "Graphics": """🎨 TW FORTH GRAPHICS TEMPLATES

1. Simple Square:
: SQUARE   ( size -- )
  4 0 DO
    DUP FORWARD 90 RIGHT
  LOOP DROP ;

100 SQUARE

2. Spiral Pattern:
: SPIRAL   ( size max -- )
  BEGIN
    2DUP > WHILE
    DUP FORWARD 91 RIGHT 5 +
  REPEAT 2DROP ;

10 200 SPIRAL

3. Star Pattern:
: STAR   ( size -- )
  5 0 DO
    DUP FORWARD 144 RIGHT
  LOOP DROP ;

100 STAR

4. Colorful Circles:
: COLOR-CIRCLE   ( radius -- )
  8 0 DO
    I SETCOLOR
    DUP CIRCLE
  LOOP DROP ;

50 COLOR-CIRCLE""",
                "Games": """🎮 TW FORTH GAME TEMPLATES

1. Number Guessing Game:
variable SECRET
variable TRIES

: INIT-GAME
  RANDOM 100 MOD 1+ SECRET !
  0 TRIES ! ;

: GUESS   ( n -- )
  1 TRIES +!
  SECRET @ 2DUP = IF
    ." Correct in " TRIES @ . ." tries!" CR
  ELSE
    > IF ." Too high! " ELSE ." Too low! " THEN
    ." Try again: "
  THEN ;

: PLAY-GAME
  INIT-GAME
  BEGIN
    ." Guess (1-100): " QUERY INTERPRET
    GUESS SECRET @ <>
  WHILE REPEAT ;

2. Simple Calculator:
: CALC   ( -- )
  BEGIN
    ." Enter operation (+ - * /) or Q to quit: "
    KEY DUP [CHAR] Q <> WHILE
    CASE
      [CHAR] + OF + ENDOF
      [CHAR] - OF - ENDOF
      [CHAR] * OF * ENDOF
      [CHAR] / OF / ENDOF
    ENDCASE .
  REPEAT DROP ;""",
                "Math": """🔢 TW FORTH MATH TEMPLATES

1. Factorial Calculator:
: FACTORIAL   ( n -- n! )
  DUP 1 > IF
    DUP 1- RECURSE *
  ELSE
    DROP 1
  THEN ;

: FACT-TEST
  ." Enter number: " QUERY INTERPRET
  DUP FACTORIAL
  SWAP ." ! = " . CR ;

2. Prime Number Checker:
: IS-PRIME?   ( n -- flag )
  DUP 2 < IF DROP FALSE EXIT THEN
  DUP 2 MOD 0= IF DROP FALSE EXIT THEN
  TRUE SWAP 3 DO
    DUP I MOD 0= IF DROP FALSE LEAVE THEN
  2 +LOOP ;

: PRIME-TEST
  ." Enter number: " QUERY INTERPRET
  DUP IS-PRIME? IF
    ." is prime" CR
  ELSE
    ." is not prime" CR
  THEN ;

3. Fibonacci Sequence:
: FIB   ( n -- fib )
  DUP 2 < IF EXIT THEN
  DUP 1- RECURSE
  SWAP 2- RECURSE + ;

: FIB-TEST
  10 0 DO I FIB . LOOP CR ;""",
            }

            }

            def update_templates():
                """Update templates based on language and category selection"""
                language = lang_var.get()
                category = category_var.get()

                content = templates.get(language, {}).get(
                    category, "No templates available for this combination."
                )

                templates_text.delete("1.0", tk.END)
                templates_text.insert(tk.END, content)

            # Bind combo box changes
            lang_combo.bind("<<ComboboxSelected>>", lambda e: update_templates())
            category_combo.bind("<<ComboboxSelected>>", lambda e: update_templates())

            # Pack text widget with scrollbars
            text_frame = ttk.Frame(main_frame)
            text_frame.pack(fill=tk.BOTH, expand=True)

            templates_text.pack(in_=text_frame, side=tk.LEFT, fill=tk.BOTH, expand=True)
            templates_scrollbar_y.pack(in_=text_frame, side=tk.RIGHT, fill=tk.Y)
            templates_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=10)

            def copy_template():
                """Copy selected template to clipboard"""
                try:
                    selected_text = templates_text.get(tk.SEL_FIRST, tk.SEL_LAST)
                    if selected_text:
                        templates_window.clipboard_clear()
                        templates_window.clipboard_append(selected_text)
                        messagebox.showinfo("Copied", "Template copied to clipboard!")
                    else:
                        messagebox.showwarning(
                            "No Selection", "Please select text to copy."
                        )
                except tk.TclError:
                    messagebox.showwarning(
                        "No Selection", "Please select text to copy."
                    )

            ttk.Button(button_frame, text="Copy Selected", command=copy_template).pack(
                side=tk.LEFT, padx=(0, 10)
            )
            ttk.Button(
                button_frame, text="Close", command=templates_window.destroy
            ).pack(side=tk.RIGHT)

            # Load initial templates
            update_templates()

            print("📝 Code templates opened")

        except Exception as e:
            messagebox.showerror(
                "Templates Error", f"Failed to open code templates:\n{str(e)}"
            )
            print(f"❌ Templates error: {e}")

    def show_code_analyzer(self):
        """Show code analysis and metrics"""
        try:
            # Create analyzer window
            analyzer_window = tk.Toplevel(self.root)
            analyzer_window.title("🔍 Code Analyzer")
            analyzer_window.geometry("700x500")
            analyzer_window.transient(self.root)
            analyzer_window.grab_set()

            # Apply current theme
            self.apply_theme_to_window(analyzer_window)

            # Create main frame
            main_frame = ttk.Frame(analyzer_window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Title
            title_label = ttk.Label(
                main_frame, text="🔍 Code Analyzer", font=("Arial", 14, "bold")
            )
            title_label.pack(pady=(0, 10))

            # Get current code
            current_code = ""
            if hasattr(self, "multi_tab_editor") and self.multi_tab_editor.tabs:
                current_code = self.multi_tab_editor.get_active_content()

            # Analysis results
            results_text = tk.Text(
                main_frame, wrap=tk.WORD, font=("Consolas", 10), height=25
            )
            results_scrollbar = ttk.Scrollbar(
                main_frame, orient=tk.VERTICAL, command=results_text.yview
            )
            results_text.configure(yscrollcommand=results_scrollbar.set)

            # Perform analysis
            analysis = self.analyze_code(current_code)

            results_text.insert(tk.END, analysis)
            results_text.config(state=tk.DISABLED)

            results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Close button
            close_btn = ttk.Button(
                main_frame, text="Close Analyzer", command=analyzer_window.destroy
            )
            close_btn.pack(pady=10)

            print("🔍 Code analyzer opened")

        except Exception as e:
            messagebox.showerror(
                "Analyzer Error", f"Failed to open code analyzer:\n{str(e)}"
            )
            print(f"❌ Analyzer error: {e}")

    def analyze_code(self, code):
        """Analyze code and return metrics and suggestions"""
        if not code.strip():
            return """🔍 CODE ANALYZER

No code to analyze. Please open a file or write some code in the editor first.

The Code Analyzer can help you with:
• Line count and complexity metrics
• Code quality suggestions
• Performance tips
• Best practice recommendations
• Language-specific advice

Write some code and run the analyzer again!"""

        lines = code.split("\n")
        total_lines = len(lines)
        non_empty_lines = len([line for line in lines if line.strip()])
        comment_lines = len(
            [line for line in lines if line.strip().startswith(("#", "REM", "//"))]
        )

        # Detect language
        language = "Unknown"
        if any(
            line.strip().startswith(("T:", "A:", "J:", "Y:", "N:")) for line in lines
        ):
            language = "TW PILOT"
        elif any(
            line.strip().split()[0].isdigit() if line.strip().split() else False
            for line in lines
        ):
            language = "TW BASIC"
        elif any(
            word in code.upper()
            for word in ["FORWARD", "BACK", "LEFT", "RIGHT", "REPEAT"]
        ):
            language = "TW Logo"
        elif any(word in code for word in ["print(", "def ", "import ", "if __name__"]):
            language = "Python"

        # Calculate complexity
        complexity_keywords = ["IF", "FOR", "WHILE", "REPEAT", "Y:", "N:", "J:"]
        complexity_score = sum(
            1
            for line in lines
            for keyword in complexity_keywords
            if keyword in line.upper()
        )

        # Generate suggestions
        suggestions = []
        if comment_lines == 0 and non_empty_lines > 5:
            suggestions.append("• Add comments to explain your code")
        if total_lines > 50:
            suggestions.append(
                "• Consider breaking long programs into smaller functions"
            )
        if complexity_score > 10:
            suggestions.append(
                "• High complexity detected - consider simplifying logic"
            )
        if language == "PILOT" and "E:" not in code:
            suggestions.append(
                "• Consider adding E: (End) statements for better structure"
            )
        if language == "BASIC" and "END" not in code.upper():
            suggestions.append("• Don't forget to add END statement")
        if not suggestions:
            suggestions.append("• Code looks good! Keep up the great work!")

        return f"""🔍 CODE ANALYSIS RESULTS

📊 BASIC METRICS:
• Total Lines: {total_lines}
• Non-empty Lines: {non_empty_lines}
• Comment Lines: {comment_lines}
• Detected Language: {language}
• Complexity Score: {complexity_score}/10

📈 CODE QUALITY:
• Comment Ratio: {comment_lines/non_empty_lines*100:.1f}% (Good: >10%)
• Code Density: {non_empty_lines/total_lines*100:.1f}% (Good: 60-80%)
• Average Line Length: {sum(len(line) for line in lines)/len(lines):.1f} chars

🎯 SUGGESTIONS:
{chr(10).join(suggestions)}

🔧 LANGUAGE-SPECIFIC TIPS:
{self.get_language_tips(language)}

💡 PERFORMANCE NOTES:
• Avoid deeply nested loops where possible
• Use meaningful variable names
• Keep functions/procedures focused on one task
• Test your code with different inputs

🌟 GOOD PRACTICES:
• Save your work frequently
• Use version control for important projects
• Write code that others (including future you) can understand
• Don't be afraid to refactor and improve

Keep coding and improving! 🚀"""

    def get_language_tips(self, language):
        """Get language-specific coding tips"""
        tips = {
            "TW PILOT": """• Use labels (*LABEL) for better organization
• Match statements (M:) are case-sensitive
• Variables are referenced with $ (e.g., $INPUT)
• Use E: to end program sections cleanly""",
            "TW BASIC": """• Line numbers help organize program flow
• Use meaningful variable names (A$, NAME$, etc.)
• FOR...NEXT loops are very efficient
• DIM arrays before using them""",
            "TW Logo": """• PENUP/PENDOWN control drawing
• Use procedures (TO...END) for reusable code
• REPEAT is more efficient than multiple commands
• Variables start with : (e.g., :SIZE)""",
            "Python": """• Follow PEP 8 style guidelines
• Use list comprehensions for efficiency
• Handle exceptions with try/except
• Use f-strings for string formatting""",
            "Unknown": """• Write clear, readable code
• Use consistent indentation
• Add comments for complex logic
• Test your code thoroughly""",
        }
        return tips.get(language, tips["Unknown"])

    def show_learning_progress(self):
        """Show learning progress and statistics"""
        try:
            # Create progress window
            progress_window = tk.Toplevel(self.root)
            progress_window.title("📊 Learning Progress")
            progress_window.geometry("600x500")
            progress_window.transient(self.root)
            progress_window.grab_set()

            # Apply current theme
            self.apply_theme_to_window(progress_window)

            # Create main frame
            main_frame = ttk.Frame(progress_window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Title
            title_label = ttk.Label(
                main_frame, text="📊 Your Learning Progress", font=("Arial", 14, "bold")
            )
            title_label.pack(pady=(0, 20))

            # Progress content
            progress_text = tk.Text(
                main_frame, wrap=tk.WORD, font=("Arial", 11), height=28
            )
            progress_scrollbar = ttk.Scrollbar(
                main_frame, orient=tk.VERTICAL, command=progress_text.yview
            )
            progress_text.configure(yscrollcommand=progress_scrollbar.set)

            progress_content = """📊 LEARNING PROGRESS TRACKER

Welcome to your personal learning journey with Time_Warp IDE!

🎯 CURRENT LEVEL: Beginner
📈 Overall Progress: 15%
🔥 Learning Streak: 1 day

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 LANGUAGE MASTERY:

🚁 PILOT (1962) - Educational Programming
   Progress: ████░░░░░░ 40%
   Skills Learned:
   ✅ Basic T: (Type) commands
   ✅ A: (Accept) user input
   ✅ Simple program flow
   🔲 Conditional jumps (Y:, N:)
   🔲 Variable manipulation (C:)
   🔲 Advanced matching (M:)
   
   Next Goal: Learn conditional programming with Y: and N:

🔢 BASIC - Classic Programming
   Progress: ██░░░░░░░░ 20%
   Skills Learned:
   ✅ PRINT statements
   ✅ Basic INPUT commands
   🔲 FOR...NEXT loops
   🔲 IF...THEN conditions
   🔲 Variable operations
   🔲 Graphics commands
   
   Next Goal: Master loop structures

🐢 Logo - Turtle Graphics
   Progress: ██████░░░░ 60%
   Skills Learned:
   ✅ FORWARD/BACK movement
   ✅ LEFT/RIGHT turning
   ✅ REPEAT loops
   ✅ Basic shapes (squares, triangles)
   ✅ PENUP/PENDOWN control
   🔲 Procedures (TO...END)
   🔲 Advanced patterns
   🔲 Color manipulation
   
   Next Goal: Create custom procedures

🐍 Python - Modern Programming
   Progress: ███░░░░░░░ 30%
   Skills Learned:
   ✅ print() function
   ✅ input() for user interaction
   ✅ Basic variables
   🔲 Lists and loops
   🔲 Functions (def)
   🔲 File operations
   🔲 Object-oriented programming
   
   Next Goal: Learn about lists and for loops

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 CODING ACHIEVEMENTS:

🏆 Recently Earned:
   ✅ First Steps - Ran your first Time_Warp program
   ✅ Multi-Lingual - Tried 3 different languages
   ✅ Graphics Explorer - Created your first turtle drawing

🎯 Next Achievements (Almost There!):
   📍 Loop Master - Write 5 different loop examples (3/5)
   📍 Code Saver - Save 10 different programs (7/10)
   📍 Theme Explorer - Try all 8 available themes (4/8)

🌟 Future Goals:
   🔲 Problem Solver - Debug 20 programs successfully
   🔲  Pattern Master - Create 10 geometric patterns
   🔲 Game Creator - Build your first interactive game
   🔲 Teaching Helper - Help another student with coding

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 STATISTICS:

⏱️ Time Spent Learning:
   • Today: 45 minutes
   • This Week: 3 hours 20 minutes  
   • Total: 12 hours 15 minutes

📝 Programs Created:
   • PILOT: 8 programs
   • BASIC: 3 programs
   • Logo: 12 programs
   • Python: 5 programs
   • Total: 28 programs

🎨 Creative Projects:
   • Geometric Patterns: 6
   • Text Programs: 8
   • Interactive Programs: 4
   • Games: 2

🔧 Problem Solving:
   • Syntax Errors Fixed: 15
   • Logic Errors Debugged: 7
   • Help Topics Viewed: 12

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 RECOMMENDED NEXT STEPS:

1. 📚 Complete the PILOT conditional programming tutorial
2. 🔄 Practice BASIC loops with the template examples  
3. 🎨 Create a complex Logo pattern using procedures
4. 🐍 Learn Python list operations and for loops
5. 🎮 Try building a simple text-based game

💡 LEARNING TIPS:
• Code a little bit every day to maintain your streak
• Don't be afraid to experiment and make mistakes
• Use the AI Assistant when you're stuck
• Share your creations and get feedback
• Challenge yourself with new programming concepts

🌟 You're doing great! Keep up the excellent work!

Remember: Every expert was once a beginner. Your coding journey is unique and valuable. Celebrate your progress and keep learning! 🚀"""

            progress_text.insert(tk.END, progress_content)
            progress_text.config(state=tk.DISABLED)

            progress_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            progress_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Close button
            close_btn = ttk.Button(
                main_frame, text="Close Progress", command=progress_window.destroy
            )
            close_btn.pack(pady=10)

            print("📊 Learning progress opened")

        except Exception as e:
            messagebox.showerror(
                "Progress Error", f"Failed to open learning progress:\n{str(e)}"
            )
            print(f"❌ Progress error: {e}")

    def show_plugin_manager(self):
        """Show plugin manager with full functionality"""
        try:
            # Create plugin manager window
            pm_window = tk.Toplevel(self.root)
            pm_window.title("🔌 Plugin Manager")
            pm_window.geometry("700x500")
            pm_window.transient(self.root)
            pm_window.grab_set()

            # Apply current theme
            self.apply_theme_to_window(pm_window)

            # Create main frame
            main_frame = ttk.Frame(pm_window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Title
            title_label = ttk.Label(
                main_frame, text="🔌 Plugin Manager", font=("Arial", 16, "bold")
            )
            title_label.pack(pady=(0, 20))

            # Create notebook for different sections
            notebook = ttk.Notebook(main_frame)
            notebook.pack(fill=tk.BOTH, expand=True)

            # Installed Plugins Tab
            installed_frame = ttk.Frame(notebook)
            notebook.add(installed_frame, text="📦 Installed")

            # Plugin list with scrollbar
            plugin_list_frame = ttk.Frame(installed_frame)
            plugin_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Create treeview for plugins
            columns = ("Name", "Version", "Author", "Status", "Description")
            plugin_tree = ttk.Treeview(
                plugin_list_frame, columns=columns, show="headings", height=15
            )

            # Define headings
            plugin_tree.heading("Name", text="Plugin Name")
            plugin_tree.heading("Version", text="Version")
            plugin_tree.heading("Author", text="Author")
            plugin_tree.heading("Status", text="Status")
            plugin_tree.heading("Description", text="Description")

            # Define column widths
            plugin_tree.column("Name", width=150)
            plugin_tree.column("Version", width=80)
            plugin_tree.column("Author", width=100)
            plugin_tree.column("Status", width=80)
            plugin_tree.column("Description", width=250)

            # Add scrollbar
            scrollbar = ttk.Scrollbar(
                plugin_list_frame, orient=tk.VERTICAL, command=plugin_tree.yview
            )
            plugin_tree.configure(yscrollcommand=scrollbar.set)

            plugin_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Load and display plugins
            self.load_plugin_list(plugin_tree)

            # Plugin control buttons
            button_frame = ttk.Frame(installed_frame)
            button_frame.pack(fill=tk.X, padx=10, pady=10)

            def refresh_plugins():
                """Refresh the plugin list"""
                for item in plugin_tree.get_children():
                    plugin_tree.delete(item)
                self.load_plugin_list(plugin_tree)

            def enable_plugin():
                """Enable selected plugin"""
                selection = plugin_tree.selection()
                if not selection:
                    messagebox.showwarning("No Selection", "Please select a plugin to enable.")
                    return

                plugin_name = plugin_tree.item(selection[0])["values"][0]
                if self.enable_plugin(plugin_name):
                    messagebox.showinfo("Success", f"Plugin '{plugin_name}' enabled successfully!")
                    refresh_plugins()
                else:
                    messagebox.showerror("Error", f"Failed to enable plugin '{plugin_name}'.")

            def disable_plugin():
                """Disable selected plugin"""
                selection = plugin_tree.selection()
                if not selection:
                    messagebox.showwarning("No Selection", "Please select a plugin to disable.")
                    return

                plugin_name = plugin_tree.item(selection[0])["values"][0]
                if self.disable_plugin(plugin_name):
                    messagebox.showinfo("Success", f"Plugin '{plugin_name}' disabled successfully!")
                    refresh_plugins()
                else:
                    messagebox.showerror("Error", f"Failed to disable plugin '{plugin_name}'.")

            def show_plugin_details():
                """Show detailed information about selected plugin"""
                selection = plugin_tree.selection()
                if not selection:
                    messagebox.showwarning("No Selection", "Please select a plugin to view details.")
                    return

                plugin_name = plugin_tree.item(selection[0])["values"][0]
                self.show_plugin_details(plugin_name)

            ttk.Button(button_frame, text="🔄 Refresh", command=refresh_plugins).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(button_frame, text="✅ Enable", command=enable_plugin).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(button_frame, text="❌ Disable", command=disable_plugin).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(button_frame, text="ℹ️ Details", command=show_plugin_details).pack(side=tk.LEFT, padx=(0, 10))

            # Plugin Store Tab (placeholder for future)
            store_frame = ttk.Frame(notebook)
            notebook.add(store_frame, text="🛒 Store")

            store_label = ttk.Label(
                store_frame,
                text="🛒 Plugin Store\n\nComing Soon!\n\nBrowse and download plugins from the Time_Warp Plugin Repository.\n\nFeatures:\n• Official plugin collection\n• User-submitted plugins\n• Automatic updates\n• Plugin ratings and reviews",
                justify=tk.CENTER,
                font=("Arial", 12)
            )
            store_label.pack(expand=True)

            # Settings Tab
            settings_frame = ttk.Frame(notebook)
            notebook.add(settings_frame, text="⚙️ Settings")

            settings_label = ttk.Label(
                settings_frame,
                text="🔧 Plugin Settings\n\n• Auto-load enabled plugins on startup\n• Plugin update notifications\n• Security settings for plugin permissions\n• Plugin development mode\n\nThese settings will be available in a future update.",
                justify=tk.LEFT,
                font=("Arial", 11)
            )
            settings_label.pack(anchor=tk.W, padx=20, pady=20)

            # Close button
            close_btn = ttk.Button(
                main_frame, text="Close Plugin Manager", command=pm_window.destroy
            )
            close_btn.pack(pady=10)

            print("🔌 Plugin manager opened")

        except Exception as e:
            messagebox.showerror(
                "Plugin Manager Error",
                f"Failed to open plugin manager:\n{str(e)}",
            )
            print(f"❌ Plugin manager error: {e}")

    def load_plugin_list(self, treeview):
        """Load and display available plugins in the treeview"""
        try:
            import os
            import json

            # Initialize plugin tracking if not exists
            if not hasattr(self, "loaded_plugins"):
                self.loaded_plugins = {}

            # Scan plugins directory
            plugins_dir = os.path.join(os.path.dirname(__file__), "..", "..", "plugins", "plugins")
            if not os.path.exists(plugins_dir):
                plugins_dir = os.path.join(os.path.dirname(__file__), "..", "plugins")

            if os.path.exists(plugins_dir):
                for item in os.listdir(plugins_dir):
                    plugin_path = os.path.join(plugins_dir, item)
                    if os.path.isdir(plugin_path):
                        manifest_path = os.path.join(plugin_path, "manifest.json")

                        if os.path.exists(manifest_path):
                            try:
                                with open(manifest_path, "r") as f:
                                    manifest = json.load(f)

                                plugin_name = manifest.get("name", item)
                                version = manifest.get("version", "1.0.0")
                                author = manifest.get("author", "Unknown")
                                description = manifest.get("description", "No description available")

                                # Check if plugin is loaded
                                status = "Disabled"
                                if plugin_name in self.loaded_plugins:
                                    status = "Enabled"

                                treeview.insert("", tk.END, values=(
                                    plugin_name, version, author, status, description
                                ))

                            except Exception as e:
                                print(f"Error loading plugin {item}: {e}")
                                treeview.insert("", tk.END, values=(
                                    item, "Error", "Unknown", "Error", f"Failed to load: {str(e)}"
                                ))

        except Exception as e:
            print(f"Error scanning plugins: {e}")

    def enable_plugin(self, plugin_name):
        """Enable a plugin by name"""
        try:
            import os
            import json
            import importlib.util

            # Find plugin directory
            plugins_dir = os.path.join(os.path.dirname(__file__), "..", "..", "plugins", "plugins")
            if not os.path.exists(plugins_dir):
                plugins_dir = os.path.join(os.path.dirname(__file__), "..", "plugins")

            plugin_dir = None
            for item in os.listdir(plugins_dir):
                plugin_path = os.path.join(plugins_dir, item)
                if os.path.isdir(plugin_path):
                    manifest_path = os.path.join(plugin_path, "manifest.json")
                    if os.path.exists(manifest_path):
                        with open(manifest_path, "r") as f:
                            manifest = json.load(f)
                        if manifest.get("name") == plugin_name:
                            plugin_dir = plugin_path
                            break

            if not plugin_dir:
                return False

            # Load plugin
            manifest_path = os.path.join(plugin_dir, "manifest.json")
            plugin_file = os.path.join(plugin_dir, "plugin.py")

            if not os.path.exists(plugin_file):
                return False

            # Load manifest
            with open(manifest_path, "r") as f:
                manifest = json.load(f)

            # Import plugin module
            spec = importlib.util.spec_from_file_location("plugin_module", plugin_file)
            plugin_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin_module)

            # Instantiate plugin
            plugin_class = getattr(plugin_module, "TimeWarpPlugin", None)
            if not plugin_class:
                return False

            plugin_instance = plugin_class(self)
            plugin_instance.activate()

            # Track loaded plugin
            self.loaded_plugins[plugin_name] = plugin_instance

            return True

        except Exception as e:
            print(f"Error enabling plugin {plugin_name}: {e}")
            return False

    def disable_plugin(self, plugin_name):
        """Disable a plugin by name"""
        try:
            if plugin_name in self.loaded_plugins:
                plugin_instance = self.loaded_plugins[plugin_name]
                plugin_instance.deactivate()
                del self.loaded_plugins[plugin_name]
                return True
            return False

        except Exception as e:
            print(f"Error disabling plugin {plugin_name}: {e}")
            return False

    def show_plugin_details(self, plugin_name):
        """Show detailed information about a plugin"""
        try:
            # Create details window
            details_window = tk.Toplevel(self.root)
            details_window.title(f"ℹ️ {plugin_name} - Details")
            details_window.geometry("500x400")
            details_window.transient(self.root)
            details_window.grab_set()

            # Apply theme
            self.apply_theme_to_window(details_window)

            main_frame = ttk.Frame(details_window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Title
            title_label = ttk.Label(
                main_frame, text=f"ℹ️ {plugin_name}", font=("Arial", 14, "bold")
            )
            title_label.pack(pady=(0, 20))

            # Plugin info
            if plugin_name in self.loaded_plugins:
                plugin = self.loaded_plugins[plugin_name]
                info = plugin.get_info()
            else:
                # Try to load info from manifest
                info = self.get_plugin_info_from_manifest(plugin_name)

            if info:
                info_text = f"""📦 Plugin Information

Name: {info.get('name', 'Unknown')}
Version: {info.get('version', 'Unknown')}
Author: {info.get('author', 'Unknown')}

📝 Description:
{info.get('description', 'No description available')}

🔧 Features:
{chr(10).join('• ' + feature for feature in info.get('features', ['No features listed']))}

🔐 Permissions:
{chr(10).join('• ' + perm for perm in info.get('permissions', ['No permissions specified']))}

📊 Status: {'Enabled' if plugin_name in getattr(self, 'loaded_plugins', {}) else 'Disabled'}"""

                text_widget = tk.Text(
                    main_frame, wrap=tk.WORD, font=("Consolas", 10), height=20
                )
                scrollbar = ttk.Scrollbar(
                    main_frame, orient=tk.VERTICAL, command=text_widget.yview
                )
                text_widget.configure(yscrollcommand=scrollbar.set)

                text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

                text_widget.insert(tk.END, info_text)
                text_widget.config(state=tk.DISABLED)
            else:
                ttk.Label(main_frame, text="❌ Plugin information not available.").pack()

            # Close button
            ttk.Button(
                main_frame, text="Close", command=details_window.destroy
            ).pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to show plugin details: {str(e)}")

    def get_plugin_info_from_manifest(self, plugin_name):
        """Get plugin info from manifest file"""
        try:
            import os
            import json

            plugins_dir = os.path.join(os.path.dirname(__file__), "..", "..", "plugins", "plugins")
            if not os.path.exists(plugins_dir):
                plugins_dir = os.path.join(os.path.dirname(__file__), "..", "plugins")

            for item in os.listdir(plugins_dir):
                plugin_path = os.path.join(plugins_dir, item)
                if os.path.isdir(plugin_path):
                    manifest_path = os.path.join(plugin_path, "manifest.json")
                    if os.path.exists(manifest_path):
                        with open(manifest_path, "r") as f:
                            manifest = json.load(f)
                        if manifest.get("name") == plugin_name:
                            return {
                                "name": manifest.get("name"),
                                "version": manifest.get("version"),
                                "author": manifest.get("author"),
                                "description": manifest.get("description"),
                                "features": ["Plugin loaded from manifest"],
                                "permissions": manifest.get("permissions", [])
                            }
            return None

        except Exception as e:
            print(f"Error reading plugin manifest: {e}")
            return None

    def show_documentation(self):
        """Show comprehensive documentation"""
        doc_text = """📖 Time_Warp IDE 1.3 - Complete Documentation

⏰ Time_Warp IDE is an educational programming environment that bridges
programming history with modern development through accessible, visual learning.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 SUPPORTED LANGUAGES

1. TW PILOT (Educational Programming)
   • Simple, English-like syntax for beginners
   • Commands: T: (Type), A: (Accept input), Y: (store input), J: (Jump)
   • Example: T: Hello World! A: What is your name? Y: *NAME* T: Nice to meet you, *NAME*

2. TW BASIC (Classic Line-Numbered Programming)
   • Traditional BASIC with line numbers (10, 20, 30...)
   • Commands: PRINT, INPUT, LET, GOTO, IF...THEN, FOR...NEXT
   • Example: 10 PRINT "Hello World!" 20 INPUT "Your name: "; NAME$

3. TW Logo (Turtle Graphics)
   • Visual programming with turtle graphics
   • Commands: FORWARD, BACK, LEFT, RIGHT, PENUP, PENDOWN
   • Example: FORWARD 100 RIGHT 90 FORWARD 100

4. Python (Modern Scripting)
   • Full Python 3 support with syntax highlighting
   • Access to standard libraries and external packages
   • Example: print("Hello from Python!")

5. JavaScript (Web Scripting)
   • Modern JavaScript with Node.js-style execution
   • Example: console.log("Hello from JavaScript!");

6. Perl (Text Processing)
   • Powerful text manipulation and scripting
   • Example: print "Hello from Perl!\\n";

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🖥️ USER INTERFACE FEATURES

📝 Multi-Tab Editor
• Open multiple files simultaneously
• Syntax highlighting for all supported languages
• Line numbers and code folding
• Font customization and themes

🎨 Theme System (8 Beautiful Themes)
• Dark Themes: Dracula, Monokai, Solarized Dark, Ocean
• Light Themes: Spring, Sunset, Candy, Forest
• Live theme switching and preview
• Persistent theme preferences

🖼️ Enhanced Graphics Canvas
• Turtle graphics with modern enhancements
• Zoom, pan, and export capabilities
• Grid overlay and coordinate display
• High-resolution output

📁 File Explorer
• Project navigation and file management
• Drag-and-drop file opening
• Recent files and workspace management

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⌨️ KEYBOARD SHORTCUTS

File Operations:
• Ctrl+N - New file
• Ctrl+O - Open file
• Ctrl+S - Save file
• Ctrl+Shift+S - Save as
• Ctrl+W - Close tab
• Ctrl+Q - Quit

Code Execution:
• F5 - Run code
• Ctrl+F5 - Run with debug output
• F6 - Stop execution

Editing:
• Ctrl+Z - Undo
• Ctrl+Y - Redo
• Ctrl+A - Select all
• Ctrl+F - Find
• Ctrl+H - Replace

View:
• F1 - Quick help
• F11 - Toggle fullscreen
• Ctrl+Plus/Minus - Zoom

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎮 ADVANCED FEATURES

🤖 AI Assistant
• Context-aware code suggestions
• Programming help and explanations
• Code completion and error detection

📚 Tutorial System
• Interactive learning modules
• Step-by-step programming lessons
• Progress tracking and achievements

🎯 Gamification Dashboard
• Achievement system with badges
• Skill progression and levels
• Programming challenges and rewards

🔌 Plugin Architecture
• Extensible plugin system
• Custom language support
• Third-party integrations

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🛠️ DEVELOPMENT FEATURES

🐛 Integrated Debugging
• Breakpoint support
• Variable inspection
• Step-through execution
• Error highlighting and suggestions

📊 Code Analysis
• Syntax checking and validation
• Code quality metrics
• Performance profiling
• Memory usage monitoring

🔧 Settings & Customization
• Editor preferences (fonts, themes, behavior)
• Language-specific settings
• Plugin management
• Export/import configurations

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 INSTALLATION & SETUP

System Requirements:
• Python 3.8 or higher
• tkinter (included with Python)
• pygame (for graphics and multimedia)
• 500MB free disk space

Quick Start:
1. Download from GitHub
2. Run: python timewarp.py
3. Select a language and start coding!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌟 LEARNING RESOURCES

📚 Built-in Tutorials
• Language introductions
• Basic programming concepts
• Graphics and animation
• File I/O and data handling

🎓 Educational Features
• Progressive difficulty levels
• Interactive examples
• Visual feedback and results
• Comprehensive error messages

📖 Documentation
• In-app help system
• Online documentation
• Community forums
• Video tutorials

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔗 CONNECT & CONTRIBUTE

GitHub: https://github.com/James-HoneyBadger/Time_Warp
Issues: Report bugs and request features
Wiki: Detailed guides and tutorials
Discord: Community discussions

License: MIT (Open Source)
Version: 1.3.0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Happy coding through time! ⏰✨"""

        # Create a scrollable documentation window
        doc_window = tk.Toplevel(self.root)
        doc_window.title("📖 Time_Warp IDE Documentation")
        doc_window.geometry("900x700")
        doc_window.resizable(True, True)

        # Create main frame
        main_frame = ttk.Frame(doc_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create text widget with scrollbar
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_widget = tk.Text(
            text_frame,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 10),
            padx=10,
            pady=10,
        )
        text_widget.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)

        # Insert documentation text
        text_widget.insert(tk.END, doc_text)
        text_widget.config(state=tk.DISABLED)  # Make read-only

        # Apply current theme to the documentation window
        try:
            self.apply_theme_to_window(doc_window)
            colors = self.theme_manager.get_colors()
            text_widget.config(
                bg=colors.get("bg_secondary", "#ffffff"),
                fg=colors.get("text_primary", "#000000"),
                insertbackground=colors.get("text_primary", "#000000"),
            )
        except Exception:
            pass

        # Close button
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text="Close", command=doc_window.destroy).pack(
            side=tk.RIGHT
        )

    def show_quick_help(self):
        """Show quick help"""
        help_text = """⏰ Time_Warp IDE 1.3 - Quick Help

🔥 NEW FEATURES:
• File structure reorganization and cleanup
• Enhanced documentation system
• Improved repository organization
• Better maintainability and navigation

⌨️ KEYBOARD SHORTCUTS:
• Ctrl+N - New file
• Ctrl+O - Open file
• Ctrl+S - Save file
• Ctrl+W - Close tab
• F5 - Run code
• F1 - This help

🎯 LANGUAGES SUPPORTED:
• TW PILOT (Educational programming)
• TW BASIC (Classic line-numbered)
• TW Logo (Turtle graphics)
• Python (Modern scripting)
• JavaScript (Web scripting)
• Perl (Text processing)

🚀 Happy coding through time!"""

        messagebox.showinfo("Time_Warp IDE 1.3 - Quick Help", help_text)

    # Theme and settings

    def show_settings(self):
        """Show settings dialog"""
        # Remember original theme for this settings session so we can revert previews
        self._settings_original_theme = self.current_theme
        self._preview_original_theme = None

        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ Time_Warp IDE Settings")
        settings_window.geometry("500x400")
        settings_window.resizable(True, True)

        # Center the window
        settings_window.transient(self.root)
        settings_window.grab_set()

        # Create notebook for different settings categories
        notebook = ttk.Notebook(settings_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Editor Settings Tab
        editor_frame = ttk.Frame(notebook)
        notebook.add(editor_frame, text="📝 Editor")

        # Font settings - initialize from saved config when available
        cfg = getattr(self.theme_manager, "config", {}) or {}

        # Font settings
        font_frame = ttk.LabelFrame(editor_frame, text="Font Settings")
        font_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(font_frame, text="Font Family:").grid(
            row=0, column=0, sticky="w", padx=5, pady=2
        )
        font_default = cfg.get(
            "font_family", cfg.get("editor_settings", {}).get("font_family", "Consolas")
        )
        font_var = tk.StringVar(value=font_default)
        font_combo = ttk.Combobox(
            font_frame,
            textvariable=font_var,
            values=["Consolas", "Monaco", "DejaVu Sans Mono", "Courier New", "Fira Code", "JetBrains Mono", "Source Code Pro", "Roboto Mono", "Cascadia Code", "Hack", "Inconsolata", "Ubuntu Mono"],
        )
        font_combo.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(font_frame, text="Font Size:").grid(
            row=1, column=0, sticky="w", padx=5, pady=2
        )
        size_default = cfg.get(
            "font_size", cfg.get("editor_settings", {}).get("font_size", 11)
        )
        size_var = tk.IntVar(value=size_default)
        size_spin = tk.Spinbox(
            font_frame, from_=8, to=24, textvariable=size_var, width=10
        )
        size_spin.grid(row=1, column=1, padx=5, pady=2)

        # Editor behavior
        behavior_frame = ttk.LabelFrame(editor_frame, text="Editor Behavior")
        behavior_frame.pack(fill=tk.X, padx=10, pady=5)

        # Editor behavior - initialize from config
        editor_cfg = (
            cfg.get("editor_settings", {})
            if isinstance(cfg.get("editor_settings", {}), dict)
            else {}
        )

        line_numbers_var = tk.BooleanVar(value=editor_cfg.get("line_numbers", True))
        tk.Checkbutton(
            behavior_frame, text="Show line numbers", variable=line_numbers_var
        ).pack(anchor="w", padx=5, pady=2)

        auto_indent_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            behavior_frame, text="Auto-indent", variable=auto_indent_var
        ).pack(anchor="w", padx=5, pady=2)

        auto_indent_var.set(editor_cfg.get("auto_indent", True))

        word_wrap_var = tk.BooleanVar(value=editor_cfg.get("word_wrap", False))
        tk.Checkbutton(behavior_frame, text="Word wrap", variable=word_wrap_var).pack(
            anchor="w", padx=5, pady=2
        )

        # Editor tab buttons
        editor_button_frame = tk.Frame(editor_frame)
        editor_button_frame.pack(fill=tk.X, padx=10, pady=5)

        def apply_editor_settings():
            """Apply editor settings to current session without saving"""
            try:
                fam = font_var.get()
                sz = int(size_var.get())
                wrap_mode = tk.WORD if word_wrap_var.get() else tk.NONE

                if hasattr(self, "multi_tab_editor") and self.multi_tab_editor:
                    for tab in self.multi_tab_editor.tabs.values():
                        try:
                            if hasattr(tab, "text_editor"):
                                tab.text_editor.configure(
                                    font=(fam, sz), wrap=wrap_mode
                                )
                            if hasattr(tab, "line_numbers"):
                                if line_numbers_var.get():
                                    try:
                                        tab.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
                                    except Exception:
                                        pass
                                else:
                                    try:
                                        tab.line_numbers.pack_forget()
                                    except Exception:
                                        pass
                        except Exception:
                            pass

                self.update_status("Editor settings applied")
                try:
                    self.show_toast("Editor settings applied")
                except Exception:
                    pass
            except Exception as e:
                print(f"⚠️ Failed to apply editor settings: {e}")
                messagebox.showerror(
                    "Apply Error", f"Failed to apply editor settings: {e}"
                )

        def save_editor_settings():
            """Save editor settings to persistent config"""
            try:
                new_editor_cfg = {
                    "line_numbers": bool(line_numbers_var.get()),
                    "auto_indent": bool(auto_indent_var.get()),
                    "word_wrap": bool(word_wrap_var.get()),
                    "font_family": font_var.get(),
                    "font_size": int(size_var.get()),
                    "tab_size": cfg.get("editor_settings", {}).get("tab_size", 4),
                    "syntax_highlighting": cfg.get("editor_settings", {}).get(
                        "syntax_highlighting", True
                    ),
                }

                updates = {
                    "editor_settings": new_editor_cfg,
                    "font_family": font_var.get(),
                    "font_size": int(size_var.get()),
                }

                ok = self.theme_manager.save_config(updates)
                if not ok:
                    messagebox.showerror(
                        "Save Error",
                        "Failed to write editor settings to disk. Check permissions or disk space.",
                    )
                    return

                self.update_status("Editor settings saved")
                try:
                    self.show_toast("Editor settings saved")
                except Exception:
                    pass
            except Exception as e:
                print(f"⚠️ Failed to save editor settings: {e}")
                messagebox.showerror(
                    "Save Error", f"Failed to save editor settings: {e}"
                )

        tk.Button(
            editor_button_frame, text="Apply", command=apply_editor_settings
        ).pack(side=tk.RIGHT, padx=5)
        tk.Button(editor_button_frame, text="Save", command=save_editor_settings).pack(
            side=tk.RIGHT, padx=5
        )

        # Theme Settings Tab
        theme_frame = ttk.Frame(notebook)
        notebook.add(theme_frame, text="🎨 Themes")

        current_theme_frame = ttk.LabelFrame(theme_frame, text="Current Theme")
        current_theme_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(
            current_theme_frame, text=f"Active Theme: {self.current_theme.title()}"
        ).pack(pady=10)
        # Display config file location for debugging/persistence visibility
        try:
            cfg_path = get_config_file()
            tk.Label(
                current_theme_frame,
                text=f"Config file: {cfg_path}",
                font=("TkDefaultFont", 8),
                fg="#666666",
            ).pack(pady=(0, 6))
        except Exception:
            pass

        theme_list_frame = ttk.LabelFrame(theme_frame, text="Available Themes")
        theme_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create a scrollable frame for theme grid
        theme_canvas = tk.Canvas(theme_list_frame, height=200)
        theme_scrollbar = ttk.Scrollbar(
            theme_list_frame, orient=tk.VERTICAL, command=theme_canvas.yview
        )
        theme_scrollable_frame = ttk.Frame(theme_canvas)

        theme_scrollable_frame.bind(
            "<Configure>",
            lambda e: theme_canvas.configure(scrollregion=theme_canvas.bbox("all")),
        )

        theme_canvas.create_window((0, 0), window=theme_scrollable_frame, anchor="nw")
        theme_canvas.configure(yscrollcommand=theme_scrollbar.set)

        # Pack the canvas and scrollbar
        theme_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        theme_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Dynamically load all available themes and show in a compact grid
        themes = available_themes()
        theme_var = tk.StringVar(value=self.current_theme)

        # Preview toggle - when enabled, clicking a swatch will preview without saving
        preview_var = tk.BooleanVar(value=False)
        preview_chk = tk.Checkbutton(
            theme_frame, text="Preview on click", variable=preview_var
        )
        preview_chk.pack(anchor="w", padx=12, pady=(0, 6))

        def on_theme_select(selected_theme):
            """Handle theme selection"""
            theme_var.set(selected_theme)

            if preview_var.get():
                # Show a temporary preview (do not persist)
                try:
                    self.preview_theme(selected_theme)
                except Exception as e:
                    print(f"⚠️ Preview failed: {e}")
            else:
                # Persist immediately
                try:
                    self.change_theme(selected_theme)
                except Exception as e:
                    print(f"⚠️ Theme apply failed: {e}")

        def create_theme_swatch(theme_name, row, col):
            """Create a compact theme swatch with name underneath"""
            # Frame for this theme
            theme_frame = ttk.Frame(theme_scrollable_frame)
            theme_frame.grid(row=row, column=col, padx=8, pady=8, sticky="n")

            try:
                sw_bg, sw_bg2, sw_accent = get_theme_preview(theme_name)
            except Exception:
                sw_bg, sw_bg2, sw_accent = ("#ffffff", "#cccccc", "#888888")

            # Compact swatch (smaller than before)
            sw = tk.Canvas(theme_frame, width=60, height=40, bd=0, highlightthickness=2)
            sw.create_rectangle(0, 0, 60, 40, fill=sw_bg, outline=sw_bg2)
            sw.create_rectangle(0, 30, 60, 40, fill=sw_accent, outline=sw_accent)

            # Theme name label underneath
            name_label = ttk.Label(
                theme_frame,
                text=theme_name.title(),
                font=("TkDefaultFont", 9),
                wraplength=70,
                justify=tk.CENTER,
            )

            # Radio button for selection
            rb = tk.Radiobutton(theme_frame, variable=theme_var, value=theme_name)

            # Pack components
            sw.pack(pady=(0, 4))
            name_label.pack(pady=(0, 2))
            rb.pack()

            # Bind click events to the swatch
            def on_click(e):
                on_theme_select(theme_name)

            sw.bind("<Button-1>", on_click)
            name_label.bind("<Button-1>", on_click)
            rb.bind("<Button-1>", on_click)

            # Keyboard accessibility
            sw.configure(takefocus=1)
            sw.bind("<Return>", on_click)
            sw.bind("<space>", on_click)
            sw.bind("<FocusIn>", lambda e: sw.configure(highlightbackground=sw_accent))
            sw.bind("<FocusOut>", lambda e: sw.configure(highlightbackground=sw_bg2))

            # Highlight current theme
            if theme_name == self.current_theme:
                sw.configure(highlightbackground=sw_accent, highlightcolor=sw_accent)

        # Arrange themes in a grid (6 columns)
        cols = 6
        for i, theme in enumerate(themes):
            row = i // cols
            col = i % cols
            create_theme_swatch(theme, row, col)

        # I/O controls (export, import, restore defaults)
        io_frame = ttk.Frame(theme_frame)
        io_frame.pack(fill=tk.X, padx=10, pady=(6, 2))

        def export_theme_handler():
            sel = theme_var.get()
            if not sel:
                messagebox.showwarning("Export Theme", "No theme selected to export.")
                return
            fp = filedialog.asksaveasfilename(
                title="Export Theme",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            )
            if not fp:
                return
            ok = self.theme_manager.export_theme(sel, fp)
            if ok:
                messagebox.showinfo("Export Theme", f"Theme '{sel}' exported to {fp}")
            else:
                messagebox.showerror("Export Theme", "Failed to export theme.")

        def import_theme_handler():
            fp = filedialog.askopenfilename(
                title="Import Theme",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            )
            if not fp:
                return
            new_name = self.theme_manager.import_theme_from_file(fp)
            if new_name:
                # Refresh the theme grid to include the new theme
                for child in theme_scrollable_frame.winfo_children():
                    child.destroy()
                themes = available_themes()
                cols = 6
                for i, theme in enumerate(themes):
                    row = i // cols
                    col = i % cols
                    create_theme_swatch(theme, row, col)
                messagebox.showinfo("Import Theme", f"Imported theme as '{new_name}'")
            else:
                messagebox.showerror("Import Theme", "Failed to import theme file.")

        def restore_defaults_handler():
            ok = messagebox.askyesno(
                "Restore Defaults", "Restore default settings and remove custom themes?"
            )
            if not ok:
                return
            if self.theme_manager.restore_defaults():
                # Refresh the theme grid
                for child in theme_scrollable_frame.winfo_children():
                    child.destroy()
                themes = available_themes()
                cols = 6
                for i, theme in enumerate(themes):
                    row = i // cols
                    col = i % cols
                    create_theme_swatch(theme, row, col)
                # Apply default theme
                self.change_theme(self.theme_manager.current_theme)
                messagebox.showinfo("Restore Defaults", "Defaults restored")
            else:
                messagebox.showerror("Restore Defaults", "Failed to restore defaults")

        ttk.Button(io_frame, text="Export Theme", command=export_theme_handler).pack(
            side=tk.LEFT
        )
        ttk.Button(io_frame, text="Import Theme", command=import_theme_handler).pack(
            side=tk.LEFT, padx=6
        )
        ttk.Button(
            io_frame, text="Restore Defaults", command=restore_defaults_handler
        ).pack(side=tk.RIGHT)

        # Theme tab buttons
        theme_button_frame = tk.Frame(theme_frame)
        theme_button_frame.pack(fill=tk.X, padx=10, pady=5)

        def apply_theme_settings():
            """Apply selected theme to current session without saving"""
            try:
                sel = theme_var.get()
                if sel:
                    self.preview_theme(sel)
                    self.update_status(f"Theme '{sel}' applied")
                    try:
                        self.show_toast(f"Theme '{sel}' applied")
                    except Exception:
                        pass
            except Exception as e:
                print(f"⚠️ Failed to apply theme: {e}")
                messagebox.showerror("Apply Error", f"Failed to apply theme: {e}")

        def save_theme_settings():
            """Save selected theme to persistent config"""
            try:
                sel = theme_var.get()
                if sel:
                    self.change_theme(sel)
                    self.update_status(f"Theme '{sel}' saved")
                    try:
                        self.show_toast(f"Theme '{sel}' saved")
                    except Exception:
                        pass
            except Exception as e:
                print(f"⚠️ Failed to save theme: {e}")
                messagebox.showerror("Save Error", f"Failed to save theme: {e}")

        tk.Button(theme_button_frame, text="Apply", command=apply_theme_settings).pack(
            side=tk.RIGHT, padx=5
        )
        tk.Button(theme_button_frame, text="Save", command=save_theme_settings).pack(
            side=tk.RIGHT, padx=5
        )

        # General Settings Tab
        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text="⚙️ General")

        startup_frame = ttk.LabelFrame(general_frame, text="Startup Options")
        startup_frame.pack(fill=tk.X, padx=10, pady=5)

        remember_tabs_var = tk.BooleanVar(value=cfg.get("remember_tabs", True))
        tk.Checkbutton(
            startup_frame, text="Remember open tabs", variable=remember_tabs_var
        ).pack(anchor="w", padx=5, pady=2)

        auto_save_var = tk.BooleanVar(value=cfg.get("auto_save", False))
        tk.Checkbutton(
            startup_frame, text="Auto-save files", variable=auto_save_var
        ).pack(anchor="w", padx=5, pady=2)

        # General tab buttons
        general_button_frame = tk.Frame(general_frame)
        general_button_frame.pack(fill=tk.X, padx=10, pady=5)

        def apply_general_settings():
            """Apply general settings to current session without saving"""
            try:
                self.remember_tabs = bool(remember_tabs_var.get())
                self.auto_save = bool(auto_save_var.get())
                self.update_status("General settings applied")
                try:
                    self.show_toast("General settings applied")
                except Exception:
                    pass
            except Exception as e:
                print(f"⚠️ Failed to apply general settings: {e}")
                messagebox.showerror(
                    "Apply Error", f"Failed to apply general settings: {e}"
                )

        def save_general_settings():
            """Save general settings to persistent config"""
            try:
                updates = {
                    "remember_tabs": bool(remember_tabs_var.get()),
                    "auto_save": bool(auto_save_var.get()),
                }

                ok = self.theme_manager.save_config(updates)
                if not ok:
                    messagebox.showerror(
                        "Save Error",
                        "Failed to write general settings to disk. Check permissions or disk space.",
                    )
                    return

                # Apply to instance
                self.remember_tabs = bool(remember_tabs_var.get())
                self.auto_save = bool(auto_save_var.get())

                self.update_status("General settings saved")
                try:
                    self.show_toast("General settings saved")
                except Exception:
                    pass
            except Exception as e:
                print(f"⚠️ Failed to save general settings: {e}")
                messagebox.showerror(
                    "Save Error", f"Failed to save general settings: {e}"
                )

        tk.Button(
            general_button_frame, text="Apply", command=apply_general_settings
        ).pack(side=tk.RIGHT, padx=5)
        tk.Button(
            general_button_frame, text="Save", command=save_general_settings
        ).pack(side=tk.RIGHT, padx=5)

        # Button frame
        button_frame = tk.Frame(settings_window)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        def apply_settings():
            # Persist the selected theme and other settings, then apply them.
            try:
                # --- Theme handling ---
                try:
                    sel = theme_var.get()
                    if sel:
                        self.change_theme(sel)
                except Exception as e:
                    print(f"⚠️ Failed to apply selected theme: {e}")

                # --- Editor and general settings ---
                new_editor_cfg = {
                    "line_numbers": bool(line_numbers_var.get()),
                    "auto_indent": bool(auto_indent_var.get()),
                    "word_wrap": bool(word_wrap_var.get()),
                    "font_family": font_var.get(),
                    "font_size": int(size_var.get()),
                    "tab_size": cfg.get("editor_settings", {}).get("tab_size", 4),
                    "syntax_highlighting": cfg.get("editor_settings", {}).get(
                        "syntax_highlighting", True
                    ),
                }

                updates = {
                    "editor_settings": new_editor_cfg,
                    "font_family": font_var.get(),
                    "font_size": int(size_var.get()),
                    "remember_tabs": bool(remember_tabs_var.get()),
                    "auto_save": bool(auto_save_var.get()),
                }

                # Save to persistent config (atomic, returns bool)
                try:
                    ok = self.theme_manager.save_config(updates)
                    if not ok:
                        messagebox.showerror(
                            "Save Error",
                            "Failed to write settings to disk. Check permissions or disk space.",
                        )
                        return
                except Exception as e:
                    print(f"⚠️ Failed to save settings: {e}")
                    messagebox.showerror(
                        "Save Error",
                        f"Failed to write settings to disk: {e}",
                    )
                    return

                # Apply changes immediately to editor widgets
                try:
                    fam = font_var.get()
                    sz = int(size_var.get())
                    wrap_mode = tk.WORD if word_wrap_var.get() else tk.NONE

                    if hasattr(self, "multi_tab_editor") and self.multi_tab_editor:
                        for tab in self.multi_tab_editor.tabs.values():
                            try:
                                if hasattr(tab, "text_editor"):
                                    tab.text_editor.configure(
                                        font=(fam, sz), wrap=wrap_mode
                                    )
                                if hasattr(tab, "line_numbers"):
                                    if line_numbers_var.get():
                                        try:
                                            tab.line_numbers.pack(
                                                side=tk.LEFT, fill=tk.Y
                                            )
                                        except Exception:
                                            pass
                                    else:
                                        try:
                                            tab.line_numbers.pack_forget()
                                        except Exception:
                                            pass
                            except Exception:
                                pass

                except Exception as e:
                    print(f"⚠️ Failed to apply editor settings live: {e}")

                self.update_status("Settings applied")
                # Briefly notify the user that settings were saved
                try:
                    self.show_toast("Settings saved")
                except Exception:
                    pass
                # Clear any preview marker since selection is now persisted
                try:
                    self._preview_original_theme = None
                except Exception:
                    pass
                settings_window.destroy()

            except Exception as e:
                # Ensure unexpected errors don't close the settings dialog silently
                print(f"⚠️ apply_settings outer error: {e}")
                try:
                    messagebox.showerror(
                        "Settings Error", f"Error applying settings: {e}"
                    )
                except Exception:
                    pass

        def cancel_settings():
            # If a preview was applied during this settings session, always revert
            # to the original theme regardless of the current state of the preview checkbox.
            try:
                if getattr(self, "_preview_original_theme", None):
                    try:
                        self.revert_preview()
                    except Exception as e:
                        print(f"⚠️ Failed to revert preview on cancel: {e}")
            finally:
                settings_window.destroy()

        # Buttons
        tk.Button(button_frame, text="Apply", command=apply_settings).pack(
            side=tk.RIGHT, padx=5
        )
        tk.Button(button_frame, text="Cancel", command=cancel_settings).pack(
            side=tk.RIGHT, padx=5
        )
        tk.Button(button_frame, text="OK", command=apply_settings).pack(
            side=tk.RIGHT, padx=5
        )

    def change_theme(self, theme_name):
        """Change to a different theme"""
        try:
            print(f"🎨 Changing theme to: {theme_name}")
            # Delegate to ThemeManager which persists and updates colors
            try:
                self.theme_manager.set_theme(theme_name)
            except Exception:
                # Fallback to local assignment
                self.current_theme = theme_name
                try:
                    cfg = load_config()
                    cfg["current_theme"] = theme_name
                    save_config(cfg)
                except Exception:
                    pass

            # Refresh visuals
            self.apply_theme()

            print(f"✅ Theme changed to: {theme_name}")
        except Exception as e:
            print(f"⚠️ Theme change error: {e}")

    def preview_theme(self, theme_name):
        """Temporarily apply a theme for preview purposes without saving to config."""
        try:
            # Save original theme if not already saved
            if getattr(self, "_preview_original_theme", None) is None:
                self._preview_original_theme = self.current_theme

            # Apply theme visually but do not save to config
            colors = self.theme_manager.get_colors(theme_name)
            self.current_theme = theme_name
            # Apply to root and components
            self.root.configure(bg=colors.get("bg_primary", "#000000"))
            try:
                self.theme_manager.apply_theme(self.root, theme_name)
            except Exception:
                pass

            # Apply to editor and output if present
            if hasattr(self, "multi_tab_editor"):
                try:
                    self.multi_tab_editor.apply_theme(colors)
                except Exception:
                    pass

            if hasattr(self, "output_text"):
                try:
                    self.output_text.configure(
                        bg=colors.get("bg_secondary", colors.get("bg_primary")),
                        fg=colors.get("text_primary", "#000"),
                        insertbackground=colors.get("text_primary", "#000"),
                    )
                except Exception:
                    pass

        except Exception as e:
            print(f"⚠️ Preview theme error: {e}")

    def revert_preview(self):
        """Revert any temporary preview to the original theme saved at start of preview."""
        try:
            original = getattr(self, "_preview_original_theme", None)
            if original:
                self.change_theme(original)
                self._preview_original_theme = None
        except Exception as e:
            print(f"⚠️ Revert preview error: {e}")

    def apply_theme(self):
        """Apply current theme consistently to all components"""
        try:
            print(f"🎨 Applying theme: {self.current_theme}")

            # Get theme colors
            colors = self.theme_manager.get_colors()

            # Apply theme to root window first
            self.root.configure(bg=colors["bg_primary"])

            # Apply TTK styles
            self.theme_manager.apply_theme(self.root, self.current_theme)

            # Apply theme consistently to all frames and panels
            frame_bg = colors.get("bg_secondary", colors["bg_primary"])

            # Apply theme to main container and panels
            if hasattr(self, "main_container"):
                try:
                    self.main_container.configure(style="Themed.TPanedWindow")
                except:
                    pass

            # Ensure editor panel uses consistent colors
            if hasattr(self, "editor_panel"):
                try:
                    self.editor_panel.configure(style="Themed.TFrame")
                    # Note: ttk widgets use styles, not direct bg configuration
                except Exception as e:
                    print(f"Warning: Could not theme editor panel: {e}")

            # Ensure graphics panel uses consistent colors
            if hasattr(self, "graphics_output_panel"):
                try:
                    self.graphics_output_panel.configure(style="Themed.TFrame")
                    # Note: ttk widgets use styles, not direct bg configuration
                except Exception as e:
                    print(f"Warning: Could not theme graphics panel: {e}")

            # Apply theme to multi-tab editor with proper error handling
            if hasattr(self, "multi_tab_editor"):
                try:
                    self.multi_tab_editor.apply_theme(colors)
                    print("✅ Multi-tab editor theme applied successfully")
                except Exception as e:
                    print(f"Warning: Could not apply theme to multi-tab editor: {e}")

            # Apply theme to output text
            if hasattr(self, "output_text"):
                try:
                    self.output_text.configure(
                        bg=colors.get("bg_secondary", colors["bg_primary"]),
                        fg=colors.get("text_primary", "#000000"),
                        insertbackground=colors.get("text_primary", "#000000"),
                    )
                except:
                    pass

            # Apply theme to status bar
            if hasattr(self, "status_label"):
                self.status_label.configure(
                    background=colors["bg_secondary"],
                    foreground=colors["text_primary"],
                    relief="flat",
                )

            if hasattr(self, "language_label"):
                # Use high contrast colors for language label readability
                if self.current_theme in ["forest", "spring"]:
                    # Light themes: use dark background with light text
                    label_bg = colors["text_primary"]  # Dark green
                    label_fg = colors["bg_primary"]  # Light background
                elif self.current_theme in ["sunset", "candy"]:
                    # Light themes with colorful backgrounds: use dark text on light background
                    label_bg = colors["bg_secondary"]  # Light background
                    label_fg = colors["text_primary"]  # Dark text
                else:
                    # Dark themes: use accent with light text
                    label_bg = colors["accent"]
                    label_fg = colors["bg_primary"]  # Light background color for text

                self.language_label.configure(
                    background=label_bg, foreground=label_fg, relief="flat"
                )

            # Apply theme to enhanced graphics canvas
            if hasattr(self, "enhanced_graphics") and ENHANCED_GRAPHICS_AVAILABLE:
                self.enhanced_graphics.apply_theme(colors)
            elif hasattr(self, "basic_canvas"):
                self.theme_manager.apply_canvas_theme(self.basic_canvas)

            # Apply theme to output text areas
            if hasattr(self, "output_text"):
                self.theme_manager.apply_text_widget_theme(self.output_text)

            # Recursively apply theme to all widgets (ensures canvases get themed)
            try:
                self.theme_manager.apply_widget_theme(self.root)
            except Exception:
                pass

        except Exception as e:
            print(f"⚠️ Theme application error: {e}")

    def apply_theme_to_window(self, window):
        """Apply current theme to a specific window"""
        try:
            # Initialize theme manager if not already done
            if not hasattr(self, "theme_manager"):
                from .utils.theme import ThemeManager

                self.theme_manager = ThemeManager()

            # Apply theme to the window
            self.theme_manager.apply_theme(window, self.current_theme)
            colors = self.theme_manager.get_colors()

            # Apply basic styling to the window
            window.configure(bg=colors["bg_primary"])

        except Exception as e:
            print(f"⚠️ Window theme application error: {e}")

    def show_toast(self, message, duration=1800):
        """Show a small transient toast-like notification near the bottom of the main window."""
        try:
            toast = tk.Toplevel(self.root)
            toast.overrideredirect(True)
            toast.attributes("-topmost", True)
            toast.configure(bg="#333333")

            label = tk.Label(
                toast,
                text=message,
                bg="#333333",
                fg="#ffffff",
                padx=10,
                pady=6,
                font=("TkDefaultFont", 10),
            )
            label.pack()

            # Position near bottom-right of main window
            self.root.update_idletasks()
            x = (
                self.root.winfo_rootx()
                + self.root.winfo_width()
                - toast.winfo_reqwidth()
                - 20
            )
            y = (
                self.root.winfo_rooty()
                + self.root.winfo_height()
                - toast.winfo_reqheight()
                - 40
            )
            toast.geometry(f"+{x}+{y}")

            # Auto-destroy after duration milliseconds
            toast.after(duration, toast.destroy)
        except Exception:
            pass

    def load_plugins(self):
        """Load essential plugins"""
        try:
            print("🔌 Loading plugins...")
            # TODO: Load plugins for 1.1
        except Exception as e:
            print(f"⚠️ Plugin loading error: {e}")

    def open_theme_selector(self):
        """Open a modern theme selector dialog with previews."""
        try:
            dlg = tk.Toplevel(self.root)
            dlg.title("Theme Settings")
            dlg.geometry("600x400")
            dlg.transient(self.root)
            dlg.grab_set()

            info = ttk.Label(
                dlg, text="Choose a theme:", font=("TkDefaultFont", 12, "bold")
            )
            info.pack(pady=8)

            # Create a scrollable frame for theme swatches
            canvas = tk.Canvas(dlg, height=300)
            scrollbar = ttk.Scrollbar(dlg, orient=tk.VERTICAL, command=canvas.yview)
            scroll_frame = ttk.Frame(canvas)

            scroll_frame_id = canvas.create_window(
                (0, 0), window=scroll_frame, anchor="nw"
            )
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Populate themes
            row = 0
            col = 0
            for theme_name in available_themes():
                sw_bg, sw_bg2, sw_accent = get_theme_preview(theme_name)

                sw_frame = ttk.Frame(scroll_frame, relief=tk.RIDGE, borderwidth=1)
                sw_frame.grid(row=row, column=col, padx=8, pady=8, sticky="n")

                sw_canvas = tk.Canvas(
                    sw_frame, width=120, height=60, bd=0, highlightthickness=0
                )
                sw_canvas.pack(padx=4, pady=4)
                sw_canvas.create_rectangle(0, 0, 120, 60, fill=sw_bg, outline=sw_bg2)
                sw_canvas.create_rectangle(
                    4, 36, 116, 56, fill=sw_accent, outline=sw_accent
                )

                label = ttk.Label(sw_frame, text=theme_name.title(), width=14)
                label.pack(pady=(2, 4))

                def make_callback(name):
                    return lambda: (self.change_theme(name), dlg.destroy())

                btn = ttk.Button(
                    sw_frame, text="Apply", command=make_callback(theme_name)
                )
                # Make the swatch itself keyboard accessible
                sw_canvas.configure(takefocus=1)
                sw_canvas.bind("<Return>", lambda e, n=theme_name: make_callback(n)())
                sw_canvas.bind("<space>", lambda e, n=theme_name: make_callback(n)())
                btn.pack(pady=(0, 6))

                col += 1
                if col >= 4:
                    col = 0
                    row += 1

            # Update scroll region
            def _on_frame_config(event):
                canvas.configure(scrollregion=canvas.bbox("all"))

            scroll_frame.bind("<Configure>", _on_frame_config)

        except Exception as e:
            print(f"⚠️ Theme selector error: {e}")

    # Gamification callbacks
    def show_achievement_notification(self, achievement):
        """Show achievement notification"""
        # TODO: Implement achievement notifications
        pass

    def show_level_up_notification(self, old_level, new_level):
        """Show level up notification"""
        # TODO: Implement level up notifications
        pass

    def update_stats_display(self, stats):
        """Update stats display"""
        # TODO: Implement stats display
        pass

    def quit_app(self):
        """Quit application with save confirmation"""
        # Check for unsaved changes
        unsaved_count = 0
        for tab in self.multi_tab_editor.tabs.values():
            if tab.is_modified:
                unsaved_count += 1

        if unsaved_count > 0:
            result = messagebox.askyesnocancel(
                "Unsaved Changes",
                f"You have {unsaved_count} unsaved file(s). Save before closing?",
            )
            if result is None:  # Cancel
                return
            elif result:  # Yes, save all
                self.save_all_files()

        self.root.quit()


def main():
    """Main application entry point - Time_Warp IDE"""
    print("🚀 Starting Time_Warp IDE 1.2...")
    print("⏰ Enhanced Educational Programming Environment")
    print("🔥 New: Multi-tab editor, Enhanced graphics, Theme selector!")

    try:
        print("🔧 Initializing Time_Warp IDE...")
        app = Time_WarpIDE()

        print("🔧 Starting main event loop...")
        # Add a check to ensure the window is still valid before starting mainloop
        if app.root.winfo_exists():
            app.root.mainloop()
            print("👋 Time_Warp IDE session ended. Happy coding!")
        else:
            print("❌ Window was destroyed during initialization")

    except KeyboardInterrupt:
        print("\n⚠️ User interrupted - Time_Warp IDE shutting down gracefully...")
    except Exception as e:
        print(f"❌ Critical error during startup: {e}")
        import traceback

        traceback.print_exc()

        # Try to keep a minimal window open for debugging
        try:
            import tkinter as tk

            root = tk.Tk()
            root.title("Time_Warp IDE - Error")
            root.geometry("500x300")

            error_label = tk.Label(
                root,
                text=f"Time_Warp IDE encountered an error:\n{str(e)}\n\nCheck console for details.",
                wraplength=450,
                justify=tk.CENTER,
                fg="red",
            )
            error_label.pack(pady=50)

            tk.Button(root, text="Close", command=root.quit).pack(pady=20)
            root.mainloop()
        except:
            pass


if __name__ == "__main__":
    main()
