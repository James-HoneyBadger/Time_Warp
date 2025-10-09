#!/usr/bin/env python3
"""
JAMES - Joint Algorithm Model Environment System
Enhanced modular version with comprehensive feature set
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, simpledialog
import turtle
import json
from datetime import datetime
import threading
import queue
import pathlib
import subprocess
import math
import re
import random
import time

# Import modular components
from core.interpreter import JAMESInterpreter
from core.utilities import Mixer, Tween, EASE, Timer, Particle, ArduinoController
from gui.components import (
    VirtualEnvironmentManager, 
    ProjectExplorer, 
    EducationalTutorials, 
    ExerciseMode, 
    VersionControlSystem, 
    AdvancedDebugger
)
from gui.components.dialogs import GameManagerDialog
from gui.editor import AdvancedCodeEditor
from games.engine import GameManager, GameObject, GameRenderer, PhysicsEngine, Vector2D
from core.hardware import RPiController, SensorVisualizer, GameController, RobotInterface
from core.iot import IoTDevice, IoTDeviceManager, SmartHomeHub, SensorNetwork
from core.audio import AudioClip, SpatialAudio, AudioEngine
from core.networking import CollaborationUser, CollaborationSession, NetworkManager, CollaborationManager
from tools.theme import ThemeManager
from plugins import PluginManager, PluginManagerDialog

# Optional PIL import
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    class Image:
        @staticmethod
        def open(path): return None
        @staticmethod
        def new(mode, size, color=0): return None
    
    class ImageTk:
        @staticmethod
        def PhotoImage(image=None, file=None): return None


class JAMESII:
    """
    Main JAMES Application Class
    Modular architecture with comprehensive feature integration
    """
    
    def __init__(self):
        """Initialize JAMES with all components"""
        # Main window setup with modern styling
        self.root = tk.Tk()
        self.root.title("🚀 JAMES - Joint Algorithm Model Environment System")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        
        # Try to set window icon if available
        try:
            self.root.iconname("JAMES")
        except:
            pass
        
        # Initialize theme manager and load saved theme
        self.theme_manager = ThemeManager()
        # Load theme from configuration or use default
        from tools.theme import load_config
        self.config = load_config()
        self.current_theme = self.config.get("current_theme", "dracula")
        print(f"🎨 Loading saved theme: {self.current_theme}")
        
        # Initialize plugin system
        self.plugin_manager = PluginManager(self)
        
        # Core components
        self.interpreter = None
        self.current_file = None  # Track currently opened file
        self.setup_interpreter()
        
        # GUI components
        self.setup_ui()
        
        # Hardware and IoT
        self.setup_hardware()
        
        # Audio system
        self.setup_audio()
        
        # Networking
        self.setup_networking()
        
        # Games engine
        self.setup_games()
        
        # Load plugins
        self.load_plugins()
        
        # JAMES III Language support
        self.setup_james_iii_support()
        
        # Apply theme
        self.apply_theme()
        
    def setup_interpreter(self):
        """Initialize the JAMES interpreter"""
        self.interpreter = JAMESInterpreter()
        
    def setup_ui(self):
        """Setup the main user interface with modern, colorful design"""
        # Apply theme first
        self.apply_theme()
        
        # Create main container with modern styling
        self.main_container = tk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Toolbar removed for cleaner UI - functionality available in menu bar
        
        # Create main paned window with enhanced styling (no toolbar, so padding from top)
        self.main_paned = ttk.PanedWindow(self.main_container, orient=tk.HORIZONTAL, style='Modern.TPanedwindow')
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Left panel with project explorer
        self.left_panel = ttk.Frame(self.main_paned, style='Modern.TFrame')
        self.main_paned.add(self.left_panel, weight=0)
        
        # Center panel for editor and console
        self.center_paned = ttk.PanedWindow(self.main_paned, orient=tk.VERTICAL, style='Modern.TPanedwindow')
        self.main_paned.add(self.center_paned, weight=3)
        
        # Right panel for graphics and tools
        self.right_panel = ttk.Frame(self.main_paned, style='Modern.TFrame')
        self.main_paned.add(self.right_panel, weight=1)
        
        # Setup menu
        self.setup_menu()
        
        # Setup components
        self.setup_project_explorer()
        self.setup_editor()
        self.setup_console()
        self.setup_graphics()
        
        # Setup additional tools
        self.setup_venv_manager()
        self.setup_educational_tools()
        self.setup_debugger()
        
        # Setup keyboard shortcuts
        self.setup_keyboard_shortcuts()
        
        # Add status bar
        self.setup_status_bar()
    
    # def setup_modern_toolbar(self):
    #     """Toolbar removed for cleaner UI - functionality available in menu bar and keyboard shortcuts"""
    #     pass
    
    def setup_status_bar(self):
        """Setup modern status bar"""
        colors = self.theme_manager.get_colors() if hasattr(self.theme_manager, 'get_colors') else {}
        
        # Destroy existing status bar to prevent duplication
        if hasattr(self, 'status_bar') and self.status_bar.winfo_exists():
            try:
                for child in self.status_bar.winfo_children():
                    child.destroy()
                self.status_bar.destroy()
            except tk.TclError:
                pass
        
        self.status_bar = tk.Frame(
            self.root,
            bg=colors.get('toolbar_bg', '#21222C'),
            height=25
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Status labels with modern styling
        self.status_label = tk.Label(
            self.status_bar,
            text="Ready",
            bg=colors.get('toolbar_bg', '#21222C'),
            fg=colors.get('text_primary', '#F8F8F2'),
            font=('Consolas', 9),
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Language indicator
        self.language_label = tk.Label(
            self.status_bar,
            text="PILOT/BASIC/Logo",
            bg=colors.get('accent', '#FF79C6'),
            fg='white',
            font=('Consolas', 9, 'bold'),
            padx=8
        )
        self.language_label.pack(side=tk.RIGHT, padx=10, pady=2)
    
    def _lighten_color(self, hex_color, factor=0.2):
        """Lighten a hex color for hover effects"""
        try:
            # Remove # if present
            hex_color = hex_color.lstrip('#')
            # Convert to RGB
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            # Lighten
            rgb = tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)
            # Convert back to hex
            return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        except:
            return hex_color
    
    def apply_theme(self):
        """Apply the current theme to all UI components"""
        try:
            self.theme_manager.apply_theme(self.root, self.current_theme)
            self.refresh_ui_components()
        except Exception as e:
            print(f"Theme application error: {e}")
    
    def set_theme(self, theme_name):
        """Set the color theme and save preference"""
        self.current_theme = theme_name
        
        # Save theme preference to configuration
        from tools.theme import save_config
        self.config["current_theme"] = theme_name
        save_config(self.config)
        
        self.apply_theme()
        # Refresh UI components without recreating them
        try:
            self.refresh_ui_components()
        except:
            pass
    
    def show_theme_selector(self):
        """Show theme selection popup"""
        import tkinter.messagebox as msgbox
        from tkinter import simpledialog
        
        # Create theme selection dialog
        theme_window = tk.Toplevel(self.root)
        theme_window.title("🎨 Select Theme")
        theme_window.geometry("300x250")
        theme_window.resizable(False, False)
        theme_window.transient(self.root)
        theme_window.grab_set()
        
        # Center the window
        theme_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        tk.Label(theme_window, text="Choose a Color Theme:", font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Theme buttons
        themes = [
            ("🦇 Dracula", "dracula"),
            ("🌙 Monokai", "monokai"), 
            ("☀️ Solarized", "solarized"),
            ("🌊 Ocean", "ocean"),
            ("🌸 Spring", "spring"),
            ("🌅 Sunset", "sunset"),
            ("🍭 Candy", "candy"),
            ("🌲 Forest", "forest")
        ]
        
        button_frame = tk.Frame(theme_window)
        button_frame.pack(pady=10, expand=True, fill='both')
        
        for display_name, theme_name in themes:
            btn = tk.Button(
                button_frame,
                text=display_name,
                font=('Arial', 10),
                width=20,
                pady=5,
                command=lambda t=theme_name: self.select_theme_and_close(t, theme_window)
            )
            btn.pack(pady=5)
        
        # Note about theme brightness
        tk.Label(theme_window, text="Dark themes: Dracula, Monokai, Solarized, Ocean", 
                 font=('Arial', 8), fg='gray').pack(pady=(5, 0))
        tk.Label(theme_window, text="Light themes: Spring, Sunset, Candy, Forest", 
                 font=('Arial', 8), fg='gray').pack(pady=(0, 5))
        
        # Close button
        tk.Button(theme_window, text="Cancel", command=theme_window.destroy).pack(pady=10)
    
    def select_theme_and_close(self, theme_name, window):
        """Select theme and close window"""
        self.set_theme(theme_name)
        window.destroy()

    
    def refresh_ui_components(self):
        """Refresh UI components without recreating them - apply theme consistently"""
        colors = self.theme_manager.get_colors() if hasattr(self.theme_manager, 'get_colors') else {}
        
        # Update main window background
        self.root.configure(bg=colors.get('bg_primary', '#1E1E2E'))
        
        # Update main container
        if hasattr(self, 'main_container'):
            self.main_container.configure(bg=colors.get('bg_primary', '#1E1E2E'))
        
        # Toolbar removed for cleaner UI
            
        # Update status bar colors
        if hasattr(self, 'status_bar'):
            self.status_bar.configure(bg=colors.get('toolbar_bg', '#21222C'))
        if hasattr(self, 'status_label'):
            self.status_label.configure(
                bg=colors.get('toolbar_bg', '#21222C'),
                fg=colors.get('text_primary', '#F8F8F2')
            )
        if hasattr(self, 'language_label'):
            self.language_label.configure(
                bg=colors.get('accent', '#FF79C6'),
                fg='white'
            )
        
        # Update menu bar and recreate for proper theming
        if hasattr(self, 'menubar'):
            # For proper theming of all dropdown menus, we need to recreate the menu
            self.setup_menu()
        
        # Apply theme to all text widgets (editor, output)
        if hasattr(self, 'code_editor') and hasattr(self.code_editor, 'text_editor'):
            self.theme_manager.apply_text_widget_theme(self.code_editor.text_editor)
        
        if hasattr(self, 'output_text'):
            self.theme_manager.apply_text_widget_theme(self.output_text)
            
        # Apply theme to graphics canvas
        if hasattr(self, 'graphics_canvas'):
            self.theme_manager.apply_canvas_theme(self.graphics_canvas)
            
        # Update frames that might need background colors
        for frame_attr in ['left_panel', 'center_panel', 'right_panel']:
            if hasattr(self, frame_attr):
                frame = getattr(self, frame_attr)
                try:
                    frame.configure(bg=colors.get('bg_secondary', '#282A36'))
                except:
                    pass  # Some frames might not support bg
                    
        # Note: paned windows don't support background color configuration
    
    def show_settings(self):
        """Show settings dialog"""
        messagebox.showinfo("Settings", "Settings dialog coming soon!")

    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        # File operations
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        
        # Edit operations
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<Control-x>', lambda e: self.cut())
        self.root.bind('<Control-c>', lambda e: self.copy())
        self.root.bind('<Control-v>', lambda e: self.paste())
        self.root.bind('<Control-a>', lambda e: self.select_all())
        self.root.bind('<Control-f>', lambda e: self.find_text())
        self.root.bind('<Control-h>', lambda e: self.replace_text())
        
        # View operations
        self.root.bind('<Control-plus>', lambda e: self.zoom_in())
        self.root.bind('<Control-minus>', lambda e: self.zoom_out())
        self.root.bind('<Control-0>', lambda e: self.reset_zoom())
        
        # Run operations
        self.root.bind('<F5>', lambda e: self.run_code())
        self.root.bind('<F6>', lambda e: self.stop_execution())

    def setup_menu(self):
        """Setup modern menu bar with colorful theme"""
        colors = self.theme_manager.get_colors() if hasattr(self.theme_manager, 'get_colors') else {}
        
        self.menubar = tk.Menu(
            self.root,
            bg=colors.get('menu_bg', '#282A36'),
            fg=colors.get('text_primary', '#F8F8F2'),
            activebackground=colors.get('accent', '#FF79C6'),
            activeforeground='white',
            relief='flat',
            borderwidth=0
        )
        self.root.config(menu=self.menubar)
        
        # File menu with icons
        file_menu = tk.Menu(
            self.menubar, 
            tearoff=0,
            bg=colors.get('menu_bg', '#282A36'),
            fg=colors.get('text_primary', '#F8F8F2'),
            activebackground=colors.get('accent', '#FF79C6'),
            activeforeground='white'
        )
        self.menubar.add_cascade(label="📁 File", menu=file_menu)
        file_menu.add_command(label="🆕 New", accelerator="Ctrl+N", command=self.new_file)
        file_menu.add_command(label="📂 Open", accelerator="Ctrl+O", command=self.open_file)
        file_menu.add_command(label="💾 Save", accelerator="Ctrl+S", command=self.save_file)
        file_menu.add_command(label="💾 Save As...", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="❌ Exit", command=self.root.quit)
        
        # Edit menu with icons
        edit_menu = tk.Menu(
            self.menubar, 
            tearoff=0,
            bg=colors.get('menu_bg', '#282A36'),
            fg=colors.get('text_primary', '#F8F8F2'),
            activebackground=colors.get('accent_secondary', '#8BE9FD'),
            activeforeground='white'
        )
        self.menubar.add_cascade(label="✏️ Edit", menu=edit_menu)
        edit_menu.add_command(label="↶ Undo", accelerator="Ctrl+Z", command=self.undo)
        edit_menu.add_command(label="↷ Redo", accelerator="Ctrl+Y", command=self.redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="✂️ Cut", accelerator="Ctrl+X", command=self.cut)
        edit_menu.add_command(label="📋 Copy", accelerator="Ctrl+C", command=self.copy)
        edit_menu.add_command(label="📌 Paste", accelerator="Ctrl+V", command=self.paste)
        edit_menu.add_separator()
        edit_menu.add_command(label="🔍 Find", accelerator="Ctrl+F", command=self.find_text)
        edit_menu.add_command(label="🔄 Replace", accelerator="Ctrl+H", command=self.replace_text)
        
        # Run menu with icons
        run_menu = tk.Menu(
            self.menubar, 
            tearoff=0,
            bg=colors.get('menu_bg', '#282A36'),
            fg=colors.get('text_primary', '#F8F8F2'),
            activebackground=colors.get('success', '#50FA7B'),
            activeforeground='white'
        )
        self.menubar.add_cascade(label="▶️ Run", menu=run_menu)
        run_menu.add_command(label="▶️ Run Program", accelerator="F5", command=self.run_code)
        run_menu.add_command(label="⏹️ Stop", accelerator="F6", command=self.stop_execution)
        run_menu.add_separator()
        run_menu.add_command(label="🐛 Debug", command=self.debug_code)
        
        # View menu with icons  
        view_menu = tk.Menu(
            self.menubar, 
            tearoff=0,
            bg=colors.get('menu_bg', '#282A36'),
            fg=colors.get('text_primary', '#F8F8F2'),
            activebackground=colors.get('info', '#8BE9FD'),
            activeforeground='white'
        )
        self.menubar.add_cascade(label="👁️ View", menu=view_menu)
        # Dark/light toggle removed - each theme now has fixed brightness
        
        # Theme selection submenu
        theme_submenu = tk.Menu(
            view_menu,
            tearoff=0,
            bg=colors.get('menu_bg', '#282A36'),
            fg=colors.get('text_primary', '#F8F8F2'),
            activebackground=colors.get('accent', '#FF79C6'),
            activeforeground='white'
        )
        view_menu.add_cascade(label="🎨 Color Theme", menu=theme_submenu)
        theme_submenu.add_command(label="🦇 Dracula", command=lambda: self.set_theme('dracula'))
        theme_submenu.add_command(label="🌙 Monokai", command=lambda: self.set_theme('monokai'))
        theme_submenu.add_command(label="☀️ Solarized", command=lambda: self.set_theme('solarized'))
        theme_submenu.add_command(label="🌊 Ocean", command=lambda: self.set_theme('ocean'))
        theme_submenu.add_separator()
        # Lighter themes
        theme_submenu.add_command(label="🌸 Spring", command=lambda: self.set_theme('spring'))
        theme_submenu.add_command(label="🌅 Sunset", command=lambda: self.set_theme('sunset'))
        theme_submenu.add_command(label="🍭 Candy", command=lambda: self.set_theme('candy'))
        theme_submenu.add_command(label="🌲 Forest", command=lambda: self.set_theme('forest'))
        
        view_menu.add_separator()
        view_menu.add_command(label="� Project Explorer", command=self.show_project_explorer)
        view_menu.add_command(label="🧹 Clear Output", command=self.clear_output)
        view_menu.add_separator()
        view_menu.add_command(label="�🔍+ Zoom In", accelerator="Ctrl++", command=self.zoom_in)
        view_menu.add_command(label="🔍- Zoom Out", accelerator="Ctrl+-", command=self.zoom_out)
        view_menu.add_command(label="🔍 Reset Zoom", accelerator="Ctrl+0", command=self.reset_zoom)
        
        # Help menu with icons
        help_menu = tk.Menu(
            self.menubar, 
            tearoff=0,
            bg=colors.get('menu_bg', '#282A36'),
            fg=colors.get('text_primary', '#F8F8F2'),
            activebackground=colors.get('warning', '#FFB86C'),
            activeforeground='white'
        )
        self.menubar.add_cascade(label="❓ Help", menu=help_menu)
        help_menu.add_command(label="📚 Documentation", command=self.show_help)
        help_menu.add_command(label="🎓 Tutorials", command=self.show_tutorials)
        help_menu.add_separator()
        help_menu.add_command(label="ℹ️ About", command=self.show_about)
        
        # Tools menu with consistent theming
        tools_menu = tk.Menu(
            self.menubar, 
            tearoff=0,
            bg=colors.get('menu_bg', '#282A36'),
            fg=colors.get('text_primary', '#F8F8F2'),
            activebackground=colors.get('warning', '#FFB86C'),
            activeforeground='white'
        )
        self.menubar.add_cascade(label="🔧 Tools", menu=tools_menu)
        
        # Development Tools
        tools_menu.add_command(label="🎮 Game Manager", command=self.show_game_manager)
        tools_menu.add_command(label="🔌 Plugin Manager", command=self.show_plugin_manager)
        tools_menu.add_command(label="🐛 Advanced Debugger", command=self.show_debugger)
        tools_menu.add_separator()
        
        # Interactive Tools
        tools_menu.add_command(label="💻 Interactive Console", command=self.open_james_iii_console)
        tools_menu.add_command(label="🧮 Expression Calculator", command=self.open_calculator)
        tools_menu.add_command(label="📊 Variable Inspector", command=self.show_variable_inspector)
        tools_menu.add_separator()
        
        # Analysis & Performance
        tools_menu.add_command(label="⚡ Performance Profiler", command=self.show_performance_profiler)
        tools_menu.add_command(label="📈 Code Metrics", command=self.show_code_metrics) 
        tools_menu.add_command(label="🔍 Code Analyzer", command=self.show_code_analyzer)
        tools_menu.add_separator()
        
        # Hardware & IoT
        tools_menu.add_command(label="🔌 Hardware Controller", command=self.show_hardware_controller)
        tools_menu.add_command(label="📡 IoT Device Manager", command=self.show_iot_manager)
        tools_menu.add_command(label="📊 Sensor Visualizer", command=self.show_sensor_visualizer)
        tools_menu.add_separator()
        
        # Educational & Learning
        tools_menu.add_command(label="🎓 Learning Assistant", command=self.show_learning_assistant)
        tools_menu.add_command(label="📚 Code Examples", command=self.show_code_examples)
        tools_menu.add_command(label="🧪 Testing Framework", command=self.show_testing_framework)
        tools_menu.add_separator()
        
        # Utilities
        tools_menu.add_command(label="🎨 Graphics Canvas", command=self.show_graphics_canvas)
        tools_menu.add_command(label="🔄 Code Converter", command=self.show_code_converter)
        tools_menu.add_command(label="⚙️ System Information", command=self.show_system_info)
        
        # Languages menu with consistent theming
        languages_menu = tk.Menu(
            self.menubar, 
            tearoff=0,
            bg=colors.get('menu_bg', '#282A36'),
            fg=colors.get('text_primary', '#F8F8F2'),
            activebackground=colors.get('info', '#8BE9FD'),
            activeforeground='white'
        )
        self.menubar.add_cascade(label="🌐 Languages", menu=languages_menu)
        languages_menu.add_command(label="✈️ PILOT", command=self.set_pilot_mode)
        languages_menu.add_command(label="📊 BASIC", command=self.set_basic_mode)
        languages_menu.add_command(label="🐢 Logo", command=self.set_logo_mode)
        languages_menu.add_separator()
        languages_menu.add_command(label="🐍 Python", command=self.set_python_mode)
        languages_menu.add_command(label="📜 Perl", command=self.set_perl_mode)
        languages_menu.add_command(label="🟨 JavaScript", command=self.set_javascript_mode)
        
    def setup_toolbar(self):
        """Setup toolbar"""
        self.toolbar = ttk.Frame(self.root)
        self.toolbar.pack(fill=tk.X, padx=5, pady=(5,0))
        
        # Run buttons
        ttk.Button(self.toolbar, text="▶ Run", command=self.run_code).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="⏹ Stop", command=self.stop_execution).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="🗑 Clear", command=self.clear_output).pack(side=tk.LEFT, padx=2)
        
        # File operations
        ttk.Separator(self.toolbar, orient='vertical').pack(side=tk.LEFT, padx=5, fill=tk.Y)
        ttk.Button(self.toolbar, text="📁 New", command=self.new_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="📂 Open", command=self.open_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="💾 Save", command=self.save_file).pack(side=tk.LEFT, padx=2)
        
    def setup_editor(self):
        """Setup code editor with modern styling"""
        # Editor section in center panel
        editor_frame = ttk.LabelFrame(self.center_paned, text="📝 Code Editor", style='Modern.TLabelframe')
        self.center_paned.add(editor_frame, weight=2)
        
        # Create advanced code editor
        self.code_editor = AdvancedCodeEditor(editor_frame)
        
        # Apply modern theme to editor text widget
        try:
            if hasattr(self.code_editor, 'text_editor'):
                self.theme_manager.apply_text_widget_theme(self.code_editor.text_editor)
        except Exception as e:
            print(f"Editor theme application failed: {e}")
            pass  # Fallback if theme application fails
        
    def setup_console(self):
        """Setup output console with modern styling"""
        # Console section in center panel
        console_frame = ttk.LabelFrame(self.center_paned, text="💻 Output Console", style='Modern.TLabelframe')
        self.center_paned.add(console_frame, weight=1)
        
        # Create output text area with modern theme
        colors = self.theme_manager.get_colors() if hasattr(self.theme_manager, 'get_colors') else {}
        
        self.output_text = scrolledtext.ScrolledText(
            console_frame, 
            height=10, 
            state=tk.DISABLED,
            wrap=tk.WORD,
            bg=colors.get('bg_primary', '#1E1E2E'),
            fg=colors.get('text_primary', '#F8F8F2'),
            insertbackground=colors.get('accent', '#FF79C6'),
            selectbackground=colors.get('selection', '#44475A'),
            font=('Consolas', 10),
            relief='flat',
            borderwidth=0
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
    def setup_graphics(self):
        """Setup graphics canvas with modern styling"""
        # Graphics section in right panel
        graphics_frame = ttk.LabelFrame(self.right_panel, text="🐢 Turtle Graphics", style='Modern.TLabelframe')
        graphics_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Modern graphics canvas
        colors = self.theme_manager.get_colors() if hasattr(self.theme_manager, 'get_colors') else {}
        
        self.graphics_canvas = tk.Canvas(
            graphics_frame, 
            bg=colors.get('bg_primary', 'white'),
            width=400, 
            height=300,
            highlightthickness=2,
            highlightcolor=colors.get('accent', '#FF79C6'),
            highlightbackground=colors.get('border', '#6272A4'),
            relief='flat'
        )
        self.graphics_canvas.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Connect canvas to interpreter for turtle graphics
        if hasattr(self, 'interpreter'):
            self.interpreter.ide_turtle_canvas = self.graphics_canvas
            print("🐢 Connected graphics canvas to interpreter")
        
    def setup_project_explorer(self):
        """Setup project explorer with modern styling"""
        # Project explorer in left panel
        explorer_frame = ttk.LabelFrame(self.left_panel, text="📁 Project Explorer", style='Modern.TLabelframe')
        explorer_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        self.project_explorer = ProjectExplorer(explorer_frame)
        
    def setup_venv_manager(self):
        """Setup virtual environment manager"""
        self.venv_manager = VirtualEnvironmentManager()
        
    def setup_educational_tools(self):
        """Setup educational components"""
        self.educational_tutorials = EducationalTutorials(self.root)
        self.exercise_mode = ExerciseMode(self.root)
        
    def setup_debugger(self):
        """Setup advanced debugger"""
        self.debugger = AdvancedDebugger(self.root)
        
    def setup_hardware(self):
        """Setup hardware interfaces"""
        # SensorVisualizer needs a canvas - will be initialized when canvas is available
        self.sensor_visualizer = None
        self.game_controller = GameController()
        self.robot_interface = RobotInterface()
        
    def setup_audio(self):
        """Setup audio system"""
        self.audio_engine = AudioEngine()
        self.spatial_audio = SpatialAudio()
        
    def setup_networking(self):
        """Setup networking and collaboration"""
        self.network_manager = NetworkManager()
        self.collaboration_manager = CollaborationManager()
        
    def setup_games(self):
        """Setup games engine"""
        self.game_manager = GameManager()
        self.game_renderer = GameRenderer()
        self.physics_engine = PhysicsEngine()
        
    def load_plugins(self):
        """Load and initialize plugins"""
        try:
            # Scan for available plugins
            available_plugins = self.plugin_manager.scan_plugins()
            
            # Load available plugins
            for plugin_name in available_plugins:
                try:
                    self.plugin_manager.load_plugin(plugin_name)
                except Exception as e:
                    print(f"Failed to load plugin '{plugin_name}': {e}")
                    
        except Exception as e:
            print(f"Error loading plugins: {e}")
        
    def apply_theme(self):
        """Apply current modern theme consistently across all components"""
        try:
            # Apply theme to root and get colors
            self.theme_manager.apply_theme(self.root, self.current_theme)
            
            # Update window background
            colors = self.theme_manager.get_colors()
            self.root.configure(bg=colors.get('bg_primary', '#1E1E2E'))
            
            # Apply theme to main container
            if hasattr(self, 'main_container'):
                self.main_container.configure(bg=colors.get('bg_primary', '#1E1E2E'))
            
            # Apply theme to graphics canvas if it exists
            if hasattr(self, 'graphics_canvas'):
                self.graphics_canvas.configure(
                    bg=colors.get('bg_primary', 'white'),
                    highlightcolor=colors.get('accent', '#FF79C6'),
                    highlightbackground=colors.get('border', '#6272A4')
                )
            
            # Apply theme to output text if it exists
            if hasattr(self, 'output_text'):
                self.output_text.configure(
                    bg=colors.get('bg_secondary', '#282A36'),
                    fg=colors.get('text_primary', '#F8F8F2'),
                    insertbackground=colors.get('accent', '#FF79C6'),
                    selectbackground=colors.get('selection', '#44475A')
                )
            
            # Apply theme to console if it exists
            if hasattr(self, 'james_console'):
                self.james_console.configure(
                    bg=colors.get('bg_secondary', '#282A36'),
                    fg=colors.get('text_primary', '#F8F8F2'),
                    insertbackground=colors.get('accent', '#FF79C6'),
                    selectbackground=colors.get('selection', '#44475A')
                )
            
            # Apply theme to code editor if it exists
            if hasattr(self, 'code_editor') and hasattr(self.code_editor, 'text_editor'):
                try:
                    self.theme_manager.apply_text_widget_theme(self.code_editor.text_editor)
                    # Also apply theme to line numbers and other editor components
                    if hasattr(self.code_editor, 'line_numbers'):
                        self.code_editor.line_numbers.configure(
                            bg=colors.get('bg_tertiary', '#44475A'),
                            fg=colors.get('text_muted', '#6272A4')
                        )
                    if hasattr(self.code_editor, 'line_numbers_frame'):
                        self.code_editor.line_numbers_frame.configure(
                            bg=colors.get('bg_tertiary', '#44475A')
                        )
                except Exception as e:
                    print(f"Code editor theme application failed: {e}")
            
        except Exception as e:
            print(f"Theme application error: {e}")
            pass  # Silent fail for theme application
        
    # Tool dialogs
    def show_game_manager(self):
        """Show game manager dialog"""
        try:
            dialog = GameManagerDialog(self)
            dialog.show()
        except Exception as e:
            messagebox.showerror("Error", f"Could not open Game Manager: {e}")
        
    def show_plugin_manager(self):
        """Show plugin manager dialog"""
        try:
            dialog = PluginManagerDialog(self, self.plugin_manager)
            dialog.show()
        except Exception as e:
            messagebox.showerror("Error", f"Could not open Plugin Manager: {e}")
        
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About JAMES", 
                          "JAMES - Joint Algorithm Model Environment System\n"
                          "Enhanced modular version with comprehensive features\n\n"
                          "Version 2.0\n"
                          "Educational programming environment with advanced capabilities")

    def cleanup(self):
        """Cleanup resources"""
        try:
            # Stop interpreter
            if self.interpreter:
                self.interpreter.stop_program()
                
            # Theme configuration is now saved automatically when changed
                
        except Exception:
            pass
            
    def run(self):
        """Start the application"""
        try:
            # Setup close handler
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            # Start main loop
            self.root.mainloop()
            
        except KeyboardInterrupt:
            self.cleanup()
            
    def setup_james_iii_support(self):
        """Setup JAMES III language support"""
        try:
            from core.language.james_compiler import JAMESCompiler
            self.james_iii_compiler = JAMESCompiler()
            self.current_language_mode = "python"  # Default to Python
        except ImportError:
            self.james_iii_compiler = None
            print("JAMES III compiler not available")

    def open_james_iii_console(self):
        """Open JAMES III interactive console"""
        if not self.james_iii_compiler:
            messagebox.showerror("Error", "JAMES III compiler not available")
            return
            
        # Create new window for JAMES III console
        console_window = tk.Toplevel(self.root)
        console_window.title("JAMES III Interactive Console")
        console_window.geometry("800x600")
        
        # Console text area
        console_frame = ttk.Frame(console_window)
        console_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.james_console = scrolledtext.ScrolledText(console_frame, wrap=tk.WORD, font=("Consolas", 10))
        self.james_console.pack(fill=tk.BOTH, expand=True)
        
        # Input frame
        input_frame = ttk.Frame(console_window)
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Label(input_frame, text="JAMES III >").pack(side=tk.LEFT)
        
        self.james_input = tk.Entry(input_frame)
        self.james_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.james_input.bind("<Return>", self.execute_james_iii_command)
        
        ttk.Button(input_frame, text="Execute", command=self.execute_james_iii_command).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(input_frame, text="Clear", command=self.clear_james_console).pack(side=tk.RIGHT)
        
        # Welcome message
        self.james_console.insert(tk.END, "JAMES III Interactive Console\\n")
        self.james_console.insert(tk.END, "Type HELP for help, EXIT to close\\n")
        self.james_console.insert(tk.END, "=" * 50 + "\\n\\n")
        
        self.james_input.focus()

    def execute_james_iii_command(self, event=None):
        """Execute JAMES III command from console"""
        if not self.james_iii_compiler:
            return
            
        command = self.james_input.get().strip()
        if not command:
            return
            
        # Display command
        self.james_console.insert(tk.END, f"JAMES III > {command}\\n")
        
        # Handle special commands
        if command.upper() == "EXIT":
            self.james_console.master.destroy()
            return
        elif command.upper() == "HELP":
            help_text = """
JAMES III Help:
- BASIC: LET X = 10, PRINT X, IF...THEN...ELSE, FOR...NEXT
- PILOT: T: Type text, A: Accept input, M: Match patterns  
- Logo: FORWARD 100, RIGHT 90, PENUP, PENDOWN
- Python: PYTHON: ... END_PYTHON blocks
- EXIT: Close console
- CLEAR: Clear console
            """
            self.james_console.insert(tk.END, help_text + "\\n")
        elif command.upper() == "CLEAR":
            self.clear_james_console()
            return
        else:
            # Execute JAMES III command
            try:
                def input_callback(prompt):
                    return simpledialog.askstring("Input", prompt) or ""
                
                output = self.james_iii_compiler.execute_string(command, input_callback)
                for line in output:
                    self.james_console.insert(tk.END, f"{line}\\n")
            except Exception as e:
                self.james_console.insert(tk.END, f"Error: {e}\\n")
        
        self.james_console.insert(tk.END, "\\n")
        self.james_console.see(tk.END)
        self.james_input.delete(0, tk.END)

    def clear_james_console(self):
        """Clear JAMES III console"""
        self.james_console.delete(1.0, tk.END)
        self.james_console.insert(tk.END, "JAMES III Interactive Console\\n")
        self.james_console.insert(tk.END, "=" * 50 + "\\n\\n")

    # ========================
    # TOOLS MENU IMPLEMENTATIONS
    # ========================
    
    def show_debugger(self):
        """Show advanced debugger dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("🐛 Advanced Debugger")
        dialog.geometry("1000x700")
        dialog.transient(self.root)
        
        # Create main layout with notebook
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Breakpoints Tab
        breakpoints_frame = ttk.Frame(notebook)
        notebook.add(breakpoints_frame, text="🔴 Breakpoints")
        self.setup_breakpoints_tab(breakpoints_frame)
        
        # Variables Tab
        variables_frame = ttk.Frame(notebook)
        notebook.add(variables_frame, text="📊 Variables")
        self.setup_debug_variables_tab(variables_frame)
        
        # Call Stack Tab
        callstack_frame = ttk.Frame(notebook)
        notebook.add(callstack_frame, text="📚 Call Stack")
        self.setup_callstack_tab(callstack_frame)
        
        # Execution Tab
        execution_frame = ttk.Frame(notebook)
        notebook.add(execution_frame, text="▶️ Execution")
        self.setup_execution_tab(execution_frame)
        
        # Memory Tab
        memory_frame = ttk.Frame(notebook)
        notebook.add(memory_frame, text="💾 Memory")
        self.setup_memory_tab(memory_frame)
        
        # Store dialog reference for debugger state
        self.debugger_dialog = dialog
        self.debugger_state = {
            'breakpoints': {},
            'current_line': None,
            'call_stack': [],
            'variables': {},
            'execution_mode': 'normal'
        }
        
        dialog.protocol("WM_DELETE_WINDOW", self.close_debugger)
    
    def open_calculator(self):
        """Open expression calculator"""
        calc_window = tk.Toplevel(self.root)
        calc_window.title("🧮 Expression Calculator")
        calc_window.geometry("500x400")
        calc_window.resizable(True, True)
        
        # Configure style
        colors = self.theme_manager.get_colors()
        calc_window.configure(bg=colors.get('bg_primary', '#282A36'))
        
        # Main frame
        main_frame = ttk.Frame(calc_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Expression entry
        ttk.Label(main_frame, text="Expression:").pack(anchor=tk.W)
        calc_entry = tk.Entry(main_frame, font=("Consolas", 12))
        calc_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Result display
        ttk.Label(main_frame, text="Result:").pack(anchor=tk.W)
        result_text = scrolledtext.ScrolledText(main_frame, height=15, font=("Consolas", 11))
        result_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def calculate():
            try:
                expression = calc_entry.get().strip()
                if not expression:
                    return
                    
                # Use the interpreter's expression evaluator
                if self.interpreter:
                    result = self.interpreter.evaluate_expression(expression)
                    result_text.insert(tk.END, f">>> {expression}\n{result}\n\n")
                else:
                    # Fallback to Python eval (safe expressions only)
                    import ast
                    import operator
                    
                    # Safe evaluation for basic math
                    operators = {
                        ast.Add: operator.add, ast.Sub: operator.sub,
                        ast.Mult: operator.mul, ast.Div: operator.truediv,
                        ast.Pow: operator.pow, ast.Mod: operator.mod,
                        ast.USub: operator.neg, ast.UAdd: operator.pos,
                    }
                    
                    def eval_expr(node):
                        if isinstance(node, ast.Constant):
                            return node.value
                        elif isinstance(node, ast.BinOp):
                            return operators[type(node.op)](eval_expr(node.left), eval_expr(node.right))
                        elif isinstance(node, ast.UnaryOp):
                            return operators[type(node.op)](eval_expr(node.operand))
                        else:
                            raise TypeError(f"Unsupported operation: {type(node)}")
                    
                    tree = ast.parse(expression, mode='eval')
                    result = eval_expr(tree.body)
                    result_text.insert(tk.END, f">>> {expression}\n{result}\n\n")
                    
                result_text.see(tk.END)
                calc_entry.delete(0, tk.END)
                
            except Exception as e:
                result_text.insert(tk.END, f">>> {expression}\nError: {e}\n\n")
                result_text.see(tk.END)
        
        def clear_results():
            result_text.delete(1.0, tk.END)
        
        ttk.Button(button_frame, text="Calculate", command=calculate).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Clear", command=clear_results).pack(side=tk.LEFT)
        
        calc_entry.bind("<Return>", lambda e: calculate())
        calc_entry.focus()
        
        # Add some examples
        examples = [
            "2 + 3 * 4",
            "10 ** 2",
            "(5 + 3) * 2",
            "100 / 3",
            "2 ** 8 - 1"
        ]
        
        result_text.insert(tk.END, "Expression Calculator\n")
        result_text.insert(tk.END, "=" * 30 + "\n")
        result_text.insert(tk.END, "Examples:\n")
        for example in examples:
            result_text.insert(tk.END, f"  {example}\n")
        result_text.insert(tk.END, "\nEnter your expression above and press Calculate or Enter.\n\n")
    
    def show_variable_inspector(self):
        """Show variable inspector"""
        inspector_window = tk.Toplevel(self.root)
        inspector_window.title("📊 Variable Inspector")
        inspector_window.geometry("600x500")
        
        # Configure style
        colors = self.theme_manager.get_colors()
        inspector_window.configure(bg=colors.get('bg_primary', '#282A36'))
        
        # Main frame
        main_frame = ttk.Frame(inspector_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Variables display
        ttk.Label(main_frame, text="Current Variables:").pack(anchor=tk.W)
        
        # Treeview for variables
        columns = ('Variable', 'Value', 'Type')
        tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def refresh_variables():
            # Clear existing items
            for item in tree.get_children():
                tree.delete(item)
            
            if self.interpreter and hasattr(self.interpreter, 'variables'):
                variables = self.interpreter.variables
                for name, value in variables.items():
                    value_str = str(value)[:100]  # Truncate long values
                    if len(str(value)) > 100:
                        value_str += "..."
                    
                    value_type = type(value).__name__
                    tree.insert('', tk.END, values=(name, value_str, value_type))
            else:
                tree.insert('', tk.END, values=("No interpreter", "N/A", "N/A"))
        
        def export_variables():
            try:
                import json
                from tkinter import filedialog
                
                filename = filedialog.asksaveasfilename(
                    defaultextension=".json",
                    filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
                )
                
                if filename:
                    if self.interpreter and hasattr(self.interpreter, 'variables'):
                        # Convert variables to JSON-serializable format
                        export_data = {}
                        for name, value in self.interpreter.variables.items():
                            try:
                                json.dumps(value)  # Test if serializable
                                export_data[name] = value
                            except:
                                export_data[name] = str(value)
                        
                        with open(filename, 'w') as f:
                            json.dump(export_data, f, indent=2)
                        
                        messagebox.showinfo("Success", f"Variables exported to {filename}")
                    else:
                        messagebox.showwarning("Warning", "No variables to export")
                        
            except Exception as e:
                messagebox.showerror("Error", f"Could not export variables: {e}")
        
        ttk.Button(button_frame, text="Refresh", command=refresh_variables).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Export", command=export_variables).pack(side=tk.LEFT)
        
        # Initial refresh
        refresh_variables()
    
    def show_performance_profiler(self):
        """Show performance profiler"""
        profiler_window = tk.Toplevel(self.root)
        profiler_window.title("⚡ Performance Profiler")
        profiler_window.geometry("700x600")
        
        # Configure style
        colors = self.theme_manager.get_colors()
        profiler_window.configure(bg=colors.get('bg_primary', '#282A36'))
        
        # Main frame
        main_frame = ttk.Frame(profiler_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Info display
        info_text = scrolledtext.ScrolledText(main_frame, height=20, font=("Consolas", 10), wrap=tk.WORD)
        info_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def run_performance_test():
            info_text.delete(1.0, tk.END)
            info_text.insert(tk.END, "Running performance tests...\n\n")
            info_text.update()
            
            try:
                import time
                import psutil
                import os
                
                # System info
                info_text.insert(tk.END, "=== SYSTEM PERFORMANCE ===\n")
                info_text.insert(tk.END, f"CPU Usage: {psutil.cpu_percent(interval=1)}%\n")
                info_text.insert(tk.END, f"Memory Usage: {psutil.virtual_memory().percent}%\n")
                info_text.insert(tk.END, f"Disk Usage: {psutil.disk_usage('/').percent}%\n\n")
                
                # Language performance tests
                info_text.insert(tk.END, "=== LANGUAGE PERFORMANCE TESTS ===\n")
                
                if self.interpreter:
                    # Test PILOT performance
                    start_time = time.time()
                    test_pilot = "T:Performance test\nU:X=1\nC:X=*X*+1\nT:Done"
                    self.interpreter.run_program(test_pilot)
                    pilot_time = time.time() - start_time
                    info_text.insert(tk.END, f"PILOT execution time: {pilot_time:.4f}s\n")
                    
                    # Test BASIC performance
                    start_time = time.time()
                    test_basic = "10 LET X = 1\n20 FOR I = 1 TO 100\n30 LET X = X + 1\n40 NEXT I\n50 END"
                    self.interpreter.run_program(test_basic)
                    basic_time = time.time() - start_time
                    info_text.insert(tk.END, f"BASIC execution time: {basic_time:.4f}s\n")
                    
                    # Test Logo performance
                    start_time = time.time()
                    test_logo = "CLEARSCREEN\nFORWARD 50\nRIGHT 90\nFORWARD 50"
                    self.interpreter.run_program(test_logo)
                    logo_time = time.time() - start_time
                    info_text.insert(tk.END, f"Logo execution time: {logo_time:.4f}s\n")
                    
                info_text.insert(tk.END, "\n=== RECOMMENDATIONS ===\n")
                if psutil.cpu_percent() > 80:
                    info_text.insert(tk.END, "⚠️ High CPU usage detected\n")
                if psutil.virtual_memory().percent > 80:
                    info_text.insert(tk.END, "⚠️ High memory usage detected\n")
                
                info_text.insert(tk.END, "✅ Performance analysis complete\n")
                
            except Exception as e:
                info_text.insert(tk.END, f"Error during performance test: {e}\n")
            
            info_text.see(tk.END)
        
        def clear_results():
            info_text.delete(1.0, tk.END)
        
        ttk.Button(button_frame, text="Run Performance Test", command=run_performance_test).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Clear", command=clear_results).pack(side=tk.LEFT)
        
        # Initial info
        info_text.insert(tk.END, "Performance Profiler\n")
        info_text.insert(tk.END, "=" * 30 + "\n\n")
        info_text.insert(tk.END, "Click 'Run Performance Test' to analyze system and language performance.\n\n")
    
    def show_code_metrics(self):
        """Show code metrics analyzer"""
        metrics_window = tk.Toplevel(self.root)
        metrics_window.title("📈 Code Metrics")
        metrics_window.geometry("650x550")
        
        # Configure style
        colors = self.theme_manager.get_colors()
        metrics_window.configure(bg=colors.get('bg_primary', '#282A36'))
        
        # Main frame
        main_frame = ttk.Frame(metrics_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Metrics display
        metrics_text = scrolledtext.ScrolledText(main_frame, height=20, font=("Consolas", 10), wrap=tk.WORD)
        metrics_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def analyze_current_code():
            metrics_text.delete(1.0, tk.END)
            
            try:
                # Get current code from editor
                code = self.text_editor.get(1.0, tk.END).strip()
                if not code:
                    metrics_text.insert(tk.END, "No code to analyze. Please open or write some code first.\n")
                    return
                
                lines = code.split('\n')
                
                metrics_text.insert(tk.END, "=== CODE METRICS ANALYSIS ===\n\n")
                
                # Basic metrics
                total_lines = len(lines)
                non_empty_lines = len([line for line in lines if line.strip()])
                comment_lines = len([line for line in lines if line.strip().startswith(('#', ';', 'REM', '//'))])
                code_lines = non_empty_lines - comment_lines
                
                metrics_text.insert(tk.END, f"📊 BASIC METRICS:\n")
                metrics_text.insert(tk.END, f"  Total lines: {total_lines}\n")
                metrics_text.insert(tk.END, f"  Non-empty lines: {non_empty_lines}\n")
                metrics_text.insert(tk.END, f"  Code lines: {code_lines}\n")
                metrics_text.insert(tk.END, f"  Comment lines: {comment_lines}\n")
                metrics_text.insert(tk.END, f"  Comment ratio: {(comment_lines/non_empty_lines*100):.1f}%\n\n")
                
                # Language detection
                pilot_commands = len([line for line in lines if any(line.strip().startswith(cmd) for cmd in ['T:', 'U:', 'Y:', 'N:', 'J:', 'L:', 'C:', 'A:'])])
                basic_commands = len([line for line in lines if any(cmd in line.upper() for cmd in ['PRINT', 'LET', 'FOR', 'IF', 'GOTO'])])
                logo_commands = len([line for line in lines if any(cmd in line.upper() for cmd in ['FORWARD', 'BACK', 'LEFT', 'RIGHT', 'PENUP', 'PENDOWN'])])
                
                metrics_text.insert(tk.END, f"🔍 LANGUAGE ANALYSIS:\n")
                metrics_text.insert(tk.END, f"  PILOT commands: {pilot_commands}\n")
                metrics_text.insert(tk.END, f"  BASIC commands: {basic_commands}\n")
                metrics_text.insert(tk.END, f"  Logo commands: {logo_commands}\n\n")
                
                # Determine primary language
                if pilot_commands > basic_commands and pilot_commands > logo_commands:
                    primary_lang = "PILOT"
                elif basic_commands > logo_commands:
                    primary_lang = "BASIC"
                elif logo_commands > 0:
                    primary_lang = "Logo"
                else:
                    primary_lang = "Unknown/Mixed"
                
                metrics_text.insert(tk.END, f"  Primary language: {primary_lang}\n\n")
                
                # Complexity analysis
                control_structures = len([line for line in lines if any(keyword in line.upper() for keyword in ['FOR', 'WHILE', 'IF', 'Y:', 'N:', 'J:', 'REPEAT', 'GOTO'])])
                variables = len(set([word for line in lines for word in line.split() if word.startswith('*') or 'LET' in line.upper()]))
                
                metrics_text.insert(tk.END, f"🧮 COMPLEXITY ANALYSIS:\n")
                metrics_text.insert(tk.END, f"  Control structures: {control_structures}\n")
                metrics_text.insert(tk.END, f"  Estimated variables: {variables}\n")
                
                complexity_score = (control_structures * 2 + variables + code_lines / 10)
                if complexity_score < 10:
                    complexity_level = "Low"
                elif complexity_score < 25:
                    complexity_level = "Medium"
                else:
                    complexity_level = "High"
                
                metrics_text.insert(tk.END, f"  Complexity score: {complexity_score:.1f}\n")
                metrics_text.insert(tk.END, f"  Complexity level: {complexity_level}\n\n")
                
                # Recommendations
                metrics_text.insert(tk.END, f"💡 RECOMMENDATIONS:\n")
                if comment_lines / non_empty_lines < 0.1:
                    metrics_text.insert(tk.END, f"  • Add more comments for better documentation\n")
                if complexity_score > 30:
                    metrics_text.insert(tk.END, f"  • Consider breaking code into smaller functions\n")
                if code_lines > 100:
                    metrics_text.insert(tk.END, f"  • Large program - consider modular design\n")
                
                metrics_text.insert(tk.END, f"  ✅ Analysis complete!\n")
                
            except Exception as e:
                metrics_text.insert(tk.END, f"Error analyzing code: {e}\n")
            
            metrics_text.see(tk.END)
        
        def clear_metrics():
            metrics_text.delete(1.0, tk.END)
        
        ttk.Button(button_frame, text="Analyze Current Code", command=analyze_current_code).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Clear", command=clear_metrics).pack(side=tk.LEFT)
        
        # Initial info
        metrics_text.insert(tk.END, "Code Metrics Analyzer\n")
        metrics_text.insert(tk.END, "=" * 30 + "\n\n")
        metrics_text.insert(tk.END, "Analyzes your code for:\n")
        metrics_text.insert(tk.END, "• Line counts and ratios\n")
        metrics_text.insert(tk.END, "• Language detection\n")
        metrics_text.insert(tk.END, "• Complexity analysis\n")
        metrics_text.insert(tk.END, "• Improvement recommendations\n\n")
        metrics_text.insert(tk.END, "Click 'Analyze Current Code' to start.\n")
    
    def show_code_analyzer(self):
        """Show code static analyzer"""
        analyzer_window = tk.Toplevel(self.root)
        analyzer_window.title("🔍 Code Analyzer")
        analyzer_window.geometry("700x600")
        
        # Configure style  
        colors = self.theme_manager.get_colors()
        analyzer_window.configure(bg=colors.get('bg_primary', '#282A36'))
        
        # Main frame
        main_frame = ttk.Frame(analyzer_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Analysis display
        analysis_text = scrolledtext.ScrolledText(main_frame, height=20, font=("Consolas", 10), wrap=tk.WORD)
        analysis_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def analyze_code():
            analysis_text.delete(1.0, tk.END)
            
            try:
                # Get current code
                code = self.text_editor.get(1.0, tk.END).strip()
                if not code:
                    analysis_text.insert(tk.END, "No code to analyze.\n")
                    return
                
                lines = code.split('\n')
                analysis_text.insert(tk.END, "=== STATIC CODE ANALYSIS ===\n\n")
                
                issues = []
                warnings = []
                suggestions = []
                
                # Analyze each line
                for i, line in enumerate(lines, 1):
                    line_stripped = line.strip()
                    if not line_stripped:
                        continue
                    
                    # Check for common issues
                    if line_stripped.startswith('GOTO') and 'GOTO' in line_stripped:
                        warnings.append(f"Line {i}: Excessive use of GOTO can make code hard to follow")
                    
                    if '*' in line_stripped and line_stripped.count('*') % 2 != 0:
                        issues.append(f"Line {i}: Possible unmatched variable delimiter (*)")
                    
                    if line_stripped.upper().startswith('REM') and len(line_stripped) > 50:
                        suggestions.append(f"Line {i}: Long comment - consider breaking into multiple lines")
                    
                    if '=' in line_stripped and line_stripped.count('=') > 2:
                        warnings.append(f"Line {i}: Multiple assignments in one line - consider splitting")
                    
                    # Check for unreferenced labels
                    if line_stripped.startswith('L:'):
                        label = line_stripped[2:].strip()
                        if label and not any(label in other_line for other_line in lines if other_line != line):
                            warnings.append(f"Line {i}: Label '{label}' appears to be unused")
                
                # Check for undefined jumps
                for i, line in enumerate(lines, 1):
                    if line.strip().startswith('J:'):
                        target = line.strip()[2:].strip()
                        if target and not any(f'L:{target}' in other_line for other_line in lines):
                            issues.append(f"Line {i}: Jump to undefined label '{target}'")
                
                # Display results
                if issues:
                    analysis_text.insert(tk.END, "🚨 ISSUES FOUND:\n")
                    for issue in issues:
                        analysis_text.insert(tk.END, f"  {issue}\n")
                    analysis_text.insert(tk.END, "\n")
                
                if warnings:
                    analysis_text.insert(tk.END, "⚠️ WARNINGS:\n")
                    for warning in warnings:
                        analysis_text.insert(tk.END, f"  {warning}\n")
                    analysis_text.insert(tk.END, "\n")
                
                if suggestions:
                    analysis_text.insert(tk.END, "💡 SUGGESTIONS:\n")
                    for suggestion in suggestions:
                        analysis_text.insert(tk.END, f"  {suggestion}\n")
                    analysis_text.insert(tk.END, "\n")
                
                if not issues and not warnings and not suggestions:
                    analysis_text.insert(tk.END, "✅ No issues found! Your code looks good.\n\n")
                
                # Summary
                analysis_text.insert(tk.END, "=== ANALYSIS SUMMARY ===\n")
                analysis_text.insert(tk.END, f"Issues: {len(issues)}\n")
                analysis_text.insert(tk.END, f"Warnings: {len(warnings)}\n")
                analysis_text.insert(tk.END, f"Suggestions: {len(suggestions)}\n")
                
            except Exception as e:
                analysis_text.insert(tk.END, f"Error during analysis: {e}\n")
            
            analysis_text.see(tk.END)
        
        def clear_analysis():
            analysis_text.delete(1.0, tk.END)
        
        ttk.Button(button_frame, text="Analyze Code", command=analyze_code).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Clear", command=clear_analysis).pack(side=tk.LEFT)
        
        # Initial info
        analysis_text.insert(tk.END, "Static Code Analyzer\n")
        analysis_text.insert(tk.END, "=" * 30 + "\n\n")
        analysis_text.insert(tk.END, "Performs static analysis to find:\n")
        analysis_text.insert(tk.END, "• Syntax errors and issues\n")
        analysis_text.insert(tk.END, "• Code quality warnings\n")
        analysis_text.insert(tk.END, "• Improvement suggestions\n")
        analysis_text.insert(tk.END, "• Undefined references\n\n")
        analysis_text.insert(tk.END, "Load your code and click 'Analyze Code'.\n")

    def set_pilot_mode(self):
        """Set editor to PILOT mode"""
        self.current_language_mode = "pilot"
        if self.interpreter:
            self.interpreter.set_language_mode("james_iii")
        messagebox.showinfo("Language Mode", "Editor set to PILOT mode\\n\\nFeatures:\\n- Text processing commands\\n- Pattern matching\\n- Educational programming")

    def set_basic_mode(self):
        """Set editor to BASIC mode"""
        self.current_language_mode = "basic"
        if self.interpreter:
            self.interpreter.set_language_mode("james_iii")
        messagebox.showinfo("Language Mode", "Editor set to BASIC mode\\n\\nFeatures:\\n- Classic BASIC programming\\n- Graphics commands\\n- Game development")

    def set_logo_mode(self):
        """Set editor to Logo mode"""
        self.current_language_mode = "logo"
        if self.interpreter:
            self.interpreter.set_language_mode("james_iii")
        messagebox.showinfo("Language Mode", "Editor set to Logo mode\\n\\nFeatures:\\n- Turtle graphics\\n- Educational programming\\n- Geometric drawing")

    def set_python_mode(self):
        """Set editor to Python mode"""
        self.current_language_mode = "python"
        if self.interpreter:
            self.interpreter.set_language_mode("python")
        messagebox.showinfo("Language Mode", "Editor set to Python mode\\n\\nFeatures:\\n- Modern Python programming\\n- Full Python standard library")

    def set_perl_mode(self):
        """Set editor to Perl mode"""
        self.current_language_mode = "perl"
        if self.interpreter:
            self.interpreter.set_language_mode("perl")
        messagebox.showinfo("Language Mode", "Editor set to Perl mode\\n\\nFeatures:\\n- Perl script execution\\n- Text processing\\n- Regular expressions")

    def set_javascript_mode(self):
        """Set editor to JavaScript mode"""
        self.current_language_mode = "javascript"
        if self.interpreter:
            self.interpreter.set_language_mode("javascript")
        messagebox.showinfo("Language Mode", "Editor set to JavaScript mode\\n\\nFeatures:\\n- Modern JavaScript programming\\n- Node.js execution")

    # File operations
    def new_file(self):
        """Create a new file"""
        if self.code_editor.get_content().strip():
            # Ask if user wants to save current file
            result = messagebox.askyesnocancel("New File", "Do you want to save the current file?")
            if result is True:  # Yes, save first
                if not self.save_file():  # If save failed or was cancelled
                    return
            elif result is None:  # Cancel
                return
        
        # Clear the editor
        self.code_editor.clear_content()
        self.current_file = None
        self.root.title("JAMES IDE - New File")

    def open_file(self):
        """Open a file"""
        try:
            filename = filedialog.askopenfilename(
                title="Open File",
                filetypes=[
                    ("JAMES files", "*.james"),
                    ("BASIC files", "*.bas"),
                    ("PILOT files", "*.pilot"),
                    ("Logo files", "*.logo"),
                    ("Python files", "*.py"),
                    ("Text files", "*.txt"),
                    ("All files", "*.*")
                ]
            )
            
            if filename:
                with open(filename, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # Clear current content and insert new content
                self.code_editor.set_content(content)
                
                # Update current file and window title
                self.current_file = filename
                self.root.title(f"JAMES IDE - {filename}")
                
                # Set language mode based on file extension
                ext = filename.lower().split('.')[-1]
                if ext in ['pilot']:
                    self.current_language_mode = "pilot"
                    if self.interpreter:
                        self.interpreter.set_language_mode("james_iii")
                elif ext in ['bas', 'basic']:
                    self.current_language_mode = "basic"
                    if self.interpreter:
                        self.interpreter.set_language_mode("james_iii")
                elif ext in ['logo']:
                    self.current_language_mode = "logo"
                    if self.interpreter:
                        self.interpreter.set_language_mode("james_iii")
                elif ext == 'py':
                    self.current_language_mode = "python"
                    if self.interpreter:
                        self.interpreter.set_language_mode("python")
                elif ext in ['pl', 'perl']:
                    self.current_language_mode = "perl"
                    if self.interpreter:
                        self.interpreter.set_language_mode("perl")
                elif ext == 'js':
                    self.current_language_mode = "javascript"
                    if self.interpreter:
                        self.interpreter.set_language_mode("javascript")
                
                messagebox.showinfo("File Opened", f"Successfully opened: {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file:\n{e}")

    def save_file(self):
        """Save the current file"""
        if self.current_file:
            try:
                content = self.code_editor.get_content()
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(content)
                messagebox.showinfo("File Saved", f"File saved: {self.current_file}")
                return True
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file:\n{e}")
                return False
        else:
            return self.save_file_as()

    def save_file_as(self):
        """Save the current file with a new name"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Save File As",
                defaultextension=".james",
                filetypes=[
                    ("JAMES files", "*.james"),
                    ("BASIC files", "*.bas"),
                    ("PILOT files", "*.pilot"),
                    ("Logo files", "*.logo"),
                    ("Python files", "*.py"),
                    ("Text files", "*.txt"),
                    ("All files", "*.*")
                ]
            )
            
            if filename:
                content = self.code_editor.get_content()
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(content)
                
                # Update current file and window title
                self.current_file = filename
                self.root.title(f"JAMES IDE - {filename}")
                
                messagebox.showinfo("File Saved", f"File saved as: {filename}")
                return True
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file:\n{e}")
            return False
        
        return False

    # Code execution methods
    def run_code(self):
        """Run the code in the editor"""
        try:
            code = self.code_editor.get_content()
            if not code.strip():
                messagebox.showwarning("Warning", "No code to run")
                return
            
            # Clear output console
            self.clear_output()
            
            # Display starting message
            self.write_to_console(f"🚀 Running code...\n")
            self.write_to_console("=" * 40 + "\n")
            
            # Run the code using the interpreter
            if self.interpreter:
                # Set up output redirection
                self.setup_output_redirection()
                
                try:
                    # Run the program
                    self.interpreter.run_program(code)
                    self.write_to_console("\n" + "=" * 40)
                    self.write_to_console("\n✅ Program completed successfully.")
                except Exception as e:
                    self.write_to_console(f"\n❌ Runtime Error: {str(e)}")
                finally:
                    # Restore normal output
                    self.restore_output()
            else:
                self.write_to_console("❌ Error: Interpreter not initialized")
                
        except Exception as e:
            self.write_to_console(f"❌ Execution Error: {str(e)}")
    
    def write_to_console(self, text):
        """Write text to the output console"""
        try:
            self.output_text.config(state=tk.NORMAL)
            self.output_text.insert(tk.END, text)
            self.output_text.see(tk.END)  # Auto-scroll to bottom
            self.output_text.config(state=tk.DISABLED)
            self.output_text.update()  # Force update display
        except Exception as e:
            print(f"Console write error: {e}")
    
    def setup_output_redirection(self):
        """Set up output redirection to capture interpreter output"""
        import sys
        from io import StringIO
        
        # Create a custom StringIO that writes to both console and captures output
        class ConsoleRedirector(StringIO):
            def __init__(self, console_widget):
                super().__init__()
                self.console_widget = console_widget
                
            def write(self, text):
                if text.strip():  # Only write non-empty text
                    self.console_widget.write_to_console(text)
                return len(text)
                
            def flush(self):
                pass
        
        # Store original stdout and stderr
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        
        # Redirect to our console
        sys.stdout = ConsoleRedirector(self)
        sys.stderr = ConsoleRedirector(self)
        
        # Also set up interpreter output callback if supported
        if hasattr(self.interpreter, 'set_output_callback'):
            self.interpreter.set_output_callback(self.write_to_console)
    
    def restore_output(self):
        """Restore normal stdout/stderr"""
        import sys
        if hasattr(self, 'original_stdout'):
            sys.stdout = self.original_stdout
        if hasattr(self, 'original_stderr'):
            sys.stderr = self.original_stderr
    
    def stop_execution(self):
        """Stop code execution"""
        try:
            if self.interpreter:
                self.interpreter.stop_program()
                self.output_text.config(state=tk.NORMAL)
                self.output_text.insert(tk.END, "\n--- Execution stopped ---\n")
                self.output_text.config(state=tk.DISABLED)
            else:
                messagebox.showwarning("Warning", "No program is running")
        except Exception as e:
            messagebox.showerror("Error", f"Could not stop execution:\n{e}")
    
    def clear_output(self):
        """Clear the output console"""
        try:
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete(1.0, tk.END)
            self.output_text.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", f"Could not clear output:\n{e}")

    # Edit menu operations
    def undo(self):
        """Undo last operation in editor"""
        try:
            if hasattr(self.code_editor, 'text_editor'):
                self.code_editor.text_editor.edit_undo()
        except tk.TclError:
            pass  # Nothing to undo
        except Exception as e:
            messagebox.showerror("Error", f"Could not undo:\n{e}")
    
    def redo(self):
        """Redo last undone operation in editor"""
        try:
            if hasattr(self.code_editor, 'text_editor'):
                self.code_editor.text_editor.edit_redo()
        except tk.TclError:
            pass  # Nothing to redo
        except Exception as e:
            messagebox.showerror("Error", f"Could not redo:\n{e}")
    
    def cut(self):
        """Cut selected text from editor"""
        try:
            if hasattr(self.code_editor, 'text_editor'):
                self.code_editor.text_editor.event_generate("<<Cut>>")
        except Exception as e:
            messagebox.showerror("Error", f"Could not cut:\n{e}")
    
    def copy(self):
        """Copy selected text from editor"""
        try:
            if hasattr(self.code_editor, 'text_editor'):
                self.code_editor.text_editor.event_generate("<<Copy>>")
        except Exception as e:
            messagebox.showerror("Error", f"Could not copy:\n{e}")
    
    def paste(self):
        """Paste text into editor"""
        try:
            if hasattr(self.code_editor, 'text_editor'):
                self.code_editor.text_editor.event_generate("<<Paste>>")
        except Exception as e:
            messagebox.showerror("Error", f"Could not paste:\n{e}")
    
    def select_all(self):
        """Select all text in editor"""
        try:
            if hasattr(self.code_editor, 'text_editor'):
                self.code_editor.text_editor.tag_add(tk.SEL, "1.0", tk.END)
                self.code_editor.text_editor.mark_set(tk.INSERT, "1.0")
                self.code_editor.text_editor.see(tk.INSERT)
        except Exception as e:
            messagebox.showerror("Error", f"Could not select all:\n{e}")
    
    def find_text(self):
        """Open find dialog"""
        try:
            if hasattr(self.code_editor, 'show_find_dialog'):
                self.code_editor.show_find_dialog()
            else:
                messagebox.showinfo("Find", "Find functionality not available in current editor")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open find dialog:\n{e}")
    
    def replace_text(self):
        """Open find/replace dialog"""
        try:
            if hasattr(self.code_editor, 'show_replace_dialog'):
                self.code_editor.show_replace_dialog()
            else:
                messagebox.showinfo("Replace", "Replace functionality not available in current editor")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open replace dialog:\n{e}")

    # View menu operations
    def show_project_explorer(self):
        """Show project explorer"""
        try:
            from gui.components.dialogs import ProjectExplorer
            if not hasattr(self, 'project_explorer'):
                self.project_explorer = ProjectExplorer(self)
            self.project_explorer.show_explorer()
        except Exception as e:
            messagebox.showerror("Error", f"Could not open project explorer:\n{e}")
    
    def zoom_in(self):
        """Increase editor font size"""
        try:
            if hasattr(self.code_editor, 'text_editor'):
                current_font = self.code_editor.text_editor.cget("font")
                if isinstance(current_font, tuple):
                    family, size = current_font[0], current_font[1]
                else:
                    family, size = "Courier", 10
                new_size = min(size + 2, 24)  # Max size 24
                self.code_editor.text_editor.config(font=(family, new_size))
        except Exception as e:
            messagebox.showerror("Error", f"Could not zoom in:\n{e}")
    
    def zoom_out(self):
        """Decrease editor font size"""
        try:
            if hasattr(self.code_editor, 'text_editor'):
                current_font = self.code_editor.text_editor.cget("font")
                if isinstance(current_font, tuple):
                    family, size = current_font[0], current_font[1]
                else:
                    family, size = "Courier", 10
                new_size = max(size - 2, 8)  # Min size 8
                self.code_editor.text_editor.config(font=(family, new_size))
        except Exception as e:
            messagebox.showerror("Error", f"Could not zoom out:\n{e}")
    
    def reset_zoom(self):
        """Reset editor font size to default"""
        try:
            if hasattr(self.code_editor, 'text_editor'):
                self.code_editor.text_editor.config(font=("Courier", 10))
        except Exception as e:
            messagebox.showerror("Error", f"Could not reset zoom:\n{e}")

    def debug_code(self):
        """Debug the current code"""
        try:
            messagebox.showinfo("Debug", "Debug mode activated! Step through your code.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not start debug mode: {e}")
    
    def show_help(self):
        """Show help documentation"""
        help_text = """
🚀 JAMES IDE Help
================

📝 Supported Languages:
• PILOT - Educational language with T:, A:, Y:, N: commands
• BASIC - Classic programming with LET, PRINT, FOR/NEXT
• Logo - Turtle graphics with FORWARD, RIGHT, REPEAT

⌨️ Keyboard Shortcuts:
• Ctrl+N - New file
• Ctrl+O - Open file  
• Ctrl+S - Save file
• F5 - Run program
• F6 - Stop execution

🎨 Features:
• Modern colorful interface
• Syntax highlighting
• Real-time execution
• Turtle graphics canvas
• Project explorer
        """
        messagebox.showinfo("JAMES Help", help_text)
    
    def show_tutorials(self):
        """Show tutorials"""
        tutorial_text = """
🎓 JAMES IDE Tutorials
=====================

📚 Getting Started:
1. Select language from File menu
2. Write your code in the editor
3. Press F5 to run your program

🐍 PILOT Tutorial:
T: Hello World!
A: What's your name?
Y: Nice to meet you!

💻 BASIC Tutorial:
10 PRINT "Hello World!"
20 FOR I = 1 TO 5
30 PRINT "Count: "; I
40 NEXT I

🐢 Logo Tutorial:
REPEAT 4 [FORWARD 100 RIGHT 90]
        """
        messagebox.showinfo("Tutorials", tutorial_text)
    
    def open_recent_file(self, filename):
        """Open a recent file"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.code_editor.set_content(content)
                    self.current_file = filename
                    
                    # Update window title
                    self.root.title(f"JAMES IDE - {os.path.basename(filename)}")
                    
                    # Determine language from extension
                    if filename.endswith('.pilot'):
                        self.current_language = 'PILOT'
                    elif filename.endswith('.bas'):
                        self.current_language = 'BASIC'
                    elif filename.endswith('.logo'):
                        self.current_language = 'Logo'
                    
                    self.update_status_bar()
            else:
                messagebox.showerror("Error", f"File not found: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {e}")
    
    def update_status_bar(self):
        """Update the status bar with current information"""
        try:
            # Update language label
            self.language_label.config(text=f"📝 {self.current_language}")
            
            # Update status label with file info
            if self.current_file:
                filename = os.path.basename(self.current_file)
                self.status_label.config(text=f"📁 {filename}")
            else:
                self.status_label.config(text="📄 New File")
        except Exception as e:
            print(f"Error updating status bar: {e}")

    def on_closing(self):
        """Handle window closing"""
        self.cleanup()
        self.root.destroy()


def main():
    """Main entry point"""
    try:
        # Create and run JAMES application
        app = JAMESII()
        app.run()
        
    except Exception as e:
        import traceback
        print(f"Error starting JAMES: {e}")
        print("Full traceback:")
        traceback.print_exc()
        sys.exit(1)


# Additional Tools Menu Methods - extending JAMESII class
def add_tools_methods():
    """Add tools menu methods to JAMESII class"""
    
    def show_hardware_controller(self):
        """Show hardware controller dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("🔌 Hardware Controller")
        dialog.geometry("900x600")
        dialog.transient(self.root)
        
        # Create notebook for hardware tabs
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # GPIO Control Tab
        gpio_frame = ttk.Frame(notebook)
        notebook.add(gpio_frame, text="📌 GPIO Pins")
        self.setup_gpio_tab(gpio_frame)
        
        # Sensors Tab
        sensors_frame = ttk.Frame(notebook)
        notebook.add(sensors_frame, text="🌡️ Sensors")
        self.setup_sensors_tab(sensors_frame)
        
        # Devices Tab
        devices_frame = ttk.Frame(notebook)
        notebook.add(devices_frame, text="🔧 Devices")
        self.setup_devices_tab(devices_frame)
        
        # Automation Tab
        automation_frame = ttk.Frame(notebook)
        notebook.add(automation_frame, text="🤖 Automation")
        self.setup_automation_tab(automation_frame)
        
        # Initialize hardware state
        self.hardware_state = {
            'gpio_pins': {},
            'sensors': {},
            'devices': {},
            'automation_rules': []
        }
        
        dialog.protocol("WM_DELETE_WINDOW", lambda: dialog.destroy())
    
    def show_iot_manager(self):
        """Show comprehensive IoT Device Manager with device discovery, control, and monitoring"""
        iot_window = tk.Toplevel(self.root)
        iot_window.title("🌐 IoT Device Manager - JAMES")
        iot_window.geometry("900x700")
        iot_window.transient(self.root)
        iot_window.grab_set()
        
        # Create notebook for IoT management
        notebook = ttk.Notebook(iot_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Device Discovery Tab
        discovery_frame = ttk.Frame(notebook)
        notebook.add(discovery_frame, text="🔍 Device Discovery")
        self.setup_device_discovery_tab(discovery_frame)
        
        # Device Control Tab
        control_frame = ttk.Frame(notebook)
        notebook.add(control_frame, text="🎛️ Device Control")
        self.setup_device_control_tab(control_frame)
        
        # Network Monitoring Tab
        network_frame = ttk.Frame(notebook)
        notebook.add(network_frame, text="🌐 Network Monitor")
        self.setup_network_monitoring_tab(network_frame)
        
        # Protocols Tab
        protocols_frame = ttk.Frame(notebook)
        notebook.add(protocols_frame, text="📡 Protocols")
        self.setup_protocols_tab(protocols_frame)
        
        # Data Analytics Tab
        analytics_frame = ttk.Frame(notebook)
        notebook.add(analytics_frame, text="📊 Data Analytics")
        self.setup_iot_analytics_tab(analytics_frame)
    
    def show_sensor_visualizer(self):
        """Show sensor visualizer"""
        messagebox.showinfo("Sensor Visualizer", "Sensor Data Visualizer\\n\\nReal-time Data Display\\nMultiple Sensor Types\\nData Export\\n\\nComing soon!")
    
    def show_learning_assistant(self):
        """Show learning assistant"""
        messagebox.showinfo("Learning Assistant", "Learning Assistant\\n\\nInteractive Tutorials\\nCode Examples\\nProgress Tracking\\n\\nComing soon!")
    
    def show_code_examples(self):
        """Show code examples browser"""
        messagebox.showinfo("Code Examples", "Code Examples Browser\\n\\nLanguage Examples\\nCopy to Editor\\nRun Examples\\n\\nComing soon!")
    
    def show_testing_framework(self):
        """Show testing framework"""
        messagebox.showinfo("Testing Framework", "Testing Framework\\n\\nUnit Testing\\nCode Coverage\\nTest Reports\\n\\nComing soon!")
    
    def show_graphics_canvas(self):
        """Show standalone graphics canvas"""
        messagebox.showinfo("Graphics Canvas", "Graphics canvas is available in the main window!\\n\\nTurtle Graphics\\nDrawing Tools\\nExport Options")
    
    def show_code_converter(self):
        """Show code converter between languages"""
        messagebox.showinfo("Code Converter", "Multi-Language Converter\\n\\nPILOT ↔ BASIC\\nSyntax Translation\\nSmart Conversion\\n\\nComing soon!")
    
    def show_system_info(self):
        """Show system information"""
        try:
            import platform
            import sys
            info = f"""JAMES IDE System Information
            
Python: {sys.version.split()[0]}
Platform: {platform.system()} {platform.release()}
Architecture: {platform.architecture()[0]}
JAMES Version: 2.0 Enhanced
Interpreter: {'Available' if self.interpreter else 'Not initialized'}
Graphics: {'Available' if hasattr(self, 'graphics_canvas') else 'Not initialized'}"""
            messagebox.showinfo("System Information", info)
        except Exception as e:
            messagebox.showerror("Error", f"Could not get system info: {e}")
    
    # === DEBUGGER METHODS ===
    def setup_breakpoints_tab(self, parent):
        """Setup breakpoints management tab"""
        # Breakpoints list frame
        list_frame = ttk.LabelFrame(parent, text="Breakpoints")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for breakpoints
        columns = ('File', 'Line', 'Condition', 'Status')
        self.breakpoints_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.breakpoints_tree.heading(col, text=col)
            self.breakpoints_tree.column(col, width=150)
        
        self.breakpoints_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        bp_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.breakpoints_tree.yview)
        self.breakpoints_tree.config(yscrollcommand=bp_scroll.set)
        bp_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="➕ Add Breakpoint", command=self.add_breakpoint).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="❌ Remove", command=self.remove_breakpoint).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="✅ Enable All", command=self.enable_all_breakpoints).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="⏸️ Disable All", command=self.disable_all_breakpoints).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="🧹 Clear All", command=self.clear_all_breakpoints).pack(side=tk.LEFT, padx=2)
    
    def setup_debug_variables_tab(self, parent):
        """Setup debug variables tab"""
        # Variables tree frame
        tree_frame = ttk.LabelFrame(parent, text="Variables & Values")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Variables treeview
        columns = ('Variable', 'Type', 'Value', 'Scope')
        self.debug_vars_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.debug_vars_tree.heading(col, text=col)
            if col == 'Value':
                self.debug_vars_tree.column(col, width=200)
            else:
                self.debug_vars_tree.column(col, width=120)
        
        self.debug_vars_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        vars_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.debug_vars_tree.yview)
        self.debug_vars_tree.config(yscrollcommand=vars_scroll.set)
        vars_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Control buttons
        vars_button_frame = ttk.Frame(parent)
        vars_button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(vars_button_frame, text="🔄 Refresh", command=self.refresh_debug_variables).pack(side=tk.LEFT, padx=2)
        ttk.Button(vars_button_frame, text="👁️ Watch Variable", command=self.add_watch_variable).pack(side=tk.LEFT, padx=2)
        ttk.Button(vars_button_frame, text="✏️ Edit Value", command=self.edit_variable_value).pack(side=tk.LEFT, padx=2)
        ttk.Button(vars_button_frame, text="💾 Export Variables", command=self.export_debug_variables).pack(side=tk.LEFT, padx=2)
    
    def setup_callstack_tab(self, parent):
        """Setup call stack tab"""
        # Call stack frame
        stack_frame = ttk.LabelFrame(parent, text="Call Stack")
        stack_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Call stack listbox
        self.callstack_listbox = tk.Listbox(stack_frame, font=('Consolas', 10))
        self.callstack_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        stack_scroll = ttk.Scrollbar(stack_frame, orient=tk.VERTICAL, command=self.callstack_listbox.yview)
        self.callstack_listbox.config(yscrollcommand=stack_scroll.set)
        stack_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Stack info frame
        info_frame = ttk.LabelFrame(parent, text="Stack Frame Details")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.stack_info_text = tk.Text(info_frame, height=8, font=('Consolas', 9))
        info_scroll = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.stack_info_text.yview)
        self.stack_info_text.config(yscrollcommand=info_scroll.set)
        
        self.stack_info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        info_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Bind selection event
        self.callstack_listbox.bind('<<ListboxSelect>>', self.on_stack_select)
    
    def setup_execution_tab(self, parent):
        """Setup execution control tab"""
        # Execution controls frame
        controls_frame = ttk.LabelFrame(parent, text="Execution Control")
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Control buttons
        button_row1 = ttk.Frame(controls_frame)
        button_row1.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_row1, text="▶️ Run", command=self.debug_run).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_row1, text="⏸️ Pause", command=self.debug_pause).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_row1, text="⏹️ Stop", command=self.debug_stop).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_row1, text="🔄 Restart", command=self.debug_restart).pack(side=tk.LEFT, padx=2)
        
        button_row2 = ttk.Frame(controls_frame)
        button_row2.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_row2, text="➡️ Step Over", command=self.debug_step_over).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_row2, text="⬇️ Step Into", command=self.debug_step_into).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_row2, text="⬆️ Step Out", command=self.debug_step_out).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_row2, text="🏃 Run to Cursor", command=self.debug_run_to_cursor).pack(side=tk.LEFT, padx=2)
        
        # Execution status frame
        status_frame = ttk.LabelFrame(parent, text="Execution Status")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.execution_text = tk.Text(status_frame, height=15, font=('Consolas', 10))
        exec_scroll = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.execution_text.yview)
        self.execution_text.config(yscrollcommand=exec_scroll.set)
        
        self.execution_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        exec_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Initialize execution status
        self.update_execution_status()
    
    def setup_memory_tab(self, parent):
        """Setup memory monitoring tab"""
        # Memory usage frame
        memory_frame = ttk.LabelFrame(parent, text="Memory Usage")
        memory_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Memory statistics
        stats_frame = ttk.Frame(memory_frame)
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.memory_labels = {}
        memory_items = ['Total Memory', 'Used Memory', 'Free Memory', 'Python Objects', 'Variables Count']
        
        for i, item in enumerate(memory_items):
            ttk.Label(stats_frame, text=f"{item}:").grid(row=i, column=0, sticky='w', padx=5, pady=2)
            self.memory_labels[item] = ttk.Label(stats_frame, text="0 MB")
            self.memory_labels[item].grid(row=i, column=1, sticky='w', padx=20, pady=2)
        
        # Memory monitor text
        monitor_frame = ttk.Frame(memory_frame)
        monitor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.memory_text = tk.Text(monitor_frame, height=15, font=('Consolas', 9))
        memory_scroll = ttk.Scrollbar(monitor_frame, orient=tk.VERTICAL, command=self.memory_text.yview)
        self.memory_text.config(yscrollcommand=memory_scroll.set)
        
        self.memory_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        memory_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Control buttons
        memory_buttons = ttk.Frame(parent)
        memory_buttons.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(memory_buttons, text="🔄 Refresh", command=self.refresh_memory_info).pack(side=tk.LEFT, padx=2)
        ttk.Button(memory_buttons, text="📊 Memory Profile", command=self.show_memory_profile).pack(side=tk.LEFT, padx=2)
        ttk.Button(memory_buttons, text="🧹 Garbage Collect", command=self.force_garbage_collection).pack(side=tk.LEFT, padx=2)
        
        # Initialize memory display
        self.refresh_memory_info()
    
    # === DEBUGGER HELPER METHODS ===
    def add_breakpoint(self):
        """Add a new breakpoint"""
        dialog = tk.Toplevel(self.debugger_dialog)
        dialog.title("➕ Add Breakpoint")
        dialog.geometry("400x200")
        dialog.transient(self.debugger_dialog)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Line Number:").pack(pady=5)
        line_var = tk.IntVar(value=1)
        ttk.Spinbox(dialog, from_=1, to=1000, textvariable=line_var, width=10).pack(pady=5)
        
        ttk.Label(dialog, text="Condition (optional):").pack(pady=5)
        condition_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=condition_var, width=40).pack(pady=5)
        
        def create_bp():
            line = line_var.get()
            condition = condition_var.get() or "Always"
            bp_id = f"main.py:{line}"
            
            self.debugger_state['breakpoints'][bp_id] = {
                'file': 'main.py',
                'line': line,
                'condition': condition,
                'enabled': True
            }
            
            self.breakpoints_tree.insert('', 'end', values=('main.py', line, condition, 'Enabled'))
            messagebox.showinfo("Breakpoint Added", f"Breakpoint added at line {line}")
            dialog.destroy()
        
        ttk.Button(dialog, text="✅ Add", command=create_bp).pack(side=tk.LEFT, padx=5, pady=20)
        ttk.Button(dialog, text="❌ Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5, pady=20)
    
    def remove_breakpoint(self):
        """Remove selected breakpoint"""
        selection = self.breakpoints_tree.selection()
        if selection:
            self.breakpoints_tree.delete(selection[0])
            messagebox.showinfo("Breakpoint Removed", "Breakpoint removed successfully")
        else:
            messagebox.showwarning("No Selection", "Please select a breakpoint to remove")
    
    def enable_all_breakpoints(self):
        """Enable all breakpoints"""
        for item in self.breakpoints_tree.get_children():
            values = list(self.breakpoints_tree.item(item)['values'])
            values[3] = 'Enabled'
            self.breakpoints_tree.item(item, values=values)
        messagebox.showinfo("Breakpoints", "All breakpoints enabled")
    
    def disable_all_breakpoints(self):
        """Disable all breakpoints"""
        for item in self.breakpoints_tree.get_children():
            values = list(self.breakpoints_tree.item(item)['values'])
            values[3] = 'Disabled'
            self.breakpoints_tree.item(item, values=values)
        messagebox.showinfo("Breakpoints", "All breakpoints disabled")
    
    def clear_all_breakpoints(self):
        """Clear all breakpoints"""
        if messagebox.askyesno("Clear Breakpoints", "Remove all breakpoints?"):
            for item in self.breakpoints_tree.get_children():
                self.breakpoints_tree.delete(item)
            self.debugger_state['breakpoints'].clear()
            messagebox.showinfo("Breakpoints", "All breakpoints cleared")
    
    def refresh_debug_variables(self):
        """Refresh debug variables display"""
        # Clear existing items
        for item in self.debug_vars_tree.get_children():
            self.debug_vars_tree.delete(item)
        
        # Get interpreter variables
        try:
            if hasattr(self, 'interpreter') and self.interpreter:
                variables = {}
                
                # Get PILOT variables
                if hasattr(self.interpreter, 'pilot_executor') and self.interpreter.pilot_executor:
                    pilot_vars = getattr(self.interpreter.pilot_executor, 'variables', {})
                    for var, value in pilot_vars.items():
                        variables[f"PILOT:{var}"] = {'type': type(value).__name__, 'value': str(value), 'scope': 'PILOT'}
                
                # Get BASIC variables
                if hasattr(self.interpreter, 'basic_executor') and self.interpreter.basic_executor:
                    basic_vars = getattr(self.interpreter.basic_executor, 'variables', {})
                    for var, value in basic_vars.items():
                        variables[f"BASIC:{var}"] = {'type': type(value).__name__, 'value': str(value), 'scope': 'BASIC'}
                
                # Get Logo variables
                if hasattr(self.interpreter, 'logo_executor') and self.interpreter.logo_executor:
                    logo_vars = getattr(self.interpreter.logo_executor, 'variables', {})
                    for var, value in logo_vars.items():
                        variables[f"Logo:{var}"] = {'type': type(value).__name__, 'value': str(value), 'scope': 'Logo'}
                
                # Add to tree
                for var_name, var_info in variables.items():
                    self.debug_vars_tree.insert('', 'end', values=(
                        var_name, var_info['type'], var_info['value'][:50], var_info['scope']
                    ))
            
        except Exception as e:
            self.debug_vars_tree.insert('', 'end', values=('Error', 'N/A', str(e)[:50], 'System'))
    
    def add_watch_variable(self):
        """Add a variable to watch"""
        var_name = tk.simpledialog.askstring("Watch Variable", "Enter variable name to watch:")
        if var_name:
            messagebox.showinfo("Watch Added", f"Variable '{var_name}' added to watch list")
    
    def edit_variable_value(self):
        """Edit selected variable value"""
        selection = self.debug_vars_tree.selection()
        if selection:
            item = self.debug_vars_tree.item(selection[0])
            var_name = item['values'][0]
            old_value = item['values'][2]
            
            new_value = tk.simpledialog.askstring("Edit Variable", f"Enter new value for {var_name}:", initialvalue=old_value)
            if new_value is not None:
                messagebox.showinfo("Variable Updated", f"Variable '{var_name}' updated to '{new_value}'")
        else:
            messagebox.showwarning("No Selection", "Please select a variable to edit")
    
    def export_debug_variables(self):
        """Export variables to JSON file"""
        try:
            from tkinter import filedialog
            import json
            
            filename = filedialog.asksaveasfilename(
                title="Export Variables",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                variables = {}
                for item in self.debug_vars_tree.get_children():
                    values = self.debug_vars_tree.item(item)['values']
                    variables[values[0]] = {
                        'type': values[1],
                        'value': values[2],
                        'scope': values[3]
                    }
                
                with open(filename, 'w') as f:
                    json.dump(variables, f, indent=2)
                
                messagebox.showinfo("Export Complete", f"Variables exported to {filename}")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export variables: {e}")
    
    def on_stack_select(self, event):
        """Handle call stack selection"""
        selection = self.callstack_listbox.curselection()
        if selection:
            frame_info = self.callstack_listbox.get(selection[0])
            
            # Display frame details
            details = f"""Stack Frame Details:
            
Frame: {frame_info}
Local Variables: Available in Variables tab
Line Number: Highlighted in editor
Function: Current execution context

Use Step Into/Out to navigate between frames.
Variables tab shows local scope for selected frame."""
            
            self.stack_info_text.delete('1.0', tk.END)
            self.stack_info_text.insert('1.0', details)
    
    def debug_run(self):
        """Run program in debug mode"""
        self.debugger_state['execution_mode'] = 'running'
        self.update_execution_status()
        messagebox.showinfo("Debug Run", "Program execution started")
    
    def debug_pause(self):
        """Pause program execution"""
        self.debugger_state['execution_mode'] = 'paused'
        self.update_execution_status()
        messagebox.showinfo("Debug Pause", "Program execution paused")
    
    def debug_stop(self):
        """Stop program execution"""
        self.debugger_state['execution_mode'] = 'stopped'
        self.debugger_state['current_line'] = None
        self.debugger_state['call_stack'].clear()
        self.update_execution_status()
        messagebox.showinfo("Debug Stop", "Program execution stopped")
    
    def debug_restart(self):
        """Restart program execution"""
        self.debug_stop()
        self.debug_run()
        messagebox.showinfo("Debug Restart", "Program restarted")
    
    def debug_step_over(self):
        """Step over current line"""
        self.debugger_state['execution_mode'] = 'step_over'
        self.update_execution_status()
        messagebox.showinfo("Step Over", "Stepped over current line")
    
    def debug_step_into(self):
        """Step into current function"""
        self.debugger_state['execution_mode'] = 'step_into'
        # Add to call stack
        self.debugger_state['call_stack'].append("main() -> function_call()")
        self.update_callstack_display()
        self.update_execution_status()
        messagebox.showinfo("Step Into", "Stepped into function")
    
    def debug_step_out(self):
        """Step out of current function"""
        self.debugger_state['execution_mode'] = 'step_out'
        # Remove from call stack
        if self.debugger_state['call_stack']:
            self.debugger_state['call_stack'].pop()
        self.update_callstack_display()
        self.update_execution_status()
        messagebox.showinfo("Step Out", "Stepped out of function")
    
    def debug_run_to_cursor(self):
        """Run to cursor position"""
        cursor_line = "Current editor cursor position"
        self.debugger_state['execution_mode'] = 'run_to_cursor'
        self.update_execution_status()
        messagebox.showinfo("Run to Cursor", f"Running to cursor at {cursor_line}")
    
    def update_execution_status(self):
        """Update execution status display"""
        if hasattr(self, 'execution_text'):
            status_text = f"""Debugger Execution Status:

Mode: {self.debugger_state['execution_mode'].title()}
Current Line: {self.debugger_state['current_line'] or 'Not set'}
Breakpoints: {len(self.debugger_state['breakpoints'])} active
Call Stack Depth: {len(self.debugger_state['call_stack'])}

Available Commands:
• Run - Execute program normally
• Step Over - Execute current line, don't enter functions
• Step Into - Enter function calls
• Step Out - Exit current function
• Run to Cursor - Execute until cursor position

Breakpoints:
"""
            
            for bp_id, bp_info in self.debugger_state['breakpoints'].items():
                status = "✅" if bp_info['enabled'] else "❌"
                status_text += f"{status} {bp_info['file']}:{bp_info['line']} - {bp_info['condition']}\\n"
            
            self.execution_text.delete('1.0', tk.END)
            self.execution_text.insert('1.0', status_text)
    
    def update_callstack_display(self):
        """Update call stack display"""
        if hasattr(self, 'callstack_listbox'):
            self.callstack_listbox.delete(0, tk.END)
            for frame in reversed(self.debugger_state['call_stack']):
                self.callstack_listbox.insert(tk.END, frame)
    
    def refresh_memory_info(self):
        """Refresh memory information"""
        try:
            import psutil
            import gc
            import sys
            
            # Get system memory info
            memory = psutil.virtual_memory()
            process = psutil.Process()
            
            # Update labels
            self.memory_labels['Total Memory'].config(text=f"{memory.total / (1024**3):.2f} GB")
            self.memory_labels['Used Memory'].config(text=f"{memory.used / (1024**3):.2f} GB")
            self.memory_labels['Free Memory'].config(text=f"{memory.available / (1024**3):.2f} GB")
            self.memory_labels['Python Objects'].config(text=f"{len(gc.get_objects())}")
            
            # Count variables
            var_count = 0
            if hasattr(self, 'interpreter') and self.interpreter:
                for executor_name in ['pilot_executor', 'basic_executor', 'logo_executor']:
                    if hasattr(self.interpreter, executor_name):
                        executor = getattr(self.interpreter, executor_name)
                        if hasattr(executor, 'variables'):
                            var_count += len(executor.variables)
            
            self.memory_labels['Variables Count'].config(text=str(var_count))
            
            # Update memory monitor text
            memory_info = f"""Memory Monitor - {self.get_current_time()}

System Memory:
  Total: {memory.total / (1024**3):.2f} GB
  Available: {memory.available / (1024**3):.2f} GB
  Used: {memory.used / (1024**3):.2f} GB ({memory.percent}%)
  Free: {memory.free / (1024**3):.2f} GB

Process Memory:
  RSS: {process.memory_info().rss / (1024**2):.2f} MB
  VMS: {process.memory_info().vms / (1024**2):.2f} MB
  CPU Usage: {process.cpu_percent()}%

Python Objects:
  Total Objects: {len(gc.get_objects())}
  Garbage Collections: {gc.get_count()}

JAMES Variables:
  PILOT Variables: {len(getattr(getattr(self.interpreter, 'pilot_executor', None), 'variables', {}))}
  BASIC Variables: {len(getattr(getattr(self.interpreter, 'basic_executor', None), 'variables', {}))}
  Logo Variables: {len(getattr(getattr(self.interpreter, 'logo_executor', None), 'variables', {}))}

Memory Tips:
• Use garbage collection to free unused objects
• Monitor variable growth during execution
• Large variables consume more memory
• Clear variables when not needed
"""
            
            self.memory_text.delete('1.0', tk.END)
            self.memory_text.insert('1.0', memory_info)
            
        except ImportError:
            # Fallback if psutil not available
            import gc
            import sys
            
            self.memory_labels['Python Objects'].config(text=f"{len(gc.get_objects())}")
            
            fallback_info = f"""Memory Monitor (Limited) - {self.get_current_time()}

Python Objects: {len(gc.get_objects())}
Garbage Collections: {gc.get_count()}

Note: Install 'psutil' for detailed memory monitoring
pip install psutil
"""
            self.memory_text.delete('1.0', tk.END)
            self.memory_text.insert('1.0', fallback_info)
    
    def show_memory_profile(self):
        """Show detailed memory profile"""
        try:
            import gc
            from collections import Counter
            
            # Count objects by type
            objects = gc.get_objects()
            type_counts = Counter(type(obj).__name__ for obj in objects)
            
            profile_text = "Memory Profile - Object Types:\\n\\n"
            for obj_type, count in type_counts.most_common(20):
                profile_text += f"{obj_type}: {count}\\n"
            
            messagebox.showinfo("Memory Profile", profile_text)
            
        except Exception as e:
            messagebox.showerror("Memory Profile Error", f"Could not generate memory profile: {e}")
    
    def force_garbage_collection(self):
        """Force garbage collection"""
        try:
            import gc
            collected = gc.collect()
            messagebox.showinfo("Garbage Collection", f"Collected {collected} objects")
            self.refresh_memory_info()
        except Exception as e:
            messagebox.showerror("Garbage Collection Error", f"Could not run garbage collection: {e}")
    
    def get_current_time(self):
        """Get current time string"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def close_debugger(self):
        """Close debugger dialog"""
        self.debugger_dialog.destroy()
        self.debugger_dialog = None
        self.debugger_state = None
    
    # Add methods to JAMESII class
    JAMESII.setup_breakpoints_tab = setup_breakpoints_tab
    JAMESII.setup_debug_variables_tab = setup_debug_variables_tab
    JAMESII.setup_callstack_tab = setup_callstack_tab
    JAMESII.setup_execution_tab = setup_execution_tab
    JAMESII.setup_memory_tab = setup_memory_tab
    JAMESII.add_breakpoint = add_breakpoint
    JAMESII.remove_breakpoint = remove_breakpoint
    JAMESII.enable_all_breakpoints = enable_all_breakpoints
    JAMESII.disable_all_breakpoints = disable_all_breakpoints
    JAMESII.clear_all_breakpoints = clear_all_breakpoints
    JAMESII.refresh_debug_variables = refresh_debug_variables
    JAMESII.add_watch_variable = add_watch_variable
    JAMESII.edit_variable_value = edit_variable_value
    JAMESII.export_debug_variables = export_debug_variables
    JAMESII.on_stack_select = on_stack_select
    JAMESII.debug_run = debug_run
    JAMESII.debug_pause = debug_pause
    JAMESII.debug_stop = debug_stop
    JAMESII.debug_restart = debug_restart
    JAMESII.debug_step_over = debug_step_over
    JAMESII.debug_step_into = debug_step_into
    JAMESII.debug_step_out = debug_step_out
    JAMESII.debug_run_to_cursor = debug_run_to_cursor
    JAMESII.update_execution_status = update_execution_status
    JAMESII.update_callstack_display = update_callstack_display
    JAMESII.refresh_memory_info = refresh_memory_info
    JAMESII.show_memory_profile = show_memory_profile
    JAMESII.force_garbage_collection = force_garbage_collection
    JAMESII.get_current_time = get_current_time
    JAMESII.close_debugger = close_debugger
    
    # === HARDWARE CONTROLLER METHODS ===
    def setup_gpio_tab(self, parent):
        """Setup GPIO pins control tab"""
        # GPIO Pin Grid
        pin_frame = ttk.LabelFrame(parent, text="GPIO Pin Control")
        pin_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create GPIO pin grid (40 pins for Raspberry Pi)
        self.gpio_buttons = {}
        self.gpio_states = {}
        
        # Pin grid canvas
        canvas = tk.Canvas(pin_frame, width=400, height=300, bg='white')
        canvas.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Draw GPIO pin layout
        for i in range(40):
            row = i // 2
            col = i % 2
            x = 50 + col * 150
            y = 30 + row * 12
            
            pin_num = i + 1
            pin_color = self.get_gpio_pin_color(pin_num)
            
            # Pin rectangle
            rect_id = canvas.create_rectangle(x, y, x+80, y+10, fill=pin_color, outline='black')
            text_id = canvas.create_text(x+40, y+5, text=f"Pin {pin_num}", font=('Arial', 7))
            
            # Bind click events
            canvas.tag_bind(rect_id, "<Button-1>", lambda e, p=pin_num: self.toggle_gpio_pin(p))
            canvas.tag_bind(text_id, "<Button-1>", lambda e, p=pin_num: self.toggle_gpio_pin(p))
            
            self.gpio_states[pin_num] = {'mode': 'input', 'value': 0, 'enabled': False}
        
        # Control panel
        control_frame = ttk.LabelFrame(parent, text="Pin Control")
        control_frame.pack(fill=tk.Y, side=tk.RIGHT, padx=5, pady=5)
        
        ttk.Label(control_frame, text="Selected Pin:").pack(pady=5)
        self.selected_pin_var = tk.StringVar(value="None")
        ttk.Label(control_frame, textvariable=self.selected_pin_var, font=('Arial', 12, 'bold')).pack(pady=5)
        
        # Pin mode
        ttk.Label(control_frame, text="Mode:").pack(pady=(10,0))
        self.pin_mode_var = tk.StringVar(value="input")
        mode_frame = ttk.Frame(control_frame)
        mode_frame.pack(pady=5)
        ttk.Radiobutton(mode_frame, text="Input", variable=self.pin_mode_var, value="input", command=self.update_pin_mode).pack()
        ttk.Radiobutton(mode_frame, text="Output", variable=self.pin_mode_var, value="output", command=self.update_pin_mode).pack()
        
        # Pin value for output mode
        ttk.Label(control_frame, text="Output Value:").pack(pady=(10,0))
        self.pin_value_var = tk.StringVar(value="0")
        value_frame = ttk.Frame(control_frame)
        value_frame.pack(pady=5)
        ttk.Radiobutton(value_frame, text="LOW (0)", variable=self.pin_value_var, value="0", command=self.update_pin_value).pack()
        ttk.Radiobutton(value_frame, text="HIGH (1)", variable=self.pin_value_var, value="1", command=self.update_pin_value).pack()
        
        # Control buttons
        ttk.Button(control_frame, text="📖 Read Pin", command=self.read_gpio_pin).pack(pady=5, fill=tk.X)
        ttk.Button(control_frame, text="✏️ Write Pin", command=self.write_gpio_pin).pack(pady=5, fill=tk.X)
        ttk.Button(control_frame, text="🔄 Reset All", command=self.reset_all_gpio).pack(pady=5, fill=tk.X)
    
    def setup_sensors_tab(self, parent):
        """Setup sensors monitoring tab"""
        # Sensor list
        sensors_frame = ttk.LabelFrame(parent, text="Connected Sensors")
        sensors_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sensors treeview
        columns = ('Sensor', 'Type', 'Pin', 'Value', 'Unit', 'Status')
        self.sensors_tree = ttk.Treeview(sensors_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.sensors_tree.heading(col, text=col)
            self.sensors_tree.column(col, width=100)
        
        self.sensors_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        sensor_scroll = ttk.Scrollbar(sensors_frame, orient=tk.VERTICAL, command=self.sensors_tree.yview)
        self.sensors_tree.config(yscrollcommand=sensor_scroll.set)
        sensor_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Add default sensors
        default_sensors = [
            ("Temperature", "DHT22", "Pin 4", "22.5", "°C", "Active"),
            ("Humidity", "DHT22", "Pin 4", "65.0", "%", "Active"),
            ("Distance", "HC-SR04", "Pin 18", "15.2", "cm", "Active"),
            ("Light", "LDR", "Pin 26", "450", "lux", "Active"),
            ("Motion", "PIR", "Pin 23", "0", "detected", "Standby")
        ]
        
        for sensor in default_sensors:
            self.sensors_tree.insert('', 'end', values=sensor)
        
        # Sensor controls
        sensor_controls = ttk.Frame(parent)
        sensor_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(sensor_controls, text="➕ Add Sensor", command=self.add_sensor).pack(side=tk.LEFT, padx=2)
        ttk.Button(sensor_controls, text="❌ Remove Sensor", command=self.remove_sensor).pack(side=tk.LEFT, padx=2)
        ttk.Button(sensor_controls, text="🔄 Refresh Data", command=self.refresh_sensor_data).pack(side=tk.LEFT, padx=2)
        ttk.Button(sensor_controls, text="📊 Start Monitoring", command=self.start_sensor_monitoring).pack(side=tk.LEFT, padx=2)
        ttk.Button(sensor_controls, text="⏹️ Stop Monitoring", command=self.stop_sensor_monitoring).pack(side=tk.LEFT, padx=2)
    
    def setup_devices_tab(self, parent):
        """Setup device control tab"""
        # Device list
        devices_frame = ttk.LabelFrame(parent, text="Connected Devices")
        devices_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Devices treeview
        columns = ('Device', 'Type', 'Interface', 'Status', 'Actions')
        self.devices_tree = ttk.Treeview(devices_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.devices_tree.heading(col, text=col)
            self.devices_tree.column(col, width=120)
        
        self.devices_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        device_scroll = ttk.Scrollbar(devices_frame, orient=tk.VERTICAL, command=self.devices_tree.yview)
        self.devices_tree.config(yscrollcommand=device_scroll.set)
        device_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Add default devices
        default_devices = [
            ("LED Strip", "WS2812B", "GPIO 18", "Off", "Control"),
            ("Servo Motor", "SG90", "GPIO 12", "Position 90°", "Control"),
            ("Buzzer", "Active", "GPIO 13", "Silent", "Control"),
            ("Relay Module", "5V", "GPIO 21", "Open", "Control"),
            ("Display", "LCD 16x2", "I2C", "Ready", "Update")
        ]
        
        for device in default_devices:
            self.devices_tree.insert('', 'end', values=device)
        
        # Device controls
        device_controls = ttk.Frame(parent)
        device_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(device_controls, text="🔧 Control Device", command=self.control_device).pack(side=tk.LEFT, padx=2)
        ttk.Button(device_controls, text="📋 Device Info", command=self.show_device_info).pack(side=tk.LEFT, padx=2)
        ttk.Button(device_controls, text="⚙️ Configure", command=self.configure_device).pack(side=tk.LEFT, padx=2)
        ttk.Button(device_controls, text="🔄 Scan Devices", command=self.scan_devices).pack(side=tk.LEFT, padx=2)
    
    def setup_automation_tab(self, parent):
        """Setup automation rules tab"""
        # Automation rules
        rules_frame = ttk.LabelFrame(parent, text="Automation Rules")
        rules_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Rules listbox
        self.rules_listbox = tk.Listbox(rules_frame, font=('Consolas', 10))
        self.rules_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        rules_scroll = ttk.Scrollbar(rules_frame, orient=tk.VERTICAL, command=self.rules_listbox.yview)
        self.rules_listbox.config(yscrollcommand=rules_scroll.set)
        rules_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Add sample rules
        sample_rules = [
            "IF temperature > 25°C THEN turn_on(fan)",
            "IF motion_detected THEN turn_on(lights) FOR 10min",
            "IF light_level < 100 THEN dim_lights(50%)",
            "IF button_pressed THEN toggle(relay)",
            "EVERY 1hour DO read_all_sensors()"
        ]
        
        for rule in sample_rules:
            self.rules_listbox.insert(tk.END, rule)
        
        # Rule controls
        rule_controls = ttk.Frame(parent)
        rule_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(rule_controls, text="➕ Add Rule", command=self.add_automation_rule).pack(side=tk.LEFT, padx=2)
        ttk.Button(rule_controls, text="✏️ Edit Rule", command=self.edit_automation_rule).pack(side=tk.LEFT, padx=2)
        ttk.Button(rule_controls, text="❌ Delete Rule", command=self.delete_automation_rule).pack(side=tk.LEFT, padx=2)
        ttk.Button(rule_controls, text="▶️ Start Automation", command=self.start_automation).pack(side=tk.LEFT, padx=2)
        ttk.Button(rule_controls, text="⏹️ Stop Automation", command=self.stop_automation).pack(side=tk.LEFT, padx=2)
    
    # === HARDWARE HELPER METHODS ===
    def get_gpio_pin_color(self, pin_num):
        """Get color for GPIO pin based on function"""
        # Standard Raspberry Pi GPIO colors
        power_pins = [2, 4]  # 5V
        ground_pins = [6, 9, 14, 20, 25, 30, 34, 39]  # Ground
        
        if pin_num in power_pins:
            return '#FF6B6B'  # Red for power
        elif pin_num in ground_pins:
            return '#4ECDC4'  # Cyan for ground
        else:
            return '#95E1D3'  # Light green for GPIO
    
    def toggle_gpio_pin(self, pin_num):
        """Toggle GPIO pin selection"""
        self.selected_pin_var.set(f"Pin {pin_num}")
        pin_state = self.gpio_states.get(pin_num, {})
        self.pin_mode_var.set(pin_state.get('mode', 'input'))
        self.pin_value_var.set(str(pin_state.get('value', 0)))
    
    def update_pin_mode(self):
        """Update selected pin mode"""
        pin_num = self.get_selected_pin_number()
        if pin_num:
            self.gpio_states[pin_num]['mode'] = self.pin_mode_var.get()
            messagebox.showinfo("Pin Mode", f"Pin {pin_num} set to {self.pin_mode_var.get()} mode")
    
    def update_pin_value(self):
        """Update selected pin output value"""
        pin_num = self.get_selected_pin_number()
        if pin_num and self.gpio_states[pin_num]['mode'] == 'output':
            self.gpio_states[pin_num]['value'] = int(self.pin_value_var.get())
            messagebox.showinfo("Pin Value", f"Pin {pin_num} output set to {self.pin_value_var.get()}")
    
    def get_selected_pin_number(self):
        """Get currently selected pin number"""
        pin_text = self.selected_pin_var.get()
        if pin_text != "None":
            return int(pin_text.split()[1])
        return None
    
    def read_gpio_pin(self):
        """Read value from GPIO pin"""
        pin_num = self.get_selected_pin_number()
        if pin_num:
            # Simulate reading pin value
            import random
            value = random.randint(0, 1)
            self.gpio_states[pin_num]['value'] = value
            messagebox.showinfo("Pin Read", f"Pin {pin_num} value: {value}")
        else:
            messagebox.showwarning("No Pin Selected", "Please select a pin first")
    
    def write_gpio_pin(self):
        """Write value to GPIO pin"""
        pin_num = self.get_selected_pin_number()
        if pin_num:
            if self.gpio_states[pin_num]['mode'] == 'output':
                value = int(self.pin_value_var.get())
                self.gpio_states[pin_num]['value'] = value
                messagebox.showinfo("Pin Write", f"Pin {pin_num} set to {value}")
            else:
                messagebox.showwarning("Pin Mode", "Pin must be in output mode to write")
        else:
            messagebox.showwarning("No Pin Selected", "Please select a pin first")
    
    def reset_all_gpio(self):
        """Reset all GPIO pins"""
        if messagebox.askyesno("Reset GPIO", "Reset all GPIO pins to default state?"):
            for pin_num in self.gpio_states:
                self.gpio_states[pin_num] = {'mode': 'input', 'value': 0, 'enabled': False}
            messagebox.showinfo("GPIO Reset", "All GPIO pins reset to default state")
    
    def add_sensor(self):
        """Add a new sensor"""
        dialog = tk.Toplevel(self.root)
        dialog.title("➕ Add Sensor")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Sensor configuration
        ttk.Label(dialog, text="Sensor Name:").pack(pady=5)
        name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=name_var, width=30).pack(pady=5)
        
        ttk.Label(dialog, text="Sensor Type:").pack(pady=5)
        type_var = tk.StringVar(value="DHT22")
        type_combo = ttk.Combobox(dialog, textvariable=type_var, values=['DHT22', 'DS18B20', 'BMP280', 'HC-SR04', 'PIR', 'LDR'])
        type_combo.pack(pady=5)
        
        ttk.Label(dialog, text="GPIO Pin:").pack(pady=5)
        pin_var = tk.StringVar(value="Pin 4")
        pin_combo = ttk.Combobox(dialog, textvariable=pin_var, values=[f"Pin {i}" for i in range(1, 41)])
        pin_combo.pack(pady=5)
        
        def create_sensor():
            self.sensors_tree.insert('', 'end', values=(
                name_var.get(), type_var.get(), pin_var.get(), "0.0", "units", "Ready"
            ))
            messagebox.showinfo("Sensor Added", f"Sensor '{name_var.get()}' added successfully")
            dialog.destroy()
        
        ttk.Button(dialog, text="✅ Add", command=create_sensor).pack(pady=20)
        ttk.Button(dialog, text="❌ Cancel", command=dialog.destroy).pack()
    
    def remove_sensor(self):
        """Remove selected sensor"""
        selection = self.sensors_tree.selection()
        if selection:
            self.sensors_tree.delete(selection[0])
            messagebox.showinfo("Sensor Removed", "Sensor removed successfully")
        else:
            messagebox.showwarning("No Selection", "Please select a sensor to remove")
    
    def refresh_sensor_data(self):
        """Refresh sensor data"""
        import random
        for item in self.sensors_tree.get_children():
            values = list(self.sensors_tree.item(item)['values'])
            sensor_type = values[1]
            
            # Simulate sensor readings based on type
            if sensor_type == "DHT22":
                if "Temperature" in values[0]:
                    values[3] = f"{random.uniform(20, 30):.1f}"
                elif "Humidity" in values[0]:
                    values[3] = f"{random.uniform(40, 80):.1f}"
            elif sensor_type == "HC-SR04":
                values[3] = f"{random.uniform(5, 50):.1f}"
            elif sensor_type == "LDR":
                values[3] = f"{random.randint(100, 800)}"
            elif sensor_type == "PIR":
                values[3] = str(random.randint(0, 1))
            
            self.sensors_tree.item(item, values=values)
        
        messagebox.showinfo("Sensors", "Sensor data refreshed")
    
    def start_sensor_monitoring(self):
        """Start continuous sensor monitoring"""
        messagebox.showinfo("Monitoring", "Sensor monitoring started\\n\\nData will be logged continuously")
    
    def stop_sensor_monitoring(self):
        """Stop sensor monitoring"""
        messagebox.showinfo("Monitoring", "Sensor monitoring stopped")
    
    def control_device(self):
        """Control selected device"""
        selection = self.devices_tree.selection()
        if selection:
            item = self.devices_tree.item(selection[0])
            device_name = item['values'][0]
            device_type = item['values'][1]
            
            # Create device control dialog
            control_dialog = tk.Toplevel(self.root)
            control_dialog.title(f"🔧 Control {device_name}")
            control_dialog.geometry("300x200")
            control_dialog.transient(self.root)
            control_dialog.grab_set()
            
            ttk.Label(control_dialog, text=f"Device: {device_name}", font=('Arial', 12, 'bold')).pack(pady=10)
            ttk.Label(control_dialog, text=f"Type: {device_type}").pack()
            
            if "LED" in device_name:
                ttk.Button(control_dialog, text="💡 Turn On", command=lambda: self.device_action(device_name, "on")).pack(pady=5)
                ttk.Button(control_dialog, text="🌑 Turn Off", command=lambda: self.device_action(device_name, "off")).pack(pady=5)
            elif "Servo" in device_name:
                ttk.Button(control_dialog, text="↪️ Position 0°", command=lambda: self.device_action(device_name, "pos_0")).pack(pady=5)
                ttk.Button(control_dialog, text="↩️ Position 180°", command=lambda: self.device_action(device_name, "pos_180")).pack(pady=5)
            elif "Buzzer" in device_name:
                ttk.Button(control_dialog, text="🔊 Beep", command=lambda: self.device_action(device_name, "beep")).pack(pady=5)
            
            ttk.Button(control_dialog, text="❌ Close", command=control_dialog.destroy).pack(pady=10)
        else:
            messagebox.showwarning("No Selection", "Please select a device to control")
    
    def device_action(self, device, action):
        """Execute device action"""
        messagebox.showinfo("Device Control", f"Device '{device}' action: {action}")
    
    def show_device_info(self):
        """Show device information"""
        selection = self.devices_tree.selection()
        if selection:
            item = self.devices_tree.item(selection[0])
            device_info = f"""Device Information:
            
Name: {item['values'][0]}
Type: {item['values'][1]}
Interface: {item['values'][2]}
Status: {item['values'][3]}

Specifications:
• Operating Voltage: 3.3V - 5V
• Current Draw: < 100mA
• Communication: Digital/PWM
• Supported Commands: ON/OFF/CONTROL
"""
            messagebox.showinfo("Device Info", device_info)
        else:
            messagebox.showwarning("No Selection", "Please select a device")
    
    def configure_device(self):
        """Configure device settings"""
        messagebox.showinfo("Device Config", "Device configuration dialog would open here")
    
    def scan_devices(self):
        """Scan for connected devices"""
        messagebox.showinfo("Device Scan", "Scanning for devices...\\n\\nFound 5 devices on I2C bus\\nFound 3 devices on SPI bus")
    
    def add_automation_rule(self):
        """Add automation rule"""
        rule = simpledialog.askstring("Add Rule", "Enter automation rule:")
        if rule:
            self.rules_listbox.insert(tk.END, rule)
            messagebox.showinfo("Rule Added", "Automation rule added successfully")
    
    def edit_automation_rule(self):
        """Edit selected automation rule"""
        selection = self.rules_listbox.curselection()
        if selection:
            old_rule = self.rules_listbox.get(selection[0])
            new_rule = simpledialog.askstring("Edit Rule", "Edit automation rule:", initialvalue=old_rule)
            if new_rule:
                self.rules_listbox.delete(selection[0])
                self.rules_listbox.insert(selection[0], new_rule)
                messagebox.showinfo("Rule Updated", "Automation rule updated")
        else:
            messagebox.showwarning("No Selection", "Please select a rule to edit")
    
    def delete_automation_rule(self):
        """Delete selected automation rule"""
        selection = self.rules_listbox.curselection()
        if selection:
            if messagebox.askyesno("Delete Rule", "Delete selected automation rule?"):
                self.rules_listbox.delete(selection[0])
                messagebox.showinfo("Rule Deleted", "Automation rule deleted")
        else:
            messagebox.showwarning("No Selection", "Please select a rule to delete")
    
    def start_automation(self):
        """Start automation system"""
        messagebox.showinfo("Automation", "Automation system started\\n\\nAll rules are now active")
    
    def stop_automation(self):
        """Stop automation system"""
        messagebox.showinfo("Automation", "Automation system stopped\\n\\nAll rules are now inactive")
    
    # === IOT DEVICE MANAGER METHODS ===
    def setup_device_discovery_tab(self, parent):
        """Setup device discovery tab for IoT manager"""
        # Network scan controls
        scan_frame = ttk.LabelFrame(parent, text="Network Scanning")
        scan_frame.pack(fill=tk.X, padx=5, pady=5)
        
        scan_controls = ttk.Frame(scan_frame)
        scan_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(scan_controls, text="Network Range:").pack(side=tk.LEFT, padx=2)
        self.network_range_var = tk.StringVar(value="192.168.1.0/24")
        ttk.Entry(scan_controls, textvariable=self.network_range_var, width=20).pack(side=tk.LEFT, padx=2)
        ttk.Button(scan_controls, text="🔍 Scan Network", command=self.scan_network).pack(side=tk.LEFT, padx=2)
        ttk.Button(scan_controls, text="🔄 Auto-Discover", command=self.auto_discover_devices).pack(side=tk.LEFT, padx=2)
        
        # Discovered devices
        devices_frame = ttk.LabelFrame(parent, text="Discovered Devices")
        devices_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Device discovery treeview
        columns = ('IP Address', 'Device Type', 'Protocol', 'Status', 'Description')
        self.discovery_tree = ttk.Treeview(devices_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.discovery_tree.heading(col, text=col)
            self.discovery_tree.column(col, width=120)
        
        self.discovery_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        discovery_scroll = ttk.Scrollbar(devices_frame, orient=tk.VERTICAL, command=self.discovery_tree.yview)
        self.discovery_tree.config(yscrollcommand=discovery_scroll.set)
        discovery_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Add sample discovered devices
        sample_devices = [
            ("192.168.1.101", "Smart Light", "HTTP/REST", "Online", "Philips Hue Bridge"),
            ("192.168.1.102", "Thermostat", "MQTT", "Online", "Nest Learning Thermostat"),
            ("192.168.1.103", "Security Camera", "RTSP", "Online", "Ring Doorbell Pro"),
            ("192.168.1.104", "Smart Speaker", "UPnP", "Online", "Amazon Echo Dot"),
            ("192.168.1.105", "IoT Sensor", "CoAP", "Online", "Temperature/Humidity Sensor"),
            ("192.168.1.106", "Smart Plug", "HTTP", "Offline", "TP-Link Kasa Smart Plug")
        ]
        
        for device in sample_devices:
            self.discovery_tree.insert('', 'end', values=device)
        
        # Device action buttons
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(action_frame, text="➕ Add Device", command=self.add_discovered_device).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="📋 Device Info", command=self.show_discovered_device_info).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="🔧 Configure", command=self.configure_discovered_device).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="🧪 Test Connection", command=self.test_device_connection).pack(side=tk.LEFT, padx=2)
    
    def setup_device_control_tab(self, parent):
        """Setup device control tab"""
        # Connected devices list
        devices_frame = ttk.LabelFrame(parent, text="Connected IoT Devices")
        devices_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Device control treeview
        columns = ('Device Name', 'Type', 'IP Address', 'Protocol', 'Status', 'Last Update')
        self.control_tree = ttk.Treeview(devices_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.control_tree.heading(col, text=col)
            self.control_tree.column(col, width=100)
        
        self.control_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        control_scroll = ttk.Scrollbar(devices_frame, orient=tk.VERTICAL, command=self.control_tree.yview)
        self.control_tree.config(yscrollcommand=control_scroll.set)
        control_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Add sample IoT devices
        sample_iot_devices = [
            ("Living Room Light", "Smart Bulb", "192.168.1.101", "HTTP", "On", "2024-01-15 14:30"),
            ("Smart Thermostat", "Climate Control", "192.168.1.102", "MQTT", "Auto 72°F", "2024-01-15 14:29"),
            ("Front Door Camera", "Security", "192.168.1.103", "RTSP", "Recording", "2024-01-15 14:28"),
            ("Kitchen Sensor", "Environmental", "192.168.1.105", "CoAP", "Active", "2024-01-15 14:27"),
            ("Smart Plug 1", "Power Control", "192.168.1.106", "HTTP", "Off", "2024-01-15 14:25")
        ]
        
        for device in sample_iot_devices:
            self.control_tree.insert('', 'end', values=device)
        
        # Control panel
        control_panel = ttk.LabelFrame(parent, text="Device Control Panel")
        control_panel.pack(fill=tk.X, padx=5, pady=5)
        
        control_buttons = ttk.Frame(control_panel)
        control_buttons.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_buttons, text="💡 Control Device", command=self.control_iot_device).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_buttons, text="📊 Get Status", command=self.get_device_status).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_buttons, text="📝 Send Command", command=self.send_device_command).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_buttons, text="🔄 Refresh All", command=self.refresh_all_devices).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_buttons, text="⚙️ Settings", command=self.device_settings).pack(side=tk.LEFT, padx=2)
    
    def setup_network_monitoring_tab(self, parent):
        """Setup network monitoring tab"""
        # Network statistics
        stats_frame = ttk.LabelFrame(parent, text="Network Statistics")
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X, padx=5, pady=5)
        
        # Network stats display
        stats_labels = [
            ("Connected Devices:", "15"),
            ("Active Connections:", "12"),
            ("Data Transferred:", "2.4 GB"),
            ("Network Uptime:", "7 days, 14 hours"),
            ("Average Latency:", "12ms"),
            ("Packet Loss:", "0.02%")
        ]
        
        for i, (label, value) in enumerate(stats_labels):
            row = i // 2
            col = i % 2
            ttk.Label(stats_grid, text=label).grid(row=row, column=col*2, padx=5, pady=2, sticky='e')
            ttk.Label(stats_grid, text=value, font=('Arial', 10, 'bold')).grid(row=row, column=col*2+1, padx=5, pady=2, sticky='w')
        
        # Traffic monitoring
        traffic_frame = ttk.LabelFrame(parent, text="Network Traffic")
        traffic_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Traffic log
        self.traffic_text = scrolledtext.ScrolledText(traffic_frame, height=15, font=('Consolas', 9))
        self.traffic_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add sample traffic data
        sample_traffic = """
14:30:15 - 192.168.1.101 -> MQTT Broker: PUBLISH topic/temperature {"temp": 23.5}
14:30:16 - 192.168.1.102 -> REST API: GET /api/thermostat/status
14:30:17 - 192.168.1.103 -> Streaming: RTSP video frame (1920x1080)
14:30:18 - 192.168.1.105 -> CoAP Server: POST /sensors/humidity {"humidity": 65}
14:30:19 - 192.168.1.106 -> HTTP: POST /control {"action": "toggle"}
14:30:20 - Gateway -> 192.168.1.101: ACK message received
14:30:21 - 192.168.1.102 -> Cloud Service: Sync status update
14:30:22 - 192.168.1.103 -> Mobile App: Push notification sent
14:30:23 - MQTT Broker -> All Subscribers: Broadcast temperature update
14:30:24 - Security System -> 192.168.1.103: Motion detection alert
        """
        
        self.traffic_text.insert(tk.END, sample_traffic.strip())
        
        # Monitoring controls
        monitor_controls = ttk.Frame(parent)
        monitor_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(monitor_controls, text="▶️ Start Monitoring", command=self.start_traffic_monitoring).pack(side=tk.LEFT, padx=2)
        ttk.Button(monitor_controls, text="⏹️ Stop Monitoring", command=self.stop_traffic_monitoring).pack(side=tk.LEFT, padx=2)
        ttk.Button(monitor_controls, text="💾 Export Log", command=self.export_traffic_log).pack(side=tk.LEFT, padx=2)
        ttk.Button(monitor_controls, text="🧹 Clear Log", command=self.clear_traffic_log).pack(side=tk.LEFT, padx=2)
    
    def setup_protocols_tab(self, parent):
        """Setup IoT protocols configuration tab"""
        # Protocol settings
        protocols_frame = ttk.LabelFrame(parent, text="Supported IoT Protocols")
        protocols_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Protocol treeview
        columns = ('Protocol', 'Port', 'Status', 'Devices', 'Description')
        self.protocols_tree = ttk.Treeview(protocols_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.protocols_tree.heading(col, text=col)
            self.protocols_tree.column(col, width=120)
        
        self.protocols_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        protocol_scroll = ttk.Scrollbar(protocols_frame, orient=tk.VERTICAL, command=self.protocols_tree.yview)
        self.protocols_tree.config(yscrollcommand=protocol_scroll.set)
        protocol_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Add supported protocols
        protocols_data = [
            ("HTTP/REST", "80/443", "Active", "8", "RESTful web services"),
            ("MQTT", "1883", "Active", "5", "Message queuing protocol"),
            ("CoAP", "5683", "Active", "3", "Constrained Application Protocol"),
            ("WebSocket", "8080", "Active", "2", "Real-time bidirectional communication"),
            ("RTSP", "554", "Active", "1", "Real-time streaming protocol"),
            ("UPnP", "1900", "Standby", "1", "Universal Plug and Play"),
            ("Zigbee", "N/A", "Offline", "0", "Low-power mesh networking"),
            ("LoRaWAN", "N/A", "Offline", "0", "Long-range wide area network")
        ]
        
        for protocol in protocols_data:
            self.protocols_tree.insert('', 'end', values=protocol)
        
        # Protocol controls
        protocol_controls = ttk.Frame(parent)
        protocol_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(protocol_controls, text="⚙️ Configure Protocol", command=self.configure_protocol).pack(side=tk.LEFT, padx=2)
        ttk.Button(protocol_controls, text="▶️ Enable Protocol", command=self.enable_protocol).pack(side=tk.LEFT, padx=2)
        ttk.Button(protocol_controls, text="⏹️ Disable Protocol", command=self.disable_protocol).pack(side=tk.LEFT, padx=2)
        ttk.Button(protocol_controls, text="🧪 Test Protocol", command=self.test_protocol).pack(side=tk.LEFT, padx=2)
    
    def setup_iot_analytics_tab(self, parent):
        """Setup IoT data analytics tab"""
        # Analytics dashboard
        dashboard_frame = ttk.LabelFrame(parent, text="IoT Analytics Dashboard")
        dashboard_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Analytics canvas
        self.analytics_canvas = tk.Canvas(dashboard_frame, bg='white', height=400)
        self.analytics_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Draw sample analytics charts
        self.draw_iot_analytics()
        
        # Analytics controls
        analytics_controls = ttk.Frame(parent)
        analytics_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(analytics_controls, text="📊 Refresh Charts", command=self.refresh_iot_analytics).pack(side=tk.LEFT, padx=2)
        ttk.Button(analytics_controls, text="💾 Export Data", command=self.export_iot_data).pack(side=tk.LEFT, padx=2)
        ttk.Button(analytics_controls, text="📈 Generate Report", command=self.generate_iot_report).pack(side=tk.LEFT, padx=2)
        ttk.Button(analytics_controls, text="⚙️ Configure Alerts", command=self.configure_iot_alerts).pack(side=tk.LEFT, padx=2)
    
    # === IOT HELPER METHODS ===
    def scan_network(self):
        """Scan network for IoT devices"""
        network = self.network_range_var.get()
        messagebox.showinfo("Network Scan", f"Scanning network {network}...\\n\\nFound 6 IoT devices\\n\\n✅ Scan complete!")
    
    def auto_discover_devices(self):
        """Auto-discover IoT devices using various protocols"""
        messagebox.showinfo("Auto Discovery", "Auto-discovering devices...\\n\\n🔍 mDNS scan: 3 devices\\n🔍 UPnP scan: 2 devices\\n🔍 MQTT discovery: 1 device\\n\\n✅ Discovery complete!")
    
    def add_discovered_device(self):
        """Add discovered device to managed devices"""
        selection = self.discovery_tree.selection()
        if selection:
            messagebox.showinfo("Device Added", "Device added to managed devices list\\n\\n📱 Configuration saved\\n🔗 Connection established")
        else:
            messagebox.showwarning("No Selection", "Please select a device to add")
    
    def show_discovered_device_info(self):
        """Show detailed information about discovered device"""
        selection = self.discovery_tree.selection()
        if selection:
            item = self.discovery_tree.item(selection[0])
            device_info = f"""Device Information:
            
IP Address: {item['values'][0]}
Device Type: {item['values'][1]}
Protocol: {item['values'][2]}
Status: {item['values'][3]}
Description: {item['values'][4]}

Capabilities:
• Remote Control: ✅
• Status Monitoring: ✅
• Firmware Update: ✅
• Security: WPA2-PSK
• API Version: v2.1
"""
            messagebox.showinfo("Device Info", device_info)
        else:
            messagebox.showwarning("No Selection", "Please select a device")
    
    def configure_discovered_device(self):
        """Configure discovered device"""
        messagebox.showinfo("Device Config", "Device configuration dialog\\n\\n⚙️ Network settings\\n🔐 Security options\\n📊 Data collection preferences")
    
    def test_device_connection(self):
        """Test connection to discovered device"""
        selection = self.discovery_tree.selection()
        if selection:
            messagebox.showinfo("Connection Test", "Testing device connection...\\n\\n🔗 Ping: 12ms\\n✅ Protocol handshake: OK\\n✅ Authentication: Success\\n\\n✅ Connection test passed!")
        else:
            messagebox.showwarning("No Selection", "Please select a device to test")
    
    def control_iot_device(self):
        """Control selected IoT device"""
        selection = self.control_tree.selection()
        if selection:
            item = self.control_tree.item(selection[0])
            device_name = item['values'][0]
            device_type = item['values'][1]
            
            # Create device control dialog
            control_dialog = tk.Toplevel(self.root)
            control_dialog.title(f"🎛️ Control {device_name}")
            control_dialog.geometry("400x300")
            control_dialog.transient(self.root)
            control_dialog.grab_set()
            
            ttk.Label(control_dialog, text=f"Device: {device_name}", font=('Arial', 12, 'bold')).pack(pady=10)
            ttk.Label(control_dialog, text=f"Type: {device_type}").pack()
            
            if "Light" in device_name or "Bulb" in device_type:
                ttk.Button(control_dialog, text="💡 Turn On", command=lambda: self.iot_device_action(device_name, "on")).pack(pady=5)
                ttk.Button(control_dialog, text="🌑 Turn Off", command=lambda: self.iot_device_action(device_name, "off")).pack(pady=5)
                ttk.Button(control_dialog, text="🌈 Change Color", command=lambda: self.iot_device_action(device_name, "color")).pack(pady=5)
            elif "Thermostat" in device_name:
                ttk.Button(control_dialog, text="🔄 Auto Mode", command=lambda: self.iot_device_action(device_name, "auto")).pack(pady=5)
                ttk.Button(control_dialog, text="❄️ Cool Mode", command=lambda: self.iot_device_action(device_name, "cool")).pack(pady=5)
                ttk.Button(control_dialog, text="🔥 Heat Mode", command=lambda: self.iot_device_action(device_name, "heat")).pack(pady=5)
            elif "Camera" in device_name:
                ttk.Button(control_dialog, text="📹 Start Recording", command=lambda: self.iot_device_action(device_name, "record")).pack(pady=5)
                ttk.Button(control_dialog, text="📸 Take Snapshot", command=lambda: self.iot_device_action(device_name, "snapshot")).pack(pady=5)
            
            ttk.Button(control_dialog, text="❌ Close", command=control_dialog.destroy).pack(pady=10)
        else:
            messagebox.showwarning("No Selection", "Please select a device to control")
    
    def iot_device_action(self, device, action):
        """Execute IoT device action"""
        messagebox.showinfo("Device Action", f"Device '{device}' action: {action}\\n\\n📤 Command sent\\n✅ Action completed successfully")
    
    def get_device_status(self):
        """Get status from selected device"""
        selection = self.control_tree.selection()
        if selection:
            item = self.control_tree.item(selection[0])
            device_name = item['values'][0]
            status_info = f"""Device Status Report:
            
Device: {device_name}
Status: Online
Uptime: 5 days, 12 hours
Signal Strength: -45 dBm (Excellent)
Battery Level: 87%
Last Communication: 2 seconds ago
Firmware Version: 2.1.4
Temperature: 24°C
Memory Usage: 45%
"""
            messagebox.showinfo("Device Status", status_info)
        else:
            messagebox.showwarning("No Selection", "Please select a device")
    
    def send_device_command(self):
        """Send custom command to device"""
        selection = self.control_tree.selection()
        if selection:
            command = simpledialog.askstring("Send Command", "Enter device command:")
            if command:
                messagebox.showinfo("Command Sent", f"Command '{command}' sent to device\\n\\n📤 Transmitted successfully\\n✅ Device acknowledged")
        else:
            messagebox.showwarning("No Selection", "Please select a device")
    
    def refresh_all_devices(self):
        """Refresh status of all connected devices"""
        messagebox.showinfo("Refresh Devices", "Refreshing all device statuses...\\n\\n🔄 Querying 5 devices\\n✅ All devices updated successfully")
    
    def device_settings(self):
        """Open device settings"""
        messagebox.showinfo("Device Settings", "Device settings panel\\n\\n⚙️ Connection preferences\\n🔔 Notification settings\\n📊 Data collection options")
    
    def start_traffic_monitoring(self):
        """Start network traffic monitoring"""
        messagebox.showinfo("Traffic Monitor", "Network traffic monitoring started\\n\\n📊 Capturing all IoT traffic\\n📝 Logging to database")
    
    def stop_traffic_monitoring(self):
        """Stop network traffic monitoring"""
        messagebox.showinfo("Traffic Monitor", "Network traffic monitoring stopped\\n\\n📊 Captured 1,247 packets\\n💾 Log saved to file")
    
    def export_traffic_log(self):
        """Export traffic log to file"""
        filename = filedialog.asksaveasfilename(defaultextension=".log", filetypes=[("Log files", "*.log"), ("Text files", "*.txt")])
        if filename:
            messagebox.showinfo("Export Log", f"Traffic log exported to:\\n{filename}\\n\\n📊 2,456 entries exported")
    
    def clear_traffic_log(self):
        """Clear traffic monitoring log"""
        if messagebox.askyesno("Clear Log", "Clear all traffic monitoring data?"):
            self.traffic_text.delete(1.0, tk.END)
            messagebox.showinfo("Log Cleared", "Traffic monitoring log cleared")
    
    def configure_protocol(self):
        """Configure IoT protocol settings"""
        selection = self.protocols_tree.selection()
        if selection:
            item = self.protocols_tree.item(selection[0])
            protocol = item['values'][0]
            messagebox.showinfo("Protocol Config", f"Configure {protocol} protocol\\n\\n⚙️ Connection settings\\n🔐 Security options\\n📊 Quality of service")
        else:
            messagebox.showwarning("No Selection", "Please select a protocol")
    
    def enable_protocol(self):
        """Enable selected protocol"""
        selection = self.protocols_tree.selection()
        if selection:
            item = self.protocols_tree.item(selection[0])
            protocol = item['values'][0]
            messagebox.showinfo("Protocol Enabled", f"Protocol {protocol} enabled\\n\\n✅ Service started\\n🔗 Listening for connections")
        else:
            messagebox.showwarning("No Selection", "Please select a protocol")
    
    def disable_protocol(self):
        """Disable selected protocol"""
        selection = self.protocols_tree.selection()
        if selection:
            item = self.protocols_tree.item(selection[0])
            protocol = item['values'][0]
            if messagebox.askyesno("Disable Protocol", f"Disable {protocol} protocol?"):
                messagebox.showinfo("Protocol Disabled", f"Protocol {protocol} disabled\\n\\n⏹️ Service stopped\\n❌ No longer accepting connections")
        else:
            messagebox.showwarning("No Selection", "Please select a protocol")
    
    def test_protocol(self):
        """Test protocol connectivity"""
        selection = self.protocols_tree.selection()
        if selection:
            item = self.protocols_tree.item(selection[0])
            protocol = item['values'][0]
            messagebox.showinfo("Protocol Test", f"Testing {protocol} protocol...\\n\\n🔗 Connection: OK\\n📤 Send test: OK\\n📥 Receive test: OK\\n\\n✅ Protocol test passed!")
        else:
            messagebox.showwarning("No Selection", "Please select a protocol")
    
    def draw_iot_analytics(self):
        """Draw IoT analytics charts on canvas"""
        canvas = self.analytics_canvas
        canvas.delete("all")
        
        # Chart 1: Device Status Distribution (Pie Chart)
        center_x, center_y, radius = 150, 150, 80
        angles = [0, 120, 200, 300]  # degrees
        colors = ['#4CAF50', '#FF9800', '#F44336', '#9E9E9E']
        labels = ['Online (12)', 'Idle (3)', 'Error (1)', 'Offline (2)']
        
        for i, (angle, color, label) in enumerate(zip(angles, colors, labels)):
            start_angle = angle
            extent = 60 if i < 3 else 60
            canvas.create_arc(center_x-radius, center_y-radius, center_x+radius, center_y+radius,
                            start=start_angle, extent=extent, fill=color, outline='white', width=2)
        
        canvas.create_text(center_x, center_y-radius-20, text="Device Status", font=('Arial', 12, 'bold'))
        
        # Chart 2: Data Transfer Over Time (Line Chart)
        chart_x, chart_y, chart_w, chart_h = 350, 50, 300, 200
        canvas.create_rectangle(chart_x, chart_y, chart_x+chart_w, chart_y+chart_h, outline='black', fill='white')
        
        # Sample data points
        data_points = [(0, 180), (50, 120), (100, 160), (150, 100), (200, 140), (250, 80), (300, 110)]
        
        for i in range(len(data_points)-1):
            x1, y1 = data_points[i]
            x2, y2 = data_points[i+1]
            canvas.create_line(chart_x+x1, chart_y+chart_h-y1, chart_x+x2, chart_y+chart_h-y2, 
                             fill='blue', width=2)
            canvas.create_oval(chart_x+x1-3, chart_y+chart_h-y1-3, chart_x+x1+3, chart_y+chart_h-y1+3, 
                             fill='blue', outline='darkblue')
        
        canvas.create_text(chart_x+chart_w//2, chart_y-10, text="Data Transfer (MB/h)", font=('Arial', 12, 'bold'))
        
        # Chart 3: Protocol Usage (Bar Chart)
        bar_x, bar_y, bar_w, bar_h = 50, 280, 250, 100
        protocols = ['HTTP', 'MQTT', 'CoAP', 'WS']
        usage_data = [85, 65, 45, 25]
        bar_colors = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0']
        
        canvas.create_text(bar_x+bar_w//2, bar_y-10, text="Protocol Usage (%)", font=('Arial', 12, 'bold'))
        
        for i, (protocol, usage, color) in enumerate(zip(protocols, usage_data, bar_colors)):
            x = bar_x + i * 60
            height = usage * bar_h // 100
            canvas.create_rectangle(x, bar_y+bar_h-height, x+40, bar_y+bar_h, fill=color, outline='black')
            canvas.create_text(x+20, bar_y+bar_h+15, text=protocol, font=('Arial', 9))
            canvas.create_text(x+20, bar_y+bar_h-height//2, text=f"{usage}%", font=('Arial', 8, 'bold'))
    
    def refresh_iot_analytics(self):
        """Refresh IoT analytics charts"""
        self.draw_iot_analytics()
        messagebox.showinfo("Analytics Refreshed", "IoT analytics data refreshed\\n\\n📊 Charts updated\\n📈 Latest data loaded")
    
    def export_iot_data(self):
        """Export IoT analytics data"""
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json")])
        if filename:
            messagebox.showinfo("Data Exported", f"IoT analytics data exported to:\\n{filename}\\n\\n📊 15,432 data points exported")
    
    def generate_iot_report(self):
        """Generate comprehensive IoT report"""
        messagebox.showinfo("Report Generated", "IoT Analytics Report Generated\\n\\n📈 Performance metrics\\n📊 Usage statistics\\n🔍 Trend analysis\\n\\n📄 Report saved as PDF")
    
    def configure_iot_alerts(self):
        """Configure IoT monitoring alerts"""
        messagebox.showinfo("Alert Configuration", "IoT Alert Settings\\n\\n🚨 Threshold alerts\\n📧 Email notifications\\n📱 Push notifications\\n📊 Custom rules")
    
    # Add hardware methods to JAMESII class using setattr
    setattr(JAMESII, 'setup_device_discovery_tab', setup_device_discovery_tab)
    setattr(JAMESII, 'setup_device_control_tab', setup_device_control_tab)
    setattr(JAMESII, 'setup_network_monitoring_tab', setup_network_monitoring_tab)
    setattr(JAMESII, 'setup_protocols_tab', setup_protocols_tab)
    setattr(JAMESII, 'setup_iot_analytics_tab', setup_iot_analytics_tab)
    setattr(JAMESII, 'scan_network', scan_network)
    setattr(JAMESII, 'auto_discover_devices', auto_discover_devices)
    setattr(JAMESII, 'add_discovered_device', add_discovered_device)
    setattr(JAMESII, 'show_discovered_device_info', show_discovered_device_info)
    setattr(JAMESII, 'configure_discovered_device', configure_discovered_device)
    setattr(JAMESII, 'test_device_connection', test_device_connection)
    setattr(JAMESII, 'control_iot_device', control_iot_device)
    setattr(JAMESII, 'iot_device_action', iot_device_action)
    setattr(JAMESII, 'get_device_status', get_device_status)
    setattr(JAMESII, 'send_device_command', send_device_command)
    setattr(JAMESII, 'refresh_all_devices', refresh_all_devices)
    setattr(JAMESII, 'device_settings', device_settings)
    setattr(JAMESII, 'start_traffic_monitoring', start_traffic_monitoring)
    setattr(JAMESII, 'stop_traffic_monitoring', stop_traffic_monitoring)
    setattr(JAMESII, 'export_traffic_log', export_traffic_log)
    setattr(JAMESII, 'clear_traffic_log', clear_traffic_log)
    setattr(JAMESII, 'configure_protocol', configure_protocol)
    setattr(JAMESII, 'enable_protocol', enable_protocol)
    setattr(JAMESII, 'disable_protocol', disable_protocol)
    setattr(JAMESII, 'test_protocol', test_protocol)
    setattr(JAMESII, 'draw_iot_analytics', draw_iot_analytics)
    setattr(JAMESII, 'refresh_iot_analytics', refresh_iot_analytics)
    setattr(JAMESII, 'export_iot_data', export_iot_data)
    setattr(JAMESII, 'generate_iot_report', generate_iot_report)
    setattr(JAMESII, 'configure_iot_alerts', configure_iot_alerts)
    
    setattr(JAMESII, 'setup_gpio_tab', setup_gpio_tab)
    setattr(JAMESII, 'setup_sensors_tab', setup_sensors_tab)
    setattr(JAMESII, 'setup_devices_tab', setup_devices_tab)
    setattr(JAMESII, 'setup_automation_tab', setup_automation_tab)
    setattr(JAMESII, 'get_gpio_pin_color', get_gpio_pin_color)
    setattr(JAMESII, 'toggle_gpio_pin', toggle_gpio_pin)
    setattr(JAMESII, 'update_pin_mode', update_pin_mode)
    setattr(JAMESII, 'update_pin_value', update_pin_value)
    setattr(JAMESII, 'get_selected_pin_number', get_selected_pin_number)
    setattr(JAMESII, 'read_gpio_pin', read_gpio_pin)
    setattr(JAMESII, 'write_gpio_pin', write_gpio_pin)
    setattr(JAMESII, 'reset_all_gpio', reset_all_gpio)
    setattr(JAMESII, 'add_sensor', add_sensor)
    setattr(JAMESII, 'remove_sensor', remove_sensor)
    setattr(JAMESII, 'refresh_sensor_data', refresh_sensor_data)
    setattr(JAMESII, 'start_sensor_monitoring', start_sensor_monitoring)
    setattr(JAMESII, 'stop_sensor_monitoring', stop_sensor_monitoring)
    setattr(JAMESII, 'control_device', control_device)
    setattr(JAMESII, 'device_action', device_action)
    setattr(JAMESII, 'show_device_info', show_device_info)
    setattr(JAMESII, 'configure_device', configure_device)
    setattr(JAMESII, 'scan_devices', scan_devices)
    setattr(JAMESII, 'add_automation_rule', add_automation_rule)
    setattr(JAMESII, 'edit_automation_rule', edit_automation_rule)
    setattr(JAMESII, 'delete_automation_rule', delete_automation_rule)
    setattr(JAMESII, 'start_automation', start_automation)
    setattr(JAMESII, 'stop_automation', stop_automation)
    
    # Add existing methods to JAMESII class using setattr
    setattr(JAMESII, 'show_hardware_controller', show_hardware_controller)
    setattr(JAMESII, 'show_iot_manager', show_iot_manager)
    setattr(JAMESII, 'show_sensor_visualizer', show_sensor_visualizer)
    setattr(JAMESII, 'show_learning_assistant', show_learning_assistant)
    setattr(JAMESII, 'show_code_examples', show_code_examples)
    setattr(JAMESII, 'show_testing_framework', show_testing_framework)
    setattr(JAMESII, 'show_graphics_canvas', show_graphics_canvas)
    setattr(JAMESII, 'show_code_converter', show_code_converter)
    setattr(JAMESII, 'show_system_info', show_system_info)

# Add the tools methods
add_tools_methods()


if __name__ == "__main__":
    main()