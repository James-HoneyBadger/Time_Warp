"""
Advanced GUI Components for JAMES IDE
Contains dialogs, managers, and specialized interface components.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import os
import subprocess
from typing import Dict, List, Optional, Callable


class ProjectExplorer:
    """File tree view for managing JAMES projects and files"""
    
    def __init__(self, ide):
        self.ide = ide
        self.current_project_path = None
        self.tree_widget: Optional[ttk.Treeview] = None
        self.explorer_window: Optional[tk.Toplevel] = None
        self.file_watchers = {}
        
    def show_explorer(self):
        """Show the project explorer window"""
        if self.explorer_window and self.explorer_window.winfo_exists():
            self.explorer_window.lift()
            return
            
        # Create explorer window
        self.explorer_window = tk.Toplevel(self.ide.root)
        self.explorer_window.title("Project Explorer")
        self.explorer_window.geometry("300x500")
        
        # Create toolbar
        toolbar = tk.Frame(self.explorer_window, bg="#F0F0F0", height=30)
        toolbar.pack(fill=tk.X, padx=2, pady=2)
        toolbar.pack_propagate(False)
        
        # Toolbar buttons
        tk.Button(toolbar, text="📁", command=self.open_project_folder,
                 font=("Segoe UI", 10), relief=tk.FLAT,
                 bg="#F0F0F0", fg="#333", padx=5).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="📄", command=self.new_file,
                 font=("Segoe UI", 10), relief=tk.FLAT, 
                 bg="#F0F0F0", fg="#333", padx=5).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="🔄", command=self.refresh_tree,
                 font=("Segoe UI", 10), relief=tk.FLAT,
                 bg="#F0F0F0", fg="#333", padx=5).pack(side=tk.LEFT, padx=2)
        
        # Project path label
        self.path_label = tk.Label(self.explorer_window, 
                                  text="No project opened",
                                  bg="#E8E8E8", fg="#666",
                                  font=("Segoe UI", 9),
                                  anchor=tk.W, padx=5)
        self.path_label.pack(fill=tk.X, padx=2, pady=(0, 2))
        
        # Create tree view
        tree_frame = tk.Frame(self.explorer_window)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tree widget with scrollbars
        self.tree_widget = ttk.Treeview(tree_frame, show='tree headings')
        self.tree_widget.heading('#0', text='JAMES Files', anchor=tk.W)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_widget.yview)    
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree_widget.xview)
        self.tree_widget.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack tree and scrollbars
        self.tree_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind events
        self.tree_widget.bind('<Double-1>', self.on_item_double_click)
        self.tree_widget.bind('<Button-3>', self.show_context_menu)
        
        # Set default project path to current directory
        current_dir = os.getcwd()
        JAMES_projects = os.path.join(current_dir, "JAMES_Projects")
        
        if os.path.exists(JAMES_projects):
            self.load_project(JAMES_projects)
        else:
            self.load_project(current_dir)
    
    def open_project_folder(self):
        """Open a project folder"""
        folder_path = filedialog.askdirectory(title="Select Project Folder")
        if folder_path:
            self.load_project(folder_path)
    
    def load_project(self, project_path):
        """Load a project folder into the tree"""
        self.current_project_path = project_path
        self.path_label.config(text=f"Project: {os.path.basename(project_path)}")
        self.refresh_tree()
    
    def refresh_tree(self):
        """Refresh the file tree"""
        if not self.tree_widget or not self.current_project_path:
            return
            
        # Clear existing tree
        for item in self.tree_widget.get_children():
            self.tree_widget.delete(item)
        
        # Populate tree
        self.populate_tree(self.current_project_path, "")
    
    def populate_tree(self, path, parent_node):
        """Populate tree with files and folders"""
        try:
            items = []
            # Get directories and files
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    items.append((item, item_path, "folder"))
                elif item.endswith(('.jtc', '.pil', '.pilot', '.logo', '.bas')):
                    items.append((item, item_path, "file"))
            
            # Sort: folders first, then files
            items.sort(key=lambda x: (x[2] != "folder", x[0].lower()))
            
            for item_name, item_path, item_type in items:
                icon = "📁" if item_type == "folder" else self.get_file_icon(item_name)
                node_text = f"{icon} {item_name}"
                
                node = self.tree_widget.insert(parent_node, tk.END, 
                                             text=node_text,
                                             values=(item_path, item_type))
                
                # If it's a folder, add a placeholder child to make it expandable
                if item_type == "folder":
                    self.tree_widget.insert(node, tk.END, text="Loading...")
                    
            # Bind tree expansion event
            self.tree_widget.bind('<<TreeviewOpen>>', self.on_tree_expand)
            
        except PermissionError:
            pass  # Skip directories we can't read
    
    def get_file_icon(self, filename):
        """Get icon for file based on extension"""
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        icons = {
            'jtc': '🎯',    # JAMES files
            'pil': '✈️',    # PILOT files
            'pilot': '✈️',  # PILOT files  
            'logo': '🐢',   # Logo files
            'bas': '💻',    # BASIC files
            'basic': '💻',  # BASIC files
            'txt': '📄',    # Text files
            'md': '📝',     # Markdown files
        }
        return icons.get(ext, '📄')
    
    def on_tree_expand(self, event):
        """Handle tree expansion - lazy loading of subdirectories"""
        if not self.tree_widget:
            return
            
        selection = self.tree_widget.selection()
        item = selection[0] if selection else None
        if not item:
            return
            
        # Check if this is a folder and has placeholder child
        values = self.tree_widget.item(item, 'values')
        if len(values) >= 2 and values[1] == "folder":
            children = self.tree_widget.get_children(item)
            if len(children) == 1 and self.tree_widget.item(children[0], 'text') == "Loading...":
                # Remove placeholder and load actual contents
                self.tree_widget.delete(children[0])
                self.populate_tree(values[0], item)
    
    def on_item_double_click(self, event):
        """Handle double-click on tree item"""
        if not self.tree_widget:
            return
            
        selection = self.tree_widget.selection()
        item = selection[0] if selection else None
        if not item:
            return
            
        values = self.tree_widget.item(item, 'values')
        if len(values) >= 2:
            file_path, item_type = values[0], values[1]
            
            if item_type == "file":
                self.open_file(file_path)
    
    def open_file(self, file_path):
        """Open a file in the main editor"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Load content into main editor
            self.ide.editor.delete('1.0', tk.END)
            self.ide.editor.insert('1.0', content)
            
            # Update IDE title and status
            filename = os.path.basename(file_path)
            self.ide.root.title(f"JAMES - {filename}")
            
            if hasattr(self.ide, 'status_label'):
                self.ide.status_label.config(text=f"📂 Opened: {filename}")
                
            # Store current file path for saving
            self.ide.current_file_path = file_path
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file:\n{str(e)}")
    
    def new_file(self):
        """Create a new JAMES file"""
        if not self.current_project_path:
            messagebox.showwarning("Warning", "Please open a project folder first")
            return
            
        filename = simpledialog.askstring("New File", 
                                        "Enter filename (with .jtc extension):")
        if filename:
            if not filename.endswith('.jtc'):
                filename += '.jtc'
                
            file_path = os.path.join(self.current_project_path, filename)
            
            try:
                # Create empty file with basic template
                template_content = """T:Welcome to JAMES!
T:This is a new JAMES program.
T:Start coding here...
E:
"""
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(template_content)
                
                # Refresh tree to show new file
                self.refresh_tree()
                
                # Open the new file
                self.open_file(file_path)
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not create file:\n{str(e)}")
    
    def show_context_menu(self, event):
        """Show context menu for tree items"""
        # Context menu implementation would go here
        pass


class GameManagerDialog:
    """Game development and object management dialog"""
    
    def __init__(self, ide):
        self.ide = ide
        self.window = None
        self.auto_refresh = False
        
    def show(self):
        """Show the game management dialog"""
        if self.window:
            self.window.lift()
            return
            
        self.window = tk.Toplevel(self.ide.root)
        self.window.title("🎮 Game Development Manager")
        self.window.geometry("700x600")
        self.window.transient(self.ide.root)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Game Objects tab
        objects_frame = ttk.Frame(notebook)
        notebook.add(objects_frame, text="🎯 Game Objects")
        self.setup_objects_tab(objects_frame)
        
        # Physics tab
        physics_frame = ttk.Frame(notebook)
        notebook.add(physics_frame, text="⚡ Physics")
        self.setup_physics_tab(physics_frame)
        
        # Scene Preview tab
        preview_frame = ttk.Frame(notebook)
        notebook.add(preview_frame, text="🎨 Scene Preview")
        self.setup_preview_tab(preview_frame)
        
        # Quick Demo tab
        demo_frame = ttk.Frame(notebook)
        notebook.add(demo_frame, text="🚀 Quick Demo")
        self.setup_demo_tab(demo_frame)
        
        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        
    def setup_objects_tab(self, parent):
        """Setup the game objects management tab"""
        # Objects list
        list_frame = ttk.LabelFrame(parent, text="Game Objects")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for objects
        columns = ('Name', 'Type', 'Position', 'Size', 'Velocity')
        self.objects_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.objects_tree.heading(col, text=col)
            self.objects_tree.column(col, width=120)
        
        # Scrollbar for tree
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.objects_tree.yview)
        self.objects_tree.configure(yscrollcommand=scrollbar.set)
        
        self.objects_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons frame
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(buttons_frame, text="🎯 Create Object", command=self.create_object).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="📝 Edit Properties", command=self.edit_object).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="🗑️ Delete Object", command=self.delete_object).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="🔄 Refresh", command=self.refresh_objects).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="🧹 Clear All", command=self.clear_all_objects).pack(side=tk.LEFT, padx=2)
        
        self.refresh_objects()
        
    def setup_physics_tab(self, parent):
        """Setup the physics configuration tab"""
        # Global physics settings
        global_frame = ttk.LabelFrame(parent, text="Global Physics Settings")
        global_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Gravity control
        gravity_frame = ttk.Frame(global_frame)
        gravity_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(gravity_frame, text="Gravity:").pack(side=tk.LEFT)
        self.gravity_var = tk.DoubleVar(value=9.8)
        gravity_scale = ttk.Scale(gravity_frame, from_=0, to=20, variable=self.gravity_var, orient=tk.HORIZONTAL)
        gravity_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 10))
        
        gravity_label = ttk.Label(gravity_frame, text="9.8")
        gravity_label.pack(side=tk.LEFT)
        
        def update_gravity_label(*args):
            gravity_label.config(text=f"{self.gravity_var.get():.1f}")
            if hasattr(self.ide, 'interpreter') and hasattr(self.ide.interpreter, 'game_manager'):
                self.ide.interpreter.game_manager.set_gravity(self.gravity_var.get())
            
        self.gravity_var.trace('w', update_gravity_label)
        
        ttk.Button(gravity_frame, text="🌍 Apply Gravity", 
                  command=lambda: self.apply_gravity()).pack(side=tk.RIGHT, padx=5)
        
        # Physics simulation controls
        sim_frame = ttk.LabelFrame(parent, text="Simulation Controls")
        sim_frame.pack(fill=tk.X, padx=5, pady=5)
        
        control_frame = ttk.Frame(sim_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="▶️ Start Physics", command=self.start_physics).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="⏸️ Pause Physics", command=self.pause_physics).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="⏹️ Stop Physics", command=self.stop_physics).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="🔄 Single Step", command=self.step_physics).pack(side=tk.LEFT, padx=2)
        
        # Physics info
        info_frame = ttk.LabelFrame(parent, text="Physics Information")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.physics_info = tk.Text(info_frame, height=8, font=('Consolas', 10))
        info_scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.physics_info.yview)
        self.physics_info.configure(yscrollcommand=info_scrollbar.set)
        self.physics_info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.update_physics_info()
        
    def setup_preview_tab(self, parent):
        """Setup the scene preview tab"""
        # Canvas for scene preview
        canvas_frame = ttk.LabelFrame(parent, text="Scene Preview")
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.preview_canvas = tk.Canvas(canvas_frame, bg='white', width=600, height=400)
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Preview controls
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="🎨 Render Scene", command=self.render_preview).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="🔄 Auto-Refresh", command=self.toggle_auto_refresh).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="💾 Save Scene", command=self.save_scene).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="📁 Load Scene", command=self.load_scene).pack(side=tk.LEFT, padx=2)
        
        self.render_preview()
        
    def setup_demo_tab(self, parent):
        """Setup the quick demo tab"""
        # Demo buttons
        demos = [
            ("🏓 Pong Game", "pong", "Classic Pong with paddles and ball physics"),
            ("🌍 Physics Demo", "physics", "Falling objects with gravity simulation"),
            ("🏃 Platformer", "platformer", "Jump and run game with platforms"),
            ("🐍 Snake Game", "snake", "Classic Snake with food collection and growth"),
        ]
        
        for name, demo_type, description in demos:
            demo_frame = ttk.LabelFrame(parent, text=name)
            demo_frame.pack(fill=tk.X, padx=5, pady=5)
            
            desc_label = ttk.Label(demo_frame, text=description, font=('Arial', 9), foreground='gray')
            desc_label.pack(anchor=tk.W, padx=5, pady=2)
            
            ttk.Button(demo_frame, text=f"🚀 Run {name}", 
                      command=lambda dt=demo_type: self.run_demo(dt)).pack(padx=5, pady=5, anchor=tk.W)
        
        # Custom demo section
        custom_frame = ttk.LabelFrame(parent, text="🛠️ Custom Demo")
        custom_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(custom_frame, text="Create your own demo with custom parameters:", 
                 font=('Arial', 9), foreground='gray').pack(anchor=tk.W, padx=5, pady=2)
        
        params_frame = ttk.Frame(custom_frame)
        params_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(params_frame, text="Objects:").pack(side=tk.LEFT)
        self.demo_objects = tk.IntVar(value=5)
        ttk.Spinbox(params_frame, from_=1, to=20, textvariable=self.demo_objects, width=5).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(params_frame, text="Gravity:").pack(side=tk.LEFT, padx=(10, 0))
        self.demo_gravity = tk.DoubleVar(value=9.8)
        ttk.Spinbox(params_frame, from_=0, to=20, textvariable=self.demo_gravity, width=8, increment=0.1).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(custom_frame, text="🎮 Run Custom Demo", command=self.run_custom_demo).pack(padx=5, pady=5, anchor=tk.W)
    
    # Game management methods (simplified for space)
    def create_object(self):
        """Create a new game object"""
        messagebox.showinfo("Create Object", "Game object creation dialog would appear here")
        
    def edit_object(self):
        """Edit selected object"""
        messagebox.showinfo("Edit Object", "Object property editor would appear here")
        
    def delete_object(self):
        """Delete selected object"""
        messagebox.showinfo("Delete Object", "Selected object would be deleted")
        
    def refresh_objects(self):
        """Refresh the objects list"""
        # Clear and repopulate tree
        for item in self.objects_tree.get_children():
            self.objects_tree.delete(item)
            
    def clear_all_objects(self):
        """Clear all game objects"""
        if messagebox.askyesno("Confirm", "Clear all game objects?"):
            self.refresh_objects()
            
    def apply_gravity(self):
        """Apply gravity setting"""
        gravity = self.gravity_var.get()
        messagebox.showinfo("Physics", f"Gravity set to {gravity:.1f}")
        
    def start_physics(self):
        """Start physics simulation"""
        messagebox.showinfo("Physics", "Physics simulation started")
        
    def pause_physics(self):
        """Pause physics simulation"""
        messagebox.showinfo("Physics", "Physics simulation paused")
        
    def stop_physics(self):
        """Stop physics simulation"""
        messagebox.showinfo("Physics", "Physics simulation stopped")
        
    def step_physics(self):
        """Single step physics simulation"""
        messagebox.showinfo("Physics", "Physics stepped one frame")
        
    def update_physics_info(self):
        """Update physics information display"""
        info_text = """Physics System Status:
        
Gravity: 9.8 m/s²
Active Objects: 0
Collisions: 0
Frame Rate: 60 FPS
Simulation: Stopped
"""
        self.physics_info.delete('1.0', tk.END)
        self.physics_info.insert('1.0', info_text)
        
    def render_preview(self):
        """Render scene preview"""
        self.preview_canvas.delete("all")
        self.preview_canvas.create_text(300, 200, text="Scene Preview\n(Game objects would render here)", 
                                       font=('Arial', 14), fill='gray')
        
    def toggle_auto_refresh(self):
        """Toggle auto-refresh of preview"""
        self.auto_refresh = not self.auto_refresh
        status = "enabled" if self.auto_refresh else "disabled"
        messagebox.showinfo("Auto Refresh", f"Auto-refresh {status}")
        
    def save_scene(self):
        """Save current scene"""
        messagebox.showinfo("Save Scene", "Scene would be saved to file")
        
    def load_scene(self):
        """Load scene from file"""
        messagebox.showinfo("Load Scene", "Scene would be loaded from file")
        
    def run_demo(self, demo_type):
        """Run game demonstration"""
        messagebox.showinfo("Demo", f"Running {demo_type} demo")
        
    def run_custom_demo(self):
        """Run custom demo with parameters"""
        objects = self.demo_objects.get()
        gravity = self.demo_gravity.get()
        messagebox.showinfo("Custom Demo", f"Running demo with {objects} objects and gravity {gravity}")
    
    def close(self):
        """Close the dialog"""
        if self.window:
            self.window.destroy()
            self.window = None


class VirtualEnvironmentManager:
    """Manages virtual environment for JAMES IDE and package installation"""
    
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
        self.venv_dir = os.path.join(self.base_dir, "james_venv")
        self.python_exe = None
        self.pip_exe = None
        self.is_initialized = False
        self.status_callback = None
        
    def set_status_callback(self, callback: Callable[[str], None]):
        """Set callback function for status updates"""
        self.status_callback = callback
        
    def log_status(self, message: str):
        """Log status message"""
        print(f"🐍 VirtualEnv: {message}")
        if self.status_callback:
            self.status_callback(f"🐍 {message}")
    
    def check_venv_exists(self) -> bool:
        """Check if virtual environment already exists"""
        if os.path.exists(self.venv_dir):
            # Check if it has the basic structure
            if os.name == 'nt':  # Windows
                python_path = os.path.join(self.venv_dir, "Scripts", "python.exe")
                pip_path = os.path.join(self.venv_dir, "Scripts", "pip.exe")
            else:  # Unix/Linux/macOS
                python_path = os.path.join(self.venv_dir, "bin", "python")
                pip_path = os.path.join(self.venv_dir, "bin", "pip")
            
            if os.path.exists(python_path) and os.path.exists(pip_path):
                self.python_exe = python_path
                self.pip_exe = pip_path
                return True
        return False
    
    def create_virtual_environment(self) -> bool:
        """Create a new virtual environment"""
        try:
            import venv
            
            self.log_status("Creating virtual environment...")
            
            # Remove existing venv if it exists but is broken
            if os.path.exists(self.venv_dir):
                import shutil
                shutil.rmtree(self.venv_dir)
            
            # Create new virtual environment
            venv.create(self.venv_dir, with_pip=True)
            
            # Set paths for executables
            if os.name == 'nt':  # Windows
                self.python_exe = os.path.join(self.venv_dir, "Scripts", "python.exe")
                self.pip_exe = os.path.join(self.venv_dir, "Scripts", "pip.exe")
            else:  # Unix/Linux/macOS
                self.python_exe = os.path.join(self.venv_dir, "bin", "python")
                self.pip_exe = os.path.join(self.venv_dir, "bin", "pip")
            
            self.log_status(f"Virtual environment created at: {self.venv_dir}")
            return True
            
        except Exception as e:
            self.log_status(f"Failed to create virtual environment: {e}")
            return False
    
    def initialize(self) -> bool:
        """Initialize virtual environment for JAMES"""
        if self.check_venv_exists():
            self.log_status("Virtual environment found")
            self.is_initialized = True
            return True
        
        self.log_status("Virtual environment not found, creating...")
        if self.create_virtual_environment():
            self.is_initialized = True
            return True
        
        return False
    
    def install_package(self, package_name: str, version: Optional[str] = None) -> bool:
        """Install a package in the virtual environment"""
        if not self.is_initialized or not self.pip_exe:
            self.log_status("Virtual environment not initialized")
            return False
        
        try:
            # Construct package specification
            if version:
                package_spec = f"{package_name}=={version}"
            else:
                package_spec = package_name
            
            self.log_status(f"Installing {package_spec}...")
            
            # Run pip install
            result = subprocess.run([
                str(self.pip_exe), "install", package_spec
            ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
            
            if result.returncode == 0:
                self.log_status(f"Successfully installed {package_spec}")
                return True
            else:
                self.log_status(f"Failed to install {package_spec}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_status(f"Installation of {package_spec} timed out")
            return False
        except Exception as e:
            self.log_status(f"Error installing {package_spec}: {e}")
            return False
    
    def install_james_dependencies(self) -> bool:
        """Install all dependencies needed for JAMES functionality"""
        dependencies = [
            ("matplotlib", "3.7.0"),  # For plotting features
            ("pillow", "10.0.0"),     # For image processing
            ("requests", "2.31.0"),   # For web operations
        ]
        
        self.log_status("Installing JAMES dependencies...")
        success_count = 0
        
        for package, version in dependencies:
            if self.install_package(package, version):
                success_count += 1
            else:
                # Try without version specification
                if self.install_package(package):
                    success_count += 1
        
        self.log_status(f"Installed {success_count}/{len(dependencies)} dependencies")
        return success_count == len(dependencies)
    
    def list_installed_packages(self) -> List[str]:
        """List all installed packages in the virtual environment"""
        if not self.is_initialized or not self.pip_exe:
            return []
        
        try:
            result = subprocess.run([
                str(self.pip_exe), "list", "--format=freeze"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return result.stdout.strip().split('\n')
            else:
                self.log_status(f"Failed to list packages: {result.stderr}")
                return []
                
        except Exception as e:
            self.log_status(f"Error listing packages: {e}")
            return []