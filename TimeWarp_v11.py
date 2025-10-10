#!/usr/bin/env python3
"""
TimeWarp IDE v1.1 - Enhanced Multi-Tab Editor
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
from tools.theme import load_config, save_config, ThemeManager

# Import core components
try:
    from core.interpreter import TimeWarpInterpreter
    from plugins import PluginManager
    CORE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Core components not available: {e}")
    CORE_AVAILABLE = False

# Import GUI components
try:
    from gui.components.multi_tab_editor import MultiTabEditor
    from gui.components.enhanced_graphics_canvas import EnhancedGraphicsCanvas
    ENHANCED_GRAPHICS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Enhanced components not available: {e}")
    ENHANCED_GRAPHICS_AVAILABLE = False
from core.enhanced_error_handler import EnhancedErrorHandler, ErrorHighlighter

# Feature modules
from core.features.tutorial_system import TutorialSystem
from core.features.ai_assistant import AICodeAssistant
from core.features.gamification import GamificationSystem


class TimeWarpIDE_v11:
    """
    TimeWarp IDE v1.1 - Enhanced Educational Programming Environment
    New features: Multi-tab editor, File explorer, Enhanced graphics, Better errors
    """

    def __init__(self):
        """Initialize TimeWarp IDE v1.1"""
        print("🚀 Starting TimeWarp IDE v1.1...")
        print("⏰ Enhanced Educational Programming Environment")
        print("🔥 New: Multi-tab editor, Enhanced graphics, Theme selector!")
        
        # Initialize main window
        self.root = tk.Tk()
        self._setup_window()

        # Initialize core systems
        self.theme_manager = ThemeManager()
        self.current_theme = "sunset"  # Default theme
        
        self.plugin_manager = PluginManager(self)
        
        # Initialize interpreter
        self.interpreter = TimeWarpInterpreter()
        
        # Initialize execution tracking
        self.execution_thread = None
        self.stop_execution_flag = False
        
        # Setup UI
        self.setup_ui()
        
        # Initialize other components
        self.load_theme_config()
        
        # Setup keyboard shortcuts
        self.setup_keyboard_shortcuts()
        
        # Initialize features
        self.init_features()
        
        # Apply initial theme
        self.apply_theme()
        
        # Load plugins
        self.load_plugins()
        
        print("🚀 TimeWarp IDE v1.1 - Clean two-panel layout ready!")
        
        # Handle any initialization errors gracefully

    def load_theme_config(self):
        """Load theme configuration"""
        try:
            self.current_theme = self.theme_manager.config.get("current_theme", "dracula")
            print(f"🎨 Loaded theme: {self.current_theme}")
        except Exception as e:
            print(f"⚠️ Theme loading error: {e}")
            self.current_theme = "dracula"

    def _setup_window(self):
        """Setup main window properties"""
        # Basic window setup is now done in setup_ui
        pass

    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts - delegates to setup_keybindings"""
        self.setup_keybindings()

    def init_features(self):
        """Initialize additional features"""
        try:
            # Initialize error handler
            self.error_handler = EnhancedErrorHandler()
            
            # Simplified feature initialization for v1.1
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
        except:
            self.main_container.add(self.editor_panel, weight=3)

        # Right panel: Graphics and Output
        self.graphics_output_panel = ttk.Frame(self.main_container, width=400)
        try:
            self.main_container.add(self.graphics_output_panel, weight=1, minsize=350)
        except:
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
        file_menu.add_command(label="📄 New File", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="📂 Open File", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="📁 Open Folder", command=self.open_folder, accelerator="Ctrl+Shift+O")
        file_menu.add_separator()
        file_menu.add_command(label="💾 Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="💾 Save As", command=self.save_as_file, accelerator="Ctrl+Shift+S")
        file_menu.add_command(label="💾 Save All", command=self.save_all_files, accelerator="Ctrl+Alt+S")
        file_menu.add_separator()
        file_menu.add_command(label="❌ Close Tab", command=self.close_current_tab, accelerator="Ctrl+W")
        file_menu.add_command(label="🚪 Exit", command=self.quit_app, accelerator="Ctrl+Q")

        # Edit menu
        edit_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="🔍 Find", command=self.find_text, accelerator="Ctrl+F")
        edit_menu.add_command(label="🔁 Replace", command=self.replace_text, accelerator="Ctrl+H")
        edit_menu.add_separator()
        edit_menu.add_command(label="↩️ Undo", accelerator="Ctrl+Z")
        edit_menu.add_command(label="↪️ Redo", accelerator="Ctrl+Y")

        # View menu (NEW)
        view_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="🔍 Zoom In", command=self.zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="🔍 Zoom Out", command=self.zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="🔍 Reset Zoom", command=self.reset_zoom, accelerator="Ctrl+0")
        view_menu.add_separator()
        view_menu.add_command(label="🎨 Toggle Graphics Panel", command=self.toggle_graphics_panel)
        view_menu.add_separator()
        
        # Theme selector submenu
        theme_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="🎨 Themes", menu=theme_menu)
        
        # Dark themes
        theme_menu.add_command(label="🌙 Dracula", command=lambda: self.change_theme("dracula"))
        theme_menu.add_command(label="🌙 Monokai", command=lambda: self.change_theme("monokai"))
        theme_menu.add_command(label="🌙 Solarized Dark", command=lambda: self.change_theme("solarized"))
        theme_menu.add_command(label="🌙 Ocean", command=lambda: self.change_theme("ocean"))
        theme_menu.add_separator()
        
        # Light themes
        theme_menu.add_command(label="☀️ Spring", command=lambda: self.change_theme("spring"))
        theme_menu.add_command(label="☀️ Sunset", command=lambda: self.change_theme("sunset"))
        theme_menu.add_command(label="☀️ Candy", command=lambda: self.change_theme("candy"))
        theme_menu.add_command(label="☀️ Forest", command=lambda: self.change_theme("forest"))

        # Run menu  
        run_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="▶️ Run Code", command=self.run_code, accelerator="F5")
        run_menu.add_command(label="⏹️ Stop", command=self.stop_execution, accelerator="Shift+F5")
        run_menu.add_separator()
        run_menu.add_command(label="🗑️ Clear Output", command=self.clear_output)
        run_menu.add_command(label="🗑️ Clear Graphics", command=self.clear_graphics)

        # Tools menu
        tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="⚙️ Settings", command=self.show_settings)
        tools_menu.add_command(label="🔌 Plugin Manager", command=self.show_plugin_manager)

        # Features menu
        features_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Features", menu=features_menu)
        features_menu.add_command(label="📚 Tutorial System", command=self.show_tutorial_system)
        features_menu.add_command(label="🤖 AI Assistant", command=self.show_ai_assistant)
        features_menu.add_command(label="🎮 Gamification", command=self.show_gamification_dashboard)
        features_menu.add_separator()
        features_menu.add_command(label="📝 Code Templates", command=self.show_code_templates)
        features_menu.add_command(label="🔍 Code Analyzer", command=self.show_code_analyzer)
        features_menu.add_command(label="📊 Learning Progress", command=self.show_learning_progress)

        # Help menu
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="📖 Documentation", command=self.show_documentation)
        help_menu.add_command(label="🆘 Quick Help", command=self.show_quick_help, accelerator="F1")
        help_menu.add_separator()
        help_menu.add_command(label="ℹ️ About TimeWarp IDE", command=self.show_about)

    def setup_multi_tab_editor(self):
        """Setup multi-tab code editor"""
        # Editor with status bar
        editor_frame = ttk.Frame(self.editor_panel)
        editor_frame.pack(fill=tk.BOTH, expand=True)

        # Multi-tab editor
        self.multi_tab_editor = MultiTabEditor(editor_frame)

        # Status bar for editor
        status_frame = ttk.Frame(editor_frame)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_label = ttk.Label(
            status_frame, 
            text="Ready", 
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        # Language indicator
        self.language_label = ttk.Label(
            status_frame,
            text="PILOT",
            relief=tk.SUNKEN,
            width=10
        )
        self.language_label.pack(side=tk.RIGHT, padx=2)

    def setup_output_graphics_panel(self):
        """Setup right panel with output and graphics"""
        # Create notebook for output and graphics
        self.graphics_notebook = ttk.Notebook(self.graphics_output_panel)
        self.graphics_notebook.pack(fill=tk.BOTH, expand=True)

        # Output tab
        output_frame = ttk.Frame(self.graphics_notebook)
        self.graphics_notebook.add(output_frame, text="📺 Output")

        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            state=tk.DISABLED,
            wrap=tk.WORD,
            font=('Consolas', 10)
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Graphics tab
        graphics_frame = ttk.Frame(self.graphics_notebook)
        self.graphics_notebook.add(graphics_frame, text="🎨 Graphics")

        # Enhanced graphics canvas
        if ENHANCED_GRAPHICS_AVAILABLE:
            self.enhanced_graphics = EnhancedGraphicsCanvas(graphics_frame, 380, 300)
            
            # Connect to interpreter (using available attributes)
            try:
                self.interpreter.turtle_graphics = {
                    'canvas': self.enhanced_graphics.get_canvas(),
                    'screen': self.enhanced_graphics.get_screen(),
                    'turtle': self.enhanced_graphics.get_turtle()
                }
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
            
            self.interpreter.turtle_graphics = {
                'canvas': self.basic_canvas,
                'screen': screen,
                'turtle': turtle_obj
            }

    def setup_keybindings(self):
        """Setup keyboard shortcuts"""
        keybindings = {
            '<Control-n>': self.new_file,
            '<Control-o>': self.open_file,
            '<Control-s>': self.save_file,
            '<Control-Shift-S>': self.save_as_file,
            '<Control-w>': self.close_current_tab,
            '<Control-q>': self.quit_app,
            '<F5>': self.run_code,
            '<Shift-F5>': self.stop_execution,
            '<Control-f>': self.find_text,
            '<Control-h>': self.replace_text,

            '<F1>': self.show_quick_help,
            '<Control-plus>': self.zoom_in,
            '<Control-minus>': self.zoom_out,
            '<Control-0>': self.reset_zoom
        }

        for key, command in keybindings.items():
            self.root.bind(key, lambda e, cmd=command: cmd())

    # File operations
    def new_file(self):
        """Create new file in editor"""
        self.multi_tab_editor.new_tab()
        self.update_status("New file created")

    def open_file(self):
        """Open file dialog and load file"""
        file_path = filedialog.askopenfilename(
            title="Open File",
            filetypes=[
                ("All TimeWarp files", "*.py *.js *.pilot *.bas *.logo *.pl"),
                ("Python files", "*.py"),
                ("BASIC files", "*.bas"),
                ("Logo files", "*.logo"),
                ("PILOT files", "*.pilot"),
                ("JavaScript files", "*.js"),
                ("Perl files", "*.pl"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.multi_tab_editor.open_file(file_path)
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
            text_widget.tag_configure("search_highlight", background="yellow", foreground="black")
            
            if found_positions:
                # Move to first occurrence
                text_widget.see(found_positions[0])
                text_widget.mark_set("insert", found_positions[0])
                self.update_status(f"Found {len(found_positions)} occurrence(s) of '{search_term}'")
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
        tk.Label(replace_window, text="Find:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        find_entry = tk.Entry(replace_window, width=30)
        find_entry.grid(row=0, column=1, padx=10, pady=5)
        find_entry.focus()
        
        # Replace field
        tk.Label(replace_window, text="Replace with:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
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
                    text_widget.tag_configure("search_highlight", background="yellow", foreground="black")
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
        tk.Button(button_frame, text="Find Next", command=do_find).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Replace All", command=do_replace).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=replace_window.destroy).pack(side=tk.LEFT, padx=5)

    # View operations
    def zoom_in(self):
        """Zoom in graphics canvas"""
        if hasattr(self.enhanced_graphics, 'zoom_in'):
            self.enhanced_graphics.zoom_in()

    def zoom_out(self):
        """Zoom out graphics canvas"""
        if hasattr(self.enhanced_graphics, 'zoom_out'):
            self.enhanced_graphics.zoom_out()

    def reset_zoom(self):
        """Reset graphics canvas zoom"""
        if hasattr(self.enhanced_graphics, 'zoom_fit'):
            self.enhanced_graphics.zoom_fit()



    def toggle_graphics_panel(self):
        """Toggle graphics panel visibility"""
        try:
            if hasattr(self, 'graphics_output_panel'):
                # Check current state
                if self.graphics_output_panel.winfo_viewable():
                    # Hide the panel by removing it from the container
                    self.main_container.forget(self.graphics_output_panel)
                    self.update_status("Graphics panel hidden")
                else:
                    # Show the panel by adding it back
                    try:
                        self.main_container.add(self.graphics_output_panel, weight=1, minsize=350)
                    except:
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
                
                # Execute code using appropriate method
                if language.lower() == 'pilot':
                    result = self.interpreter.run_program(code)
                elif language.lower() in ['python', 'py']:
                    # Basic Python execution
                    import io
                    import sys
                    from contextlib import redirect_stdout, redirect_stderr
                    
                    # Capture output
                    stdout_capture = io.StringIO()
                    stderr_capture = io.StringIO()
                    
                    try:
                        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                            # Check for stop flag periodically
                            if self.stop_execution_flag:
                                self.write_to_console("🛑 Execution stopped by user\n")
                                return
                            
                            exec(code)
                        
                        # Display captured output
                        stdout_content = stdout_capture.getvalue()
                        stderr_content = stderr_capture.getvalue()
                        
                        if stdout_content:
                            self.write_to_console(stdout_content)
                        if stderr_content:
                            self.write_to_console(f"Error: {stderr_content}")
                        
                        result = True
                    except Exception as e:
                        self.write_to_console(f"❌ Python Error: {str(e)}\n")
                        result = False
                else:
                    # For other languages, show placeholder
                    self.write_to_console(f"🔧 {language.upper()} execution - Coming in next update!\n")
                    result = True
                
                if not self.stop_execution_flag:
                    if result:
                        self.write_to_console(f"✅ {language.upper()} execution completed\n")
                        self.root.after(0, lambda: self.update_status(f"{language.upper()} code executed successfully"))
                    else:
                        self.write_to_console(f"❌ {language.upper()} execution failed\n")
                        self.root.after(0, lambda: self.update_status(f"{language.upper()} execution failed"))
                        
            except Exception as e:
                self.write_to_console(f"💥 Execution error: {str(e)}\n")
                self.root.after(0, lambda: self.update_status(f"Execution error: {str(e)}"))
        
        # Start execution thread
        self.execution_thread = threading.Thread(target=run_in_thread, daemon=True)
        self.execution_thread.start()

    def stop_execution(self):
        """Stop code execution"""
        try:
            # If there's an active execution thread, try to stop it
            if hasattr(self, 'execution_thread') and self.execution_thread and self.execution_thread.is_alive():
                # Set a stop flag for graceful termination
                if hasattr(self, 'stop_execution_flag'):
                    self.stop_execution_flag = True
                
                self.write_to_console("🛑 Execution stop requested...\n")
                self.update_status("Stopping execution...")
                
                # Give thread a moment to stop gracefully
                import time
                time.sleep(0.1)
                
                if self.execution_thread.is_alive():
                    self.write_to_console("⚠️ Force stopping execution (may not work for all code)\n")
                
                self.update_status("Execution stopped")
            else:
                self.write_to_console("ℹ️ No active execution to stop\n")
                self.update_status("No running code to stop")
                
        except Exception as e:
            self.update_status(f"Stop execution error: {e}")

    def clear_output(self):
        """Clear output console"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete('1.0', tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.update_status("Output cleared")

    def clear_graphics(self):
        """Clear graphics canvas"""
        if hasattr(self.enhanced_graphics, 'clear_canvas'):
            self.enhanced_graphics.clear_canvas()

    # Utility methods
    def write_to_console(self, text: str):
        """Write text to output console"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def update_status(self, message: str):
        """Update status bar"""
        if hasattr(self, 'status_label'):
            self.status_label.config(text=message)
            # Clear after 3 seconds
            self.root.after(3000, lambda: self.status_label.config(text="Ready"))

    # Feature system methods (placeholder implementations)
    def show_tutorial_system(self):
        """Show interactive tutorial system"""
        try:
            # Create tutorial window
            tutorial_window = tk.Toplevel(self.root)
            tutorial_window.title("📚 TimeWarp IDE Tutorial System")
            tutorial_window.geometry("800x600")
            tutorial_window.transient(self.root)
            tutorial_window.grab_set()
            
            # Apply current theme to tutorial window
            self.apply_theme_to_window(tutorial_window)
            
            # Create notebook for tutorial categories
            notebook = ttk.Notebook(tutorial_window)
            notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Basic Programming Tutorial
            basic_frame = ttk.Frame(notebook)
            notebook.add(basic_frame, text="🎯 Basic Programming")
            
            basic_text = tk.Text(basic_frame, wrap=tk.WORD, font=("Consolas", 11))
            basic_scrollbar = ttk.Scrollbar(basic_frame, orient=tk.VERTICAL, command=basic_text.yview)
            basic_text.configure(yscrollcommand=basic_scrollbar.set)
            
            basic_content = """🎯 BASIC PROGRAMMING TUTORIAL

Welcome to TimeWarp IDE! Let's learn the fundamentals:

1. CHOOSING A LANGUAGE:
   • PILOT (1962) - Great for beginners, simple commands
   • BASIC - Classic line-numbered programming
   • Logo - Perfect for graphics and turtle programming
   • Python - Modern, powerful scripting

2. YOUR FIRST PILOT PROGRAM:
   Type this in the editor:
   
   T:Hello, World!
   A:Enter your name
   T:Welcome to TimeWarp IDE!
   
   Press F5 to run!

3. YOUR FIRST BASIC PROGRAM:
   10 PRINT "What's your name?"
   20 INPUT N$
   30 PRINT "Hello "; N$; "!"
   40 END

4. YOUR FIRST LOGO PROGRAM:
   FORWARD 100
   RIGHT 90
   FORWARD 100
   RIGHT 90
   FORWARD 100
   RIGHT 90
   FORWARD 100

5. TIPS FOR SUCCESS:
   • Save your work frequently (Ctrl+S)
   • Use the graphics panel to see turtle drawings
   • Check the output panel for results
   • Try different themes in View → Themes"""
            
            basic_text.insert(tk.END, basic_content)
            basic_text.config(state=tk.DISABLED)
            
            basic_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            basic_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # PILOT Language Tutorial
            pilot_frame = ttk.Frame(notebook)
            notebook.add(pilot_frame, text="🚁 PILOT Language")
            
            pilot_text = tk.Text(pilot_frame, wrap=tk.WORD, font=("Consolas", 11))
            pilot_scrollbar = ttk.Scrollbar(pilot_frame, orient=tk.VERTICAL, command=pilot_text.yview)
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
            notebook.add(basic_lang_frame, text="📊 BASIC Language")
            
            basic_lang_text = tk.Text(basic_lang_frame, wrap=tk.WORD, font=("Consolas", 11))
            basic_lang_scrollbar = ttk.Scrollbar(basic_lang_frame, orient=tk.VERTICAL, command=basic_lang_text.yview)
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
            notebook.add(logo_frame, text="🐢 Logo Language")
            
            logo_text = tk.Text(logo_frame, wrap=tk.WORD, font=("Consolas", 11))
            logo_scrollbar = ttk.Scrollbar(logo_frame, orient=tk.VERTICAL, command=logo_text.yview)
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
            
            # Close button
            close_btn = ttk.Button(tutorial_window, text="Close Tutorial", 
                                  command=tutorial_window.destroy)
            close_btn.pack(pady=10)
            
            print("📚 Tutorial system opened")
            
        except Exception as e:
            messagebox.showerror("Tutorial Error", f"Failed to open tutorial system:\n{str(e)}")
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
            title_label = ttk.Label(main_frame, text="🤖 AI Coding Assistant", 
                                   font=("Arial", 14, "bold"))
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
            lang_var = tk.StringVar(value="PILOT")
            lang_combo = ttk.Combobox(lang_frame, textvariable=lang_var, 
                                     values=["PILOT", "BASIC", "Logo", "Python"],
                                     state="readonly", width=10)
            lang_combo.pack(side=tk.LEFT, padx=(5, 0))
            
            # Query input
            ttk.Label(helper_frame, text="Ask the AI:").pack(anchor=tk.W, pady=(0, 5))
            query_text = tk.Text(helper_frame, height=3, wrap=tk.WORD)
            query_text.pack(fill=tk.X, pady=(0, 10))
            query_text.insert(tk.END, "How do I draw a circle in Logo?")
            
            # Response area
            ttk.Label(helper_frame, text="AI Response:").pack(anchor=tk.W, pady=(0, 5))
            response_text = tk.Text(helper_frame, height=15, wrap=tk.WORD, font=("Consolas", 10))
            response_scrollbar = ttk.Scrollbar(helper_frame, orient=tk.VERTICAL, command=response_text.yview)
            response_text.configure(yscrollcommand=response_scrollbar.set)
            
            response_frame = ttk.Frame(helper_frame)
            response_frame.pack(fill=tk.BOTH, expand=True)
            response_text.pack(in_=response_frame, side=tk.LEFT, fill=tk.BOTH, expand=True)
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
                        "graphics": "FORWARD 100  # Move forward\nRIGHT 90     # Turn right\nFORWARD 50   # Draw a line"
                    },
                    "BASIC": {
                        "hello": "10 PRINT \"Hello, World!\"\n20 END\n\nThis prints text and ends the program.",
                        "input": "10 PRINT \"Enter your name:\"\n20 INPUT N$\n30 PRINT \"Hello \"; N$\n40 END",
                        "loop": "10 FOR I = 1 TO 10\n20 PRINT \"Count: \"; I\n30 NEXT I\n40 END",
                        "graphics": "10 FOR I = 1 TO 4\n20 FORWARD 100\n30 RIGHT 90\n40 NEXT I\n50 END"
                    },
                    "Logo": {
                        "circle": "REPEAT 360 [FORWARD 1 RIGHT 1]\n\nThis draws a circle by moving forward 1 unit and turning right 1 degree, repeated 360 times.",
                        "square": "REPEAT 4 [FORWARD 100 RIGHT 90]\n\nDraws a square with 100-unit sides.",
                        "spiral": "REPEAT 100 [FORWARD :I RIGHT 91]\n\nCreates a spiral pattern.",
                        "flower": "REPEAT 36 [\n  REPEAT 4 [FORWARD 50 RIGHT 90]\n  RIGHT 10\n]\n\nDraws a flower pattern with 36 squares."
                    },
                    "Python": {
                        "hello": "print(\"Hello, World!\")\n\nSimple text output in Python.",
                        "input": "name = input(\"What's your name? \")\nprint(f\"Hello, {name}!\")",
                        "loop": "for i in range(1, 11):\n    print(f\"Count: {i}\")",
                        "function": "def greet(name):\n    return f\"Hello, {name}!\"\n\nprint(greet(\"World\"))"
                    }
                }
                
                # Generate response
                lang_responses = responses.get(language, {})
                response = "I'd be happy to help! Here are some examples:\n\n"
                
                # Check for keywords in query
                query_lower = query.lower()
                if "hello" in query_lower or "world" in query_lower:
                    response += lang_responses.get("hello", "Try: print('Hello, World!')")
                elif "input" in query_lower or "name" in query_lower:
                    response += lang_responses.get("input", "Use input() to get user input")
                elif "loop" in query_lower or "repeat" in query_lower:
                    response += lang_responses.get("loop", "Use loops to repeat code")
                elif "circle" in query_lower and language == "Logo":
                    response += lang_responses.get("circle", "Use REPEAT to draw circles")
                elif "square" in query_lower and language == "Logo":
                    response += lang_responses.get("square", "Use REPEAT 4 for squares")
                elif "function" in query_lower and language == "Python":
                    response += lang_responses.get("function", "Use def to create functions")
                else:
                    # General help
                    response += f"For {language} programming:\n\n"
                    if language == "PILOT":
                        response += "• T: - Display text\n• A: - Get input\n• J: - Jump to label\n• M: - Match input"
                    elif language == "BASIC":
                        response += "• PRINT - Display text\n• INPUT - Get input\n• FOR...NEXT - Loops\n• IF...THEN - Conditions"
                    elif language == "Logo":
                        response += "• FORWARD/BACK - Move turtle\n• LEFT/RIGHT - Turn turtle\n• REPEAT - Loop commands\n• PENUP/PENDOWN - Control drawing"
                    elif language == "Python":
                        response += "• print() - Display text\n• input() - Get input\n• for/while - Loops\n• if/elif/else - Conditions"
                
                response += f"\n\n💡 Try running this code in TimeWarp IDE!"
                
                response_text.delete("1.0", tk.END)
                response_text.insert(tk.END, response)
            
            # Ask button
            ask_btn = ttk.Button(helper_frame, text="Ask AI", command=ask_ai)
            ask_btn.pack(pady=10)
            
            # Code Examples Tab
            examples_frame = ttk.Frame(notebook)
            notebook.add(examples_frame, text="📝 Examples")
            
            examples_text = tk.Text(examples_frame, wrap=tk.WORD, font=("Consolas", 10))
            examples_scrollbar = ttk.Scrollbar(examples_frame, orient=tk.VERTICAL, command=examples_text.yview)
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
Y:T:Correct! Well done!
N:T:Wrong! The answer is 8.

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

🐍 PYTHON EXAMPLES:
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

💡 TIP: Copy any example and paste it into TimeWarp IDE!"""
            
            examples_text.insert(tk.END, examples_content)
            examples_text.config(state=tk.DISABLED)
            
            examples_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            examples_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Close button
            close_btn = ttk.Button(main_frame, text="Close Assistant", 
                                  command=ai_window.destroy)
            close_btn.pack(pady=10)
            
            # Initial AI response
            ask_ai()
            
            print("🤖 AI Assistant opened")
            
        except Exception as e:
            messagebox.showerror("AI Assistant Error", f"Failed to open AI assistant:\n{str(e)}")
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
            title_label = ttk.Label(main_frame, text="🎮 TimeWarp IDE Gamification", 
                                   font=("Arial", 16, "bold"))
            title_label.pack(pady=(0, 20))
            
            # Create notebook for different sections
            notebook = ttk.Notebook(main_frame)
            notebook.pack(fill=tk.BOTH, expand=True)
            
            # Achievements Tab
            achievements_frame = ttk.Frame(notebook)
            notebook.add(achievements_frame, text="🏆 Achievements")
            
            # Achievement list
            achievements_text = tk.Text(achievements_frame, wrap=tk.WORD, font=("Arial", 11))
            achievements_scrollbar = ttk.Scrollbar(achievements_frame, orient=tk.VERTICAL, command=achievements_text.yview)
            achievements_text.configure(yscrollcommand=achievements_scrollbar.set)
            
            achievements_content = """🏆 ACHIEVEMENT SYSTEM

Welcome to TimeWarp IDE's Learning Journey! Complete challenges to unlock achievements and level up your programming skills!

🥇 BEGINNER ACHIEVEMENTS:
▣ First Steps - Run your first program in any language
▣ Hello World - Create a "Hello, World!" program
▣ Code Explorer - Try all 4 programming languages (PILOT, BASIC, Logo, Python)
▣ File Master - Save and load 5 different programs
▣ Theme Collector - Try all 8 available themes

🥈 INTERMEDIATE ACHIEVEMENTS:
▣ Loop Master - Write 3 different types of loops
▣ Graphics Artist - Create 5 turtle graphics programs
▣ Problem Solver - Fix 10 code errors using the error messages
▣ Speed Coder - Write a program in under 2 minutes
▣ Multi-Tab Pro - Work with 5 tabs simultaneously

🥉 ADVANCED ACHIEVEMENTS:
▣ Language Polyglot - Write the same program in all 4 languages
▣ Graphics Wizard - Create complex geometric patterns
▣ Code Optimizer - Improve program efficiency by 50%
▣ Teaching Assistant - Help others learn programming concepts
▣ Innovation Award - Create something completely original

🌟 SPECIAL ACHIEVEMENTS:
▣ Retro Programmer - Master PILOT language commands
▣ BASIC Pioneer - Create advanced BASIC programs with graphics
▣ Logo Legend - Draw intricate patterns and designs
▣ Python Expert - Use advanced Python features
▣ TimeWarp Master - Unlock all other achievements

📊 CURRENT PROGRESS:
• Programs Run: 0/100 ⭐
• Languages Used: 0/4 🔤
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
            
            ttk.Label(level_frame, text="🌟 Level 1: Novice Programmer", 
                     font=("Arial", 14, "bold")).pack()
            ttk.Label(level_frame, text="XP: 0 / 100", font=("Arial", 12)).pack()
            
            # Progress bar
            level_progress = ttk.Progressbar(level_frame, length=300, mode='determinate')
            level_progress['value'] = 0
            level_progress.pack(pady=10)
            
            # Stats
            stats_frame = ttk.LabelFrame(progress_main, text="Statistics", padding=10)
            stats_frame.pack(fill=tk.X, pady=(0, 20))
            
            stats_grid = ttk.Frame(stats_frame)
            stats_grid.pack(fill=tk.X)
            
            # Left column
            left_stats = ttk.Frame(stats_grid)
            left_stats.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            ttk.Label(left_stats, text="📝 Programs Written: 0", font=("Arial", 11)).pack(anchor=tk.W, pady=2)
            ttk.Label(left_stats, text="🚀 Programs Run: 0", font=("Arial", 11)).pack(anchor=tk.W, pady=2)
            ttk.Label(left_stats, text="💾 Files Saved: 0", font=("Arial", 11)).pack(anchor=tk.W, pady=2)
            ttk.Label(left_stats, text="🔤 Languages Used: 0/4", font=("Arial", 11)).pack(anchor=tk.W, pady=2)
            
            # Right column
            right_stats = ttk.Frame(stats_grid)
            right_stats.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            ttk.Label(right_stats, text="🏆 Achievements: 0/25", font=("Arial", 11)).pack(anchor=tk.W, pady=2)
            ttk.Label(right_stats, text="🎨 Themes Tried: 1/8", font=("Arial", 11)).pack(anchor=tk.W, pady=2)
            ttk.Label(right_stats, text="🔥 Current Streak: 0 days", font=("Arial", 11)).pack(anchor=tk.W, pady=2)
            ttk.Label(right_stats, text="⏱️ Time Coding: 0 minutes", font=("Arial", 11)).pack(anchor=tk.W, pady=2)
            
            # Language proficiency
            proficiency_frame = ttk.LabelFrame(progress_main, text="Language Proficiency", padding=10)
            proficiency_frame.pack(fill=tk.X)
            
            languages = [("🚁 PILOT", 0), ("🔢 BASIC", 0), ("🐢 Logo", 0), ("🐍 Python", 0)]
            
            for lang, level in languages:
                lang_frame = ttk.Frame(proficiency_frame)
                lang_frame.pack(fill=tk.X, pady=2)
                
                ttk.Label(lang_frame, text=lang, width=15).pack(side=tk.LEFT)
                prog = ttk.Progressbar(lang_frame, length=200, mode='determinate')
                prog['value'] = level
                prog.pack(side=tk.LEFT, padx=(10, 5))
                ttk.Label(lang_frame, text=f"{level}%").pack(side=tk.LEFT)
            
            # Challenges Tab
            challenges_frame = ttk.Frame(notebook)
            notebook.add(challenges_frame, text="🎯 Challenges")
            
            challenges_text = tk.Text(challenges_frame, wrap=tk.WORD, font=("Arial", 11))
            challenges_scrollbar = ttk.Scrollbar(challenges_frame, orient=tk.VERTICAL, command=challenges_text.yview)
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
    • Write the same program in 2 languages
    • Compare how they work differently

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

🏆 WEEKLY CHALLENGES:
━━━━━━━━━━━━━━━━━━━━
This Week: "Retro Game Recreation"
• Recreate a classic game like Pong or Snake
• Use any TimeWarp language
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
• All challenges: "TimeWarp Champion" title"""
            
            challenges_text.insert(tk.END, challenges_content)
            challenges_text.config(state=tk.DISABLED)
            
            challenges_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            challenges_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Close button
            close_btn = ttk.Button(main_frame, text="Close Dashboard", 
                                  command=game_window.destroy)
            close_btn.pack(pady=10)
            
            print("🎮 Gamification dashboard opened")
            
        except Exception as e:
            messagebox.showerror("Gamification Error", f"Failed to open gamification dashboard:\n{str(e)}")
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
            title_label = ttk.Label(main_frame, text="📝 Code Templates", 
                                   font=("Arial", 14, "bold"))
            title_label.pack(pady=(0, 10))
            
            # Language selection
            lang_frame = ttk.Frame(main_frame)
            lang_frame.pack(fill=tk.X, pady=(0, 10))
            
            ttk.Label(lang_frame, text="Language:").pack(side=tk.LEFT)
            lang_var = tk.StringVar(value="PILOT")
            lang_combo = ttk.Combobox(lang_frame, textvariable=lang_var, 
                                     values=["PILOT", "BASIC", "Logo", "Python"],
                                     state="readonly", width=10)
            lang_combo.pack(side=tk.LEFT, padx=(5, 20))
            
            # Template categories
            ttk.Label(lang_frame, text="Category:").pack(side=tk.LEFT)
            category_var = tk.StringVar(value="Basic")
            category_combo = ttk.Combobox(lang_frame, textvariable=category_var,
                                         values=["Basic", "Loops", "Graphics", "Games", "Math"],
                                         state="readonly", width=10)
            category_combo.pack(side=tk.LEFT, padx=(5, 0))
            
            # Templates display
            templates_text = tk.Text(main_frame, height=25, wrap=tk.NONE, font=("Consolas", 10))
            templates_scrollbar_y = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=templates_text.yview)
            templates_scrollbar_x = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=templates_text.xview)
            templates_text.configure(yscrollcommand=templates_scrollbar_y.set, xscrollcommand=templates_scrollbar_x.set)
            
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
Y(TABLE):I <= 12"""
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
80 END"""
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
]"""
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
print(f"{num}! = {factorial(num)}")"""
                }
            }
            
            def update_templates():
                """Update templates based on language and category selection"""
                language = lang_var.get()
                category = category_var.get() 
                
                content = templates.get(language, {}).get(category, "No templates available for this combination.")
                
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
                        messagebox.showwarning("No Selection", "Please select text to copy.")
                except tk.TclError:
                    messagebox.showwarning("No Selection", "Please select text to copy.")
            
            ttk.Button(button_frame, text="Copy Selected", command=copy_template).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(button_frame, text="Close", command=templates_window.destroy).pack(side=tk.RIGHT)
            
            # Load initial templates
            update_templates()
            
            print("📝 Code templates opened")
            
        except Exception as e:
            messagebox.showerror("Templates Error", f"Failed to open code templates:\n{str(e)}")
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
            title_label = ttk.Label(main_frame, text="🔍 Code Analyzer", 
                                   font=("Arial", 14, "bold"))
            title_label.pack(pady=(0, 10))
            
            # Get current code
            current_code = ""
            if hasattr(self, 'multi_tab_editor') and self.multi_tab_editor.tabs:
                current_code = self.multi_tab_editor.get_active_content()
            
            # Analysis results
            results_text = tk.Text(main_frame, wrap=tk.WORD, font=("Consolas", 10), height=25)
            results_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=results_text.yview)
            results_text.configure(yscrollcommand=results_scrollbar.set)
            
            # Perform analysis
            analysis = self.analyze_code(current_code)
            
            results_text.insert(tk.END, analysis)
            results_text.config(state=tk.DISABLED)
            
            results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Close button
            close_btn = ttk.Button(main_frame, text="Close Analyzer", 
                                  command=analyzer_window.destroy)
            close_btn.pack(pady=10)
            
            print("🔍 Code analyzer opened")
            
        except Exception as e:
            messagebox.showerror("Analyzer Error", f"Failed to open code analyzer:\n{str(e)}")
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
        
        lines = code.split('\n')
        total_lines = len(lines)
        non_empty_lines = len([line for line in lines if line.strip()])
        comment_lines = len([line for line in lines if line.strip().startswith(('#', 'REM', '//'))])
        
        # Detect language
        language = "Unknown"
        if any(line.strip().startswith(('T:', 'A:', 'J:', 'Y:', 'N:')) for line in lines):
            language = "PILOT"
        elif any(line.strip().split()[0].isdigit() if line.strip().split() else False for line in lines):
            language = "BASIC"
        elif any(word in code.upper() for word in ['FORWARD', 'BACK', 'LEFT', 'RIGHT', 'REPEAT']):
            language = "Logo"
        elif any(word in code for word in ['print(', 'def ', 'import ', 'if __name__']):
            language = "Python"
        
        # Calculate complexity
        complexity_keywords = ['IF', 'FOR', 'WHILE', 'REPEAT', 'Y:', 'N:', 'J:']
        complexity_score = sum(1 for line in lines for keyword in complexity_keywords if keyword in line.upper())
        
        # Generate suggestions
        suggestions = []
        if comment_lines == 0 and non_empty_lines > 5:
            suggestions.append("• Add comments to explain your code")
        if total_lines > 50:
            suggestions.append("• Consider breaking long programs into smaller functions")
        if complexity_score > 10:
            suggestions.append("• High complexity detected - consider simplifying logic")
        if language == "PILOT" and 'E:' not in code:
            suggestions.append("• Consider adding E: (End) statements for better structure")
        if language == "BASIC" and 'END' not in code.upper():
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
            "PILOT": """• Use labels (*LABEL) for better organization
• Match statements (M:) are case-sensitive
• Variables are referenced with $ (e.g., $INPUT)
• Use E: to end program sections cleanly""",
            
            "BASIC": """• Line numbers help organize program flow
• Use meaningful variable names (A$, NAME$, etc.)
• FOR...NEXT loops are very efficient
• DIM arrays before using them""",
            
            "Logo": """• PENUP/PENDOWN control drawing
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
• Test your code thoroughly"""
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
            title_label = ttk.Label(main_frame, text="📊 Your Learning Progress", 
                                   font=("Arial", 14, "bold"))
            title_label.pack(pady=(0, 20))
            
            # Progress content
            progress_text = tk.Text(main_frame, wrap=tk.WORD, font=("Arial", 11), height=28)
            progress_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=progress_text.yview)
            progress_text.configure(yscrollcommand=progress_scrollbar.set)
            
            progress_content = """📊 LEARNING PROGRESS TRACKER

Welcome to your personal learning journey with TimeWarp IDE!

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
   ✅ First Steps - Ran your first TimeWarp program
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
            close_btn = ttk.Button(main_frame, text="Close Progress", 
                                  command=progress_window.destroy)
            close_btn.pack(pady=10)
            
            print("📊 Learning progress opened")
            
        except Exception as e:
            messagebox.showerror("Progress Error", f"Failed to open learning progress:\n{str(e)}")
            print(f"❌ Progress error: {e}")

    def show_plugin_manager(self):
        """Show plugin manager"""
        messagebox.showinfo("Plugin Manager", "Plugin management - Coming in next update!")

    def show_documentation(self):
        """Show documentation"""
        messagebox.showinfo("Documentation", "Built-in docs - Coming in next update!")

    def show_quick_help(self):
        """Show quick help"""
        help_text = """⏰ TimeWarp IDE v1.1 - Quick Help

🔥 NEW FEATURES:
• Multi-tab editor with syntax highlighting
• File explorer with project navigation  
• Enhanced graphics canvas with zoom/export
• Better error messages with suggestions

⌨️ KEYBOARD SHORTCUTS:
• Ctrl+N - New file
• Ctrl+O - Open file
• Ctrl+S - Save file
• Ctrl+W - Close tab
• F5 - Run code
• F1 - This help

🎯 LANGUAGES SUPPORTED:
• PILOT (Educational programming)
• BASIC (Classic line-numbered)
• Logo (Turtle graphics)
• Python (Modern scripting)
• JavaScript (Web scripting)
• Perl (Text processing)

🚀 Happy coding through time!"""
        
        messagebox.showinfo("TimeWarp IDE v1.1 - Quick Help", help_text)

    # Theme and settings


    def show_settings(self):
        """Show settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ TimeWarp IDE Settings")
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
        
        # Font settings
        font_frame = ttk.LabelFrame(editor_frame, text="Font Settings")
        font_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(font_frame, text="Font Family:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        font_var = tk.StringVar(value="Consolas")
        font_combo = ttk.Combobox(font_frame, textvariable=font_var, 
                                 values=["Consolas", "Monaco", "DejaVu Sans Mono", "Courier New"])
        font_combo.grid(row=0, column=1, padx=5, pady=2)
        
        tk.Label(font_frame, text="Font Size:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        size_var = tk.IntVar(value=10)
        size_spin = tk.Spinbox(font_frame, from_=8, to=24, textvariable=size_var, width=10)
        size_spin.grid(row=1, column=1, padx=5, pady=2)
        
        # Editor behavior
        behavior_frame = ttk.LabelFrame(editor_frame, text="Editor Behavior")
        behavior_frame.pack(fill=tk.X, padx=10, pady=5)
        
        line_numbers_var = tk.BooleanVar(value=True)
        tk.Checkbutton(behavior_frame, text="Show line numbers", 
                      variable=line_numbers_var).pack(anchor="w", padx=5, pady=2)
        
        auto_indent_var = tk.BooleanVar(value=True)
        tk.Checkbutton(behavior_frame, text="Auto-indent", 
                      variable=auto_indent_var).pack(anchor="w", padx=5, pady=2)
        
        word_wrap_var = tk.BooleanVar(value=False)
        tk.Checkbutton(behavior_frame, text="Word wrap", 
                      variable=word_wrap_var).pack(anchor="w", padx=5, pady=2)
        
        # Theme Settings Tab
        theme_frame = ttk.Frame(notebook)
        notebook.add(theme_frame, text="🎨 Themes")
        
        current_theme_frame = ttk.LabelFrame(theme_frame, text="Current Theme")
        current_theme_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(current_theme_frame, text=f"Active Theme: {self.current_theme.title()}").pack(pady=10)
        
        theme_list_frame = ttk.LabelFrame(theme_frame, text="Available Themes")
        theme_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        themes = ["dracula", "monokai", "solarized", "ocean", "spring", "sunset", "candy", "forest"]
        theme_var = tk.StringVar(value=self.current_theme)
        
        for theme in themes:
            rb = tk.Radiobutton(theme_list_frame, text=theme.title(), 
                               variable=theme_var, value=theme)
            rb.pack(anchor="w", padx=5, pady=2)
        
        # General Settings Tab
        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text="⚙️ General")
        
        startup_frame = ttk.LabelFrame(general_frame, text="Startup Options")
        startup_frame.pack(fill=tk.X, padx=10, pady=5)
        
        remember_tabs_var = tk.BooleanVar(value=True)
        tk.Checkbutton(startup_frame, text="Remember open tabs", 
                      variable=remember_tabs_var).pack(anchor="w", padx=5, pady=2)
        
        auto_save_var = tk.BooleanVar(value=False)
        tk.Checkbutton(startup_frame, text="Auto-save files", 
                      variable=auto_save_var).pack(anchor="w", padx=5, pady=2)
        
        # Button frame
        button_frame = tk.Frame(settings_window)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        def apply_settings():
            # Apply theme change
            if theme_var.get() != self.current_theme:
                self.change_theme(theme_var.get())
            
            self.update_status("Settings applied")
            settings_window.destroy()
        
        def cancel_settings():
            settings_window.destroy()
        
        # Buttons
        tk.Button(button_frame, text="Apply", command=apply_settings).pack(side=tk.RIGHT, padx=5)
        tk.Button(button_frame, text="Cancel", command=cancel_settings).pack(side=tk.RIGHT, padx=5)
        tk.Button(button_frame, text="OK", command=apply_settings).pack(side=tk.RIGHT, padx=5)

    def show_about(self):
        """Show about dialog"""
        about_text = """⏰ TimeWarp IDE v1.1
Enhanced Educational Programming Environment

🔥 NEW IN v1.1:
✅ Multi-tab code editor with syntax highlighting
✅ File explorer with project navigation
✅ Enhanced graphics canvas (zoom, export, grid)
✅ Better error messages with suggestions
✅ Improved UI layout and usability

🎯 MISSION:
Bridge programming history with modern development
through an accessible educational environment.

💝 FEATURES:
• 6 Programming languages (PILOT, BASIC, Logo, Python, JS, Perl)
• Turtle graphics with modern enhancements
• Educational tutorials and AI assistance
• Plugin architecture and themes
• Open source and community-driven

🌟 Developed with ❤️ for educators and learners worldwide

GitHub: https://github.com/James-HoneyBadger/Time_Warp
License: MIT"""

        
        messagebox.showinfo("About TimeWarp IDE v1.1", about_text)
    
    def change_theme(self, theme_name):
        """Change to a different theme"""
        try:
            print(f"🎨 Changing theme to: {theme_name}")
            self.current_theme = theme_name
            
            # Save theme preference
            config = load_config()
            config['current_theme'] = theme_name
            save_config(config)
            
            # Apply the new theme
            self.apply_theme()
            
            print(f"✅ Theme changed to: {theme_name}")
        except Exception as e:
            print(f"⚠️ Theme change error: {e}")

    def apply_theme(self):
        """Apply current theme to all components"""
        try:
            print(f"🎨 Applying theme: {self.current_theme}")
            
            # Initialize theme manager if not already done
            if not hasattr(self, 'theme_manager'):
                from tools.theme import ThemeManager
                self.theme_manager = ThemeManager()
            
            # Apply theme to root window and ttk styles
            self.theme_manager.apply_theme(self.root, self.current_theme)
            colors = self.theme_manager.get_colors()
            
            # Apply theme to main panels
            self.root.configure(bg=colors["bg_primary"])
            
            # Apply theme to multi-tab editor if it exists
            if hasattr(self, 'multi_tab_editor'):
                self.multi_tab_editor.apply_theme(colors)
            

            
            # Apply theme to enhanced graphics canvas if it exists
            if hasattr(self, 'enhanced_graphics') and ENHANCED_GRAPHICS_AVAILABLE:
                self.enhanced_graphics.apply_theme(colors)
            elif hasattr(self, 'basic_canvas'):
                self.theme_manager.apply_canvas_theme(self.basic_canvas)
            
            # Apply theme to output text areas
            if hasattr(self, 'output_text'):
                self.theme_manager.apply_text_widget_theme(self.output_text)
            
        except Exception as e:
            print(f"⚠️ Theme application error: {e}")

    def apply_theme_to_window(self, window):
        """Apply current theme to a specific window"""
        try:
            # Initialize theme manager if not already done
            if not hasattr(self, 'theme_manager'):
                from tools.theme import ThemeManager
                self.theme_manager = ThemeManager()
            
            # Apply theme to the window
            self.theme_manager.apply_theme(window, self.current_theme)
            colors = self.theme_manager.get_colors()
            
            # Apply basic styling to the window
            window.configure(bg=colors["bg_primary"])
            
        except Exception as e:
            print(f"⚠️ Window theme application error: {e}")

    def load_plugins(self):
        """Load essential plugins"""
        try:
            print("🔌 Loading plugins...")
            # TODO: Load plugins for v1.1
        except Exception as e:
            print(f"⚠️ Plugin loading error: {e}")

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
                f"You have {unsaved_count} unsaved file(s). Save before closing?"
            )
            if result is None:  # Cancel
                return
            elif result:  # Yes, save all
                self.save_all_files()

        self.root.quit()


def main():
    """Main application entry point - TimeWarp IDE v1.1"""
    print("🚀 Starting TimeWarp IDE v1.1...")
    print("⏰ Enhanced Educational Programming Environment")
    print("🔥 New: Multi-tab editor, Enhanced graphics, Theme selector!")
    
    try:
        app = TimeWarpIDE_v11()
        app.root.mainloop()
        print("👋 TimeWarp IDE session ended. Happy coding!")
    except KeyboardInterrupt:
        print("\n⚡ TimeWarp interrupted. See you next time!")
    except Exception as e:
        print(f"💥 TimeWarp error: {e}")
        print("🔧 Please report this issue on GitHub")


if __name__ == "__main__":
    main()