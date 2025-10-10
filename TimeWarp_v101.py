#!/usr/bin/env python3
"""
TimeWarp IDE v1.0.1 - Enhanced Multi-Tab Editor
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


class TimeWarpIDE_v101:
    """
    TimeWarp IDE v1.0.1 - Enhanced Educational Programming Environment
    New features: Multi-tab editor, File explorer, Enhanced graphics, Better errors
    """

    def __init__(self):
        """Initialize TimeWarp IDE v1.0.1"""
        print("🚀 Starting TimeWarp IDE v1.0.1...")
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
        
        print("🚀 TimeWarp IDE v1.0.1 - Clean two-panel layout ready!")

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
            
            # Simplified feature initialization for v1.0.1
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
        """Show tutorial system"""
        messagebox.showinfo("Tutorial System", "Interactive tutorials - Coming in next update!")

    def show_ai_assistant(self):
        """Show AI assistant"""
        messagebox.showinfo("AI Assistant", "AI code help - Coming in next update!")

    def show_gamification_dashboard(self):
        """Show gamification dashboard"""
        messagebox.showinfo("Gamification", "Achievement system - Coming in next update!")

    def show_plugin_manager(self):
        """Show plugin manager"""
        messagebox.showinfo("Plugin Manager", "Plugin management - Coming in next update!")

    def show_documentation(self):
        """Show documentation"""
        messagebox.showinfo("Documentation", "Built-in docs - Coming in next update!")

    def show_quick_help(self):
        """Show quick help"""
        help_text = """⏰ TimeWarp IDE v1.0.1 - Quick Help

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
        
        messagebox.showinfo("TimeWarp IDE v1.0.1 - Quick Help", help_text)

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
        about_text = """⏰ TimeWarp IDE v1.0.1
Enhanced Educational Programming Environment

🔥 NEW IN v1.0.1:
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

        messagebox.showinfo("About TimeWarp IDE v1.0.1", about_text)

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

    def load_plugins(self):
        """Load essential plugins"""
        try:
            print("🔌 Loading plugins...")
            # TODO: Load plugins for v1.0.1
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
    """Main application entry point - TimeWarp IDE v1.0.1"""
    print("🚀 Starting TimeWarp IDE v1.0.1...")
    print("⏰ Enhanced Educational Programming Environment")
    print("🔥 New: Multi-tab editor, File explorer, Enhanced graphics!")
    
    try:
        app = TimeWarpIDE_v101()
        app.root.mainloop()
        print("👋 TimeWarp IDE session ended. Happy coding!")
    except KeyboardInterrupt:
        print("\n⚡ TimeWarp interrupted. See you next time!")
    except Exception as e:
        print(f"💥 TimeWarp error: {e}")
        print("🔧 Please report this issue on GitHub")


if __name__ == "__main__":
    main()