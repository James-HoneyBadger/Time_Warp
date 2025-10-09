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


if __name__ == "__main__":
    main()