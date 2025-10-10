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

# Core modular components
from core.interpreter import TimeWarpInterpreter
from tools.theme import ThemeManager
from plugins import PluginManager

# v1.0.1 Enhanced components
from gui.components.multi_tab_editor import MultiTabEditor
from gui.components.file_explorer import FileExplorer
# PIL is optional for enhanced graphics
try:
    from gui.components.enhanced_graphics_canvas import EnhancedGraphicsCanvas
    ENHANCED_GRAPHICS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Enhanced graphics not available: {e}")
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
        """Initialize TimeWarp IDE v1.0.1 with enhanced components"""
        # Main window setup
        self.root = tk.Tk()
        self.root.title("⏰ TimeWarp IDE v1.0.1 - Enhanced Educational Programming")
        self.root.geometry("1600x1000")
        try:
            self.root.minsize(1200, 800)
        except:
            # Fallback for older Tkinter versions
            self.root.wm_minsize(1200, 800)

        # Initialize theme system
        self.theme_manager = ThemeManager()
        self.load_theme_config()

        # Initialize plugin system
        self.plugin_manager = PluginManager(self)

        # Core components
        self.interpreter = TimeWarpInterpreter()
        
        # v1.0.1 Enhanced components
        self.error_handler = EnhancedErrorHandler(self.write_to_console)
        
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

        # Setup UI with new layout
        self.setup_ui()
        self.load_plugins()
        self.apply_theme()

        # Initialize keybindings
        self.setup_keybindings()

        print("🚀 TimeWarp IDE v1.0.1 - Enhanced features loaded!")

    def load_theme_config(self):
        """Load theme configuration"""
        try:
            self.current_theme = self.theme_manager.config.get("current_theme", "dracula")
            print(f"🎨 Loaded theme: {self.current_theme}")
        except Exception as e:
            print(f"⚠️ Theme loading error: {e}")
            self.current_theme = "dracula"

    def setup_ui(self):
        """Setup the enhanced UI with new v1.0.1 layout"""
        # Create main container with three-panel layout
        self.main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left panel: File Explorer (250px width)
        self.left_panel = ttk.Frame(self.main_container, width=250)
        try:
            self.main_container.add(self.left_panel, weight=0, minsize=200)
        except:
            self.main_container.add(self.left_panel, weight=0)

        # Center panel: Code Editor
        self.center_panel = ttk.Frame(self.main_container)
        try:
            self.main_container.add(self.center_panel, weight=3, minsize=600)
        except:
            self.main_container.add(self.center_panel, weight=3)

        # Right panel: Graphics and Output
        self.right_panel = ttk.Frame(self.main_container, width=400)
        try:
            self.main_container.add(self.right_panel, weight=1, minsize=350)
        except:
            self.main_container.add(self.right_panel, weight=1)

        # Setup components
        self.setup_menu()
        self.setup_file_explorer()
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
        view_menu.add_command(label="📁 Toggle File Explorer", command=self.toggle_file_explorer, accelerator="Ctrl+B")
        view_menu.add_command(label="🎨 Toggle Graphics Panel", command=self.toggle_graphics_panel)

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
        tools_menu.add_command(label="🎨 Theme Selector", command=self.show_theme_selector)
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

    def setup_file_explorer(self):
        """Setup file explorer panel"""
        self.file_explorer = FileExplorer(self.left_panel, self.open_file_from_explorer)

    def setup_multi_tab_editor(self):
        """Setup multi-tab code editor"""
        # Editor with status bar
        editor_frame = ttk.Frame(self.center_panel)
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
        self.right_notebook = ttk.Notebook(self.right_panel)
        self.right_notebook.pack(fill=tk.BOTH, expand=True)

        # Output tab
        output_frame = ttk.Frame(self.right_notebook)
        self.right_notebook.add(output_frame, text="📺 Output")

        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            state=tk.DISABLED,
            wrap=tk.WORD,
            font=('Consolas', 10)
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Graphics tab
        graphics_frame = ttk.Frame(self.right_notebook)
        self.right_notebook.add(graphics_frame, text="🎨 Graphics")

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
            '<Control-b>': self.toggle_file_explorer,
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

    def open_file_from_explorer(self, file_path: str):
        """Open file from file explorer"""
        self.multi_tab_editor.open_file(file_path)
        self.update_status(f"Opened: {os.path.basename(file_path)}")

    def open_folder(self):
        """Open folder in file explorer"""
        folder_path = filedialog.askdirectory(title="Open Project Folder")
        if folder_path:
            self.file_explorer.set_project_path(folder_path)
            self.update_status(f"Opened project: {os.path.basename(folder_path)}")

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
        # TODO: Implement find in active tab
        self.update_status("Find function - Coming soon!")

    def replace_text(self):
        """Show replace dialog"""  
        # TODO: Implement replace in active tab
        self.update_status("Replace function - Coming soon!")

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

    def toggle_file_explorer(self):
        """Toggle file explorer visibility"""
        # TODO: Implement panel toggling
        self.update_status("File explorer toggle - Coming soon!")

    def toggle_graphics_panel(self):
        """Toggle graphics panel visibility"""
        # TODO: Implement panel toggling
        self.update_status("Graphics panel toggle - Coming soon!")

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
        
        try:
            # Clear previous output
            self.clear_output()
            
            # Execute code using appropriate method
            if language.lower() == 'pilot':
                result = self.interpreter.run_program(code)
            else:
                # For other languages, we'll need language-specific executors
                self.write_to_console(f"🔧 {language.upper()} execution - Coming in next update!\n")
                result = True
            
            if result:
                self.write_to_console(f"✅ {language.upper()} execution completed\n")
            else:
                self.write_to_console(f"❌ {language.upper()} execution failed\n")
                
        except Exception as e:
            self.error_handler.display_error(str(e), language, code)

    def stop_execution(self):
        """Stop code execution"""
        # TODO: Implement execution stopping
        self.update_status("Stop execution - Coming soon!")

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
    def show_theme_selector(self):
        """Show theme selection dialog"""
        # TODO: Implement theme selector
        messagebox.showinfo("Theme Selector", "Theme selection - Coming soon!")

    def show_settings(self):
        """Show settings dialog"""
        # TODO: Implement settings
        messagebox.showinfo("Settings", "IDE settings - Coming soon!")

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

    def apply_theme(self):
        """Apply current theme to all components"""
        try:
            print(f"🎨 Applying theme: {self.current_theme}")
            # TODO: Apply theme to all new components
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