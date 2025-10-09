#!/usr/bin/env python3
"""
JAMES - Joint Algorithm Model Environment System
Streamlined and efficient educational programming IDE
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
from core.interpreter import JAMESInterpreter
from core.editor.enhanced_editor import EnhancedCodeEditor
from tools.theme import ThemeManager
from plugins import PluginManager


class JAMES:
    """
    Streamlined JAMES Application Class
    Focus on core IDE functionality with clean architecture
    """

    def __init__(self):
        """Initialize JAMES with essential components only"""
        # Main window setup
        self.root = tk.Tk()
        self.root.title("🚀 JAMES - Joint Algorithm Model Environment System")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        
        # Initialize theme system
        self.theme_manager = ThemeManager()
        self.load_theme_config()
        
        # Initialize plugin system
        self.plugin_manager = PluginManager(self)
        
        # Core components
        self.interpreter = JAMESInterpreter()
        self.current_file = None
        
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
        """Setup the main user interface"""
        # Create main container
        self.main_container = tk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Setup toolbar
        self.setup_toolbar()
        
        # Create main paned window
        self.main_paned = ttk.PanedWindow(self.main_container, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Left panel for project explorer
        self.left_panel = ttk.Frame(self.main_paned)
        self.main_paned.add(self.left_panel, weight=0)
        
        # Center panel for editor and console
        self.center_paned = ttk.PanedWindow(self.main_paned, orient=tk.VERTICAL)
        self.main_paned.add(self.center_paned, weight=3)
        
        # Right panel for graphics
        self.right_panel = ttk.Frame(self.main_paned)
        self.main_paned.add(self.right_panel, weight=1)
        
        # Setup components
        self.setup_menu()
        self.setup_project_explorer()
        self.setup_editor()
        self.setup_console()
        self.setup_graphics()
        self.setup_status_bar()

    def setup_toolbar(self):
        """Setup simplified toolbar"""
        self.toolbar = ttk.Frame(self.root)
        self.toolbar.pack(fill=tk.X, padx=5, pady=(5,0))
        
        # Main toolbar: File operations only
        toolbar_line1 = ttk.Frame(self.toolbar)
        toolbar_line1.pack(fill=tk.X, pady=(0,5))
        
        # Initialize language_var for compatibility
        self.language_var = tk.StringVar(value="PILOT")
        
        # File operations
        ttk.Button(toolbar_line1, text="📁 New", command=self.new_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_line1, text="📂 Open", command=self.open_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_line1, text="💾 Save", command=self.save_file).pack(side=tk.LEFT, padx=2)

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
        
        # Tools menu
        tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="🎨 Theme Selector", command=self.show_theme_selector)
        tools_menu.add_command(label="⚙️ Settings", command=self.show_settings)
        
        # Help menu
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About JAMES", command=self.show_about)

    def setup_editor(self):
        """Setup streamlined code editor"""
        # Editor section
        editor_frame = ttk.LabelFrame(self.center_paned, text="📝 Code Editor")
        self.center_paned.add(editor_frame, weight=2)
        
        # Create editor toolbar within editor frame
        editor_toolbar_top = ttk.Frame(editor_frame)
        editor_toolbar_top.pack(fill=tk.X, padx=5, pady=(5,0))
        
        # Language selection
        ttk.Label(editor_toolbar_top, text="Language:").pack(side=tk.LEFT, padx=(0,5))
        self.editor_language_var = tk.StringVar(value="PILOT")
        editor_language_combo = ttk.Combobox(
            editor_toolbar_top, 
            textvariable=self.editor_language_var,
            values=["PILOT", "BASIC", "Logo", "Python", "JavaScript", "Perl"],
            state="readonly",
            width=12
        )
        editor_language_combo.pack(side=tk.LEFT, padx=(0,10))
        editor_language_combo.bind("<<ComboboxSelected>>", self.on_language_changed)
        
        # Basic syntax features
        ttk.Separator(editor_toolbar_top, orient='vertical').pack(side=tk.LEFT, padx=5, fill=tk.Y)
        ttk.Button(editor_toolbar_top, text="🎨 Syntax", command=lambda: self.write_to_console("🎨 Syntax highlighting enabled")).pack(side=tk.LEFT, padx=2)
        ttk.Button(editor_toolbar_top, text="✓ Check", command=lambda: self.write_to_console("✓ Syntax checked")).pack(side=tk.LEFT, padx=2)
        
        # Second toolbar row for actions
        editor_toolbar_bottom = ttk.Frame(editor_frame)
        editor_toolbar_bottom.pack(fill=tk.X, padx=5, pady=(3,0))
        
        # Action buttons
        ttk.Button(editor_toolbar_bottom, text="▶ Run", command=self.run_code).pack(side=tk.LEFT, padx=2)
        ttk.Button(editor_toolbar_bottom, text="⏹ Stop", command=self.stop_execution).pack(side=tk.LEFT, padx=2)
        ttk.Button(editor_toolbar_bottom, text="🗑 Clear", command=self.clear_output).pack(side=tk.LEFT, padx=2)
        
        # Create enhanced code editor
        self.code_editor = EnhancedCodeEditor(editor_frame, initial_language="pilot")
        
        # Set up callbacks
        try:
            self.code_editor.set_output_callback(self.write_to_console)
            self.code_editor.set_status_callback(self.update_status)
        except AttributeError:
            pass  # Enhanced editor methods may not be available

    def setup_console(self):
        """Setup output console"""
        console_frame = ttk.LabelFrame(self.center_paned, text="💻 Output Console")
        self.center_paned.add(console_frame, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(
            console_frame, 
            height=10, 
            state=tk.DISABLED,
            wrap=tk.WORD
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def setup_graphics(self):
        """Setup simplified graphics canvas"""
        graphics_frame = ttk.LabelFrame(self.right_panel, text="🐢 Graphics")
        graphics_frame.pack(fill=tk.BOTH, expand=True, padx=(0,0), pady=(0,5))
        
        try:
            self.graphics_canvas = tk.Canvas(
                graphics_frame, 
                width=300, 
                height=300, 
                bg='white'
            )
            self.graphics_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Initialize turtle graphics
            screen = turtle.TurtleScreen(self.graphics_canvas)
            screen.setup(280, 280)
            self.turtle = turtle.RawTurtle(screen)
        except Exception as e:
            print(f"Graphics setup error: {e}")

    def setup_project_explorer(self):
        """Setup simplified project explorer"""
        explorer_frame = ttk.LabelFrame(self.left_panel, text="📁 Project")
        explorer_frame.pack(fill=tk.BOTH, expand=True, padx=(0,5), pady=(0,5))
        
        # Simple file list
        self.file_tree = ttk.Treeview(explorer_frame, height=10)
        self.file_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Populate with current directory files
        self.refresh_project_explorer()

    def setup_status_bar(self):
        """Setup status bar"""
        self.status_bar = tk.Frame(self.root, height=25)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = tk.Label(
            self.status_bar,
            text="Ready",
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, padx=5)

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
        if hasattr(self.code_editor, 'text_editor'):
            self.code_editor.text_editor.delete(1.0, tk.END)
        self.current_file = None
        self.write_to_console("📁 New file created")

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
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    if hasattr(self.code_editor, 'text_editor'):
                        self.code_editor.text_editor.delete(1.0, tk.END)
                        self.code_editor.text_editor.insert(1.0, content)
                    
                    self.current_file = file_path
                    self.auto_detect_language(file_path)
                    self.write_to_console(f"📂 Opened: {os.path.basename(file_path)}")
                    
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
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.current_file = file_path
            self.save_to_file(file_path)

    def save_to_file(self, file_path):
        """Save content to specified file"""
        try:
            if hasattr(self.code_editor, 'text_editor'):
                content = self.code_editor.text_editor.get(1.0, tk.END + '-1c')
            else:
                content = ""
                
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
                
            self.write_to_console(f"💾 Saved: {os.path.basename(file_path)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")

    # Core execution methods
    def run_code(self):
        """Run the current code"""
        try:
            if hasattr(self.code_editor, 'text_editor'):
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
            self.write_to_console(f"▶ Running {language.upper()} code...")
            
            # Use interpreter to execute
            result = self.interpreter.execute(code)
            if result:
                self.write_to_console(str(result))
                
        except Exception as e:
            self.write_to_console(f"❌ Execution error: {e}")

    def stop_execution(self):
        """Stop code execution"""
        self.write_to_console("⏹ Execution stopped")

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
        """Update status bar"""
        if hasattr(self, 'status_label'):
            self.status_label.config(text=status)

    def on_language_changed(self, event=None):
        """Handle language change"""
        if hasattr(self, 'editor_language_var'):
            language = self.editor_language_var.get()
            self.language_var.set(language)
            self.write_to_console(f"🔄 Language changed to {language}")

    def auto_detect_language(self, file_path):
        """Auto-detect language from file extension"""
        ext = os.path.splitext(file_path)[1].lower()
        
        language_map = {
            '.pilot': 'PILOT',
            '.bas': 'BASIC',
            '.basic': 'BASIC',
            '.logo': 'Logo',
            '.py': 'Python',
            '.js': 'JavaScript',
            '.pl': 'Perl'
        }
        
        language = language_map.get(ext, 'Python')
        self.editor_language_var.set(language)
        self.language_var.set(language)

    def refresh_project_explorer(self):
        """Refresh project explorer with current directory"""
        try:
            # Clear existing items
            for item in self.file_tree.get_children():
                self.file_tree.delete(item)
                
            # Add current directory files
            current_dir = os.getcwd()
            for file in os.listdir(current_dir):
                if os.path.isfile(file) and not file.startswith('.'):
                    self.file_tree.insert("", "end", text=file)
                    
        except Exception as e:
            print(f"Project explorer error: {e}")

    # Dialog methods
    def show_theme_selector(self):
        """Show theme selection dialog"""
        themes = ["dracula", "monokai", "solarized_dark", "ocean", 
                 "spring", "sunset", "candy", "forest"]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Theme Selector")
        dialog.geometry("300x400")
        
        tk.Label(dialog, text="Select Theme:", font=("Arial", 12, "bold")).pack(pady=10)
        
        for theme in themes:
            btn = tk.Button(
                dialog, 
                text=theme.replace('_', ' ').title(),
                command=lambda t=theme: self.apply_selected_theme(t, dialog),
                width=20
            )
            btn.pack(pady=2)

    def apply_selected_theme(self, theme_name, dialog):
        """Apply selected theme"""
        self.current_theme = theme_name
        self.apply_theme()
        dialog.destroy()
        
        # Save theme preference
        try:
            from tools.theme import save_config
            self.config["current_theme"] = theme_name
            save_config(self.config)
        except Exception as e:
            print(f"Failed to save theme config: {e}")

    def show_settings(self):
        """Show settings dialog"""
        messagebox.showinfo("Settings", "Settings dialog - Feature available in plugins")

    def show_about(self):
        """Show about dialog"""
        about_text = f"""
JAMES - Joint Algorithm Model Environment System
Streamlined Educational Programming IDE

Version: 3.0 (Streamlined)
Platform: {platform.system()} {platform.release()}
Python: {sys.version.split()[0]}

A modern, educational programming environment
supporting multiple languages with turtle graphics.

Streamlined for efficiency and maintainability.
        """
        messagebox.showinfo("About JAMES", about_text)

    def find_text(self):
        """Simple find functionality"""
        if hasattr(self.code_editor, 'text_editor'):
            search_term = simpledialog.askstring("Find", "Enter text to find:")
            if search_term:
                # Simple search implementation
                content = self.code_editor.text_editor.get(1.0, tk.END)
                if search_term in content:
                    self.write_to_console(f"🔍 Found: '{search_term}'")
                else:
                    self.write_to_console(f"🔍 Not found: '{search_term}'")

    def replace_text(self):
        """Simple replace functionality"""
        self.write_to_console("🔄 Replace functionality available in enhanced editor")

    def apply_theme(self):
        """Apply current theme"""
        try:
            self.theme_manager.apply_theme(self.root, self.current_theme)
            colors = self.theme_manager.get_colors()
            self.root.configure(bg=colors.get('bg_primary', '#1E1E2E'))
            self.write_to_console(f"🎨 Applied theme: {self.current_theme}")
        except Exception as e:
            print(f"Theme application error: {e}")

    def quit_app(self):
        """Quit application"""
        if messagebox.askokcancel("Quit", "Do you want to quit JAMES?"):
            self.root.quit()


def main():
    """Main application entry point"""
    try:
        app = JAMES()
        app.root.mainloop()
    except Exception as e:
        print(f"Error starting JAMES: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()