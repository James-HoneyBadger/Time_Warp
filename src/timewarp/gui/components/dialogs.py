"""
Advanced GUI Components for Time_Warp IDE
Contains dialogs, managers, and specialized interface components.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import os
import subprocess
from typing import Dict, List, Optional, Callable


class ProjectExplorer:
    """File tree view for managing Time_Warp projects and files"""

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
        tk.Button(
            toolbar,
            text="📁",
            command=self.open_project_folder,
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            bg="#F0F0F0",
            fg="#333",
            padx=5,
        ).pack(side=tk.LEFT, padx=2)
        tk.Button(
            toolbar,
            text="📄",
            command=self.new_file,
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            bg="#F0F0F0",
            fg="#333",
            padx=5,
        ).pack(side=tk.LEFT, padx=2)
        tk.Button(
            toolbar,
            text="🔄",
            command=self.refresh_tree,
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            bg="#F0F0F0",
            fg="#333",
            padx=5,
        ).pack(side=tk.LEFT, padx=2)

        # Project path label
        self.path_label = tk.Label(
            self.explorer_window,
            text="No project opened",
            bg="#E8E8E8",
            fg="#666",
            font=("Segoe UI", 9),
            anchor=tk.W,
            padx=5,
        )
        self.path_label.pack(fill=tk.X, padx=2, pady=(0, 2))

        # Create tree view
        tree_frame = tk.Frame(self.explorer_window)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tree widget with scrollbars
        self.tree_widget = ttk.Treeview(tree_frame, show="tree headings")
        self.tree_widget.heading("#0", text="Time_Warp Files", anchor=tk.W)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(
            tree_frame, orient=tk.VERTICAL, command=self.tree_widget.yview
        )
        h_scrollbar = ttk.Scrollbar(
            tree_frame, orient=tk.HORIZONTAL, command=self.tree_widget.xview
        )
        self.tree_widget.configure(
            yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set
        )

        # Pack tree and scrollbars
        self.tree_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Bind events
        self.tree_widget.bind("<Double-1>", self.on_item_double_click)
        self.tree_widget.bind("<Button-3>", self.show_context_menu)

        # Set default project path to current directory
        current_dir = os.getcwd()
        TimeWarp_projects = os.path.join(current_dir, "TimeWarp_Projects")

        if os.path.exists(TimeWarp_projects):
            self.load_project(TimeWarp_projects)
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
                elif item.endswith((".pilot", ".logo", ".bas", ".py", ".js", ".pl")):
                    items.append((item, item_path, "file"))

            # Sort: folders first, then files
            items.sort(key=lambda x: (x[2] != "folder", x[0].lower()))

            for item_name, item_path, item_type in items:
                icon = "📁" if item_type == "folder" else self.get_file_icon(item_name)
                node_text = f"{icon} {item_name}"

                node = self.tree_widget.insert(
                    parent_node, tk.END, text=node_text, values=(item_path, item_type)
                )

                # If it's a folder, add a placeholder child to make it expandable
                if item_type == "folder":
                    self.tree_widget.insert(node, tk.END, text="Loading...")

            # Bind tree expansion event
            self.tree_widget.bind("<<TreeviewOpen>>", self.on_tree_expand)

        except PermissionError:
            pass  # Skip directories we can't read

    def get_file_icon(self, filename):
        """Get icon for file based on extension"""
        ext = filename.lower().split(".")[-1] if "." in filename else ""
        icons = {
            "jtc": "🎯",  # Time_Warp files
            "pil": "✈️",  # PILOT files
            "pilot": "✈️",  # PILOT files
            "logo": "🐢",  # Logo files
            "bas": "💻",  # BASIC files
            "basic": "💻",  # BASIC files
            "txt": "📄",  # Text files
            "md": "📝",  # Markdown files
        }
        return icons.get(ext, "📄")

    def on_tree_expand(self, event):
        """Handle tree expansion - lazy loading of subdirectories"""
        if not self.tree_widget:
            return

        selection = self.tree_widget.selection()
        item = selection[0] if selection else None
        if not item:
            return

        # Check if this is a folder and has placeholder child
        values = self.tree_widget.item(item, "values")
        if len(values) >= 2 and values[1] == "folder":
            children = self.tree_widget.get_children(item)
            if (
                len(children) == 1
                and self.tree_widget.item(children[0], "text") == "Loading..."
            ):
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

        values = self.tree_widget.item(item, "values")
        if len(values) >= 2:
            file_path, item_type = values[0], values[1]

            if item_type == "file":
                self.open_file(file_path)

    def open_file(self, file_path):
        """Open a file in the main editor"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Load content into main editor
            self.ide.editor.delete("1.0", tk.END)
            self.ide.editor.insert("1.0", content)

            # Update IDE title and status
            filename = os.path.basename(file_path)
            self.ide.root.title(f"Time_Warp - {filename}")

            if hasattr(self.ide, "status_label"):
                self.ide.status_label.config(text=f"📂 Opened: {filename}")

            # Store current file path for saving
            self.ide.current_file_path = file_path

        except Exception as e:
            messagebox.showerror("Error", f"Could not open file:\n{str(e)}")

    def new_file(self):
        """Create a new Time_Warp file"""
        if not self.current_project_path:
            messagebox.showwarning("Warning", "Please open a project folder first")
            return

        filename = simpledialog.askstring(
            "New File", "Enter filename (e.g., program.pilot, script.py):"
        )
        if filename:
            # Let users specify their own extensions for different languages
            if not any(filename.endswith(ext) for ext in ['.pilot', '.bas', '.logo', '.py', '.js', '.pl']):
                filename += ".pilot"  # Default to PILOT for educational use

            file_path = os.path.join(self.current_project_path, filename)

            try:
                # Create empty file with basic template
                template_content = """T:Welcome to Time_Warp!
T:This is a new Time_Warp program.
T:Start coding here...
E:
"""
                with open(file_path, "w", encoding="utf-8") as f:
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
        columns = ("Name", "Type", "Position", "Size", "Velocity")
        self.objects_tree = ttk.Treeview(
            list_frame, columns=columns, show="headings", height=10
        )

        for col in columns:
            self.objects_tree.heading(col, text=col)
            self.objects_tree.column(col, width=120)

        # Scrollbar for tree
        scrollbar = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.objects_tree.yview
        )
        self.objects_tree.configure(yscrollcommand=scrollbar.set)

        self.objects_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Buttons frame
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            buttons_frame, text="🎯 Create Object", command=self.create_object
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            buttons_frame, text="📝 Edit Properties", command=self.edit_object
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            buttons_frame, text="🗑️ Delete Object", command=self.delete_object
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="🔄 Refresh", command=self.refresh_objects).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(
            buttons_frame, text="🧹 Clear All", command=self.clear_all_objects
        ).pack(side=tk.LEFT, padx=2)

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
        gravity_scale = ttk.Scale(
            gravity_frame,
            from_=0,
            to=20,
            variable=self.gravity_var,
            orient=tk.HORIZONTAL,
        )
        gravity_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 10))

        gravity_label = ttk.Label(gravity_frame, text="9.8")
        gravity_label.pack(side=tk.LEFT)

        def update_gravity_label(*args):
            gravity_label.config(text=f"{self.gravity_var.get():.1f}")
            if hasattr(self.ide, "interpreter") and hasattr(
                self.ide.interpreter, "game_manager"
            ):
                self.ide.interpreter.game_manager.set_gravity(self.gravity_var.get())

        self.gravity_var.trace("w", update_gravity_label)

        ttk.Button(
            gravity_frame, text="🌍 Apply Gravity", command=lambda: self.apply_gravity()
        ).pack(side=tk.RIGHT, padx=5)

        # Physics simulation controls
        sim_frame = ttk.LabelFrame(parent, text="Simulation Controls")
        sim_frame.pack(fill=tk.X, padx=5, pady=5)

        control_frame = ttk.Frame(sim_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            control_frame, text="▶️ Start Physics", command=self.start_physics
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            control_frame, text="⏸️ Pause Physics", command=self.pause_physics
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            control_frame, text="⏹️ Stop Physics", command=self.stop_physics
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            control_frame, text="🔄 Single Step", command=self.step_physics
        ).pack(side=tk.LEFT, padx=2)

        # Physics info
        info_frame = ttk.LabelFrame(parent, text="Physics Information")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.physics_info = tk.Text(info_frame, height=8, font=("Consolas", 10))
        info_scrollbar = ttk.Scrollbar(
            info_frame, orient=tk.VERTICAL, command=self.physics_info.yview
        )
        self.physics_info.configure(yscrollcommand=info_scrollbar.set)
        self.physics_info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.update_physics_info()

    def setup_preview_tab(self, parent):
        """Setup the scene preview tab"""
        # Canvas for scene preview
        canvas_frame = ttk.LabelFrame(parent, text="Scene Preview")
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.preview_canvas = tk.Canvas(canvas_frame, bg="white", width=600, height=400)
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Preview controls
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            control_frame, text="🎨 Render Scene", command=self.render_preview
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            control_frame, text="🔄 Auto-Refresh", command=self.toggle_auto_refresh
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="💾 Save Scene", command=self.save_scene).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(control_frame, text="📁 Load Scene", command=self.load_scene).pack(
            side=tk.LEFT, padx=2
        )

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

            desc_label = ttk.Label(
                demo_frame, text=description, font=("Arial", 9), foreground="gray"
            )
            desc_label.pack(anchor=tk.W, padx=5, pady=2)

            ttk.Button(
                demo_frame,
                text=f"🚀 Run {name}",
                command=lambda dt=demo_type: self.run_demo(dt),
            ).pack(padx=5, pady=5, anchor=tk.W)

        # Custom demo section
        custom_frame = ttk.LabelFrame(parent, text="🛠️ Custom Demo")
        custom_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(
            custom_frame,
            text="Create your own demo with custom parameters:",
            font=("Arial", 9),
            foreground="gray",
        ).pack(anchor=tk.W, padx=5, pady=2)

        params_frame = ttk.Frame(custom_frame)
        params_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(params_frame, text="Objects:").pack(side=tk.LEFT)
        self.demo_objects = tk.IntVar(value=5)
        ttk.Spinbox(
            params_frame, from_=1, to=20, textvariable=self.demo_objects, width=5
        ).pack(side=tk.LEFT, padx=5)

        ttk.Label(params_frame, text="Gravity:").pack(side=tk.LEFT, padx=(10, 0))
        self.demo_gravity = tk.DoubleVar(value=9.8)
        ttk.Spinbox(
            params_frame,
            from_=0,
            to=20,
            textvariable=self.demo_gravity,
            width=8,
            increment=0.1,
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            custom_frame, text="🎮 Run Custom Demo", command=self.run_custom_demo
        ).pack(padx=5, pady=5, anchor=tk.W)

    # Game management methods - Full Implementation
    def create_object(self):
        """Create a new game object"""
        dialog = tk.Toplevel(self.window)
        dialog.title("🎯 Create Game Object")
        dialog.geometry("400x350")
        dialog.transient(self.window)
        dialog.grab_set()

        # Object properties
        ttk.Label(dialog, text="Object Name:").pack(pady=5)
        name_var = tk.StringVar(value="object_1")
        ttk.Entry(dialog, textvariable=name_var, width=30).pack(pady=5)

        ttk.Label(dialog, text="Object Type:").pack(pady=5)
        type_var = tk.StringVar(value="sprite")
        type_combo = ttk.Combobox(
            dialog,
            textvariable=type_var,
            values=["sprite", "platform", "enemy", "powerup", "projectile"],
        )
        type_combo.pack(pady=5)

        # Position frame
        pos_frame = ttk.LabelFrame(dialog, text="Position")
        pos_frame.pack(fill=tk.X, padx=20, pady=10)

        x_var = tk.IntVar(value=100)
        y_var = tk.IntVar(value=100)

        ttk.Label(pos_frame, text="X:").pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(pos_frame, from_=0, to=800, textvariable=x_var, width=8).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Label(pos_frame, text="Y:").pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(pos_frame, from_=0, to=600, textvariable=y_var, width=8).pack(
            side=tk.LEFT, padx=5
        )

        # Size frame
        size_frame = ttk.LabelFrame(dialog, text="Size")
        size_frame.pack(fill=tk.X, padx=20, pady=10)

        width_var = tk.IntVar(value=32)
        height_var = tk.IntVar(value=32)

        ttk.Label(size_frame, text="Width:").pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(size_frame, from_=1, to=200, textvariable=width_var, width=8).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Label(size_frame, text="Height:").pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(size_frame, from_=1, to=200, textvariable=height_var, width=8).pack(
            side=tk.LEFT, padx=5
        )

        # Color
        ttk.Label(dialog, text="Color:").pack(pady=5)
        color_var = tk.StringVar(value="blue")
        color_combo = ttk.Combobox(
            dialog,
            textvariable=color_var,
            values=[
                "red",
                "blue",
                "green",
                "yellow",
                "purple",
                "orange",
                "black",
                "white",
            ],
        )
        color_combo.pack(pady=5)

        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)

        def create():
            try:
                game_manager = getattr(self.ide.interpreter, "game_manager", None)
                if game_manager:
                    success = game_manager.create_object(
                        name_var.get(),
                        type_var.get(),
                        x_var.get(),
                        y_var.get(),
                        width_var.get(),
                        height_var.get(),
                        color_var.get(),
                    )
                    if success:
                        messagebox.showinfo(
                            "Success",
                            f"Object '{name_var.get()}' created successfully!",
                        )
                        self.refresh_objects()
                        dialog.destroy()
                    else:
                        messagebox.showerror("Error", "Failed to create object")
                else:
                    messagebox.showerror("Error", "Game engine not available")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create object: {e}")

        ttk.Button(button_frame, text="✅ Create", command=create).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="❌ Cancel", command=dialog.destroy).pack(
            side=tk.LEFT, padx=5
        )

    def edit_object(self):
        """Edit selected object"""
        selection = self.objects_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an object to edit")
            return

        item = self.objects_tree.item(selection[0])
        obj_name = item["values"][0]

        # Get object from game manager
        game_manager = getattr(self.ide.interpreter, "game_manager", None)
        if not game_manager:
            messagebox.showerror("Error", "Game engine not available")
            return

        obj = game_manager.get_object(obj_name)
        if not obj:
            messagebox.showerror("Error", f"Object '{obj_name}' not found")
            return

        dialog = tk.Toplevel(self.window)
        dialog.title(f"📝 Edit Object: {obj_name}")
        dialog.geometry("400x300")
        dialog.transient(self.window)
        dialog.grab_set()

        # Position controls
        pos_frame = ttk.LabelFrame(dialog, text="Position")
        pos_frame.pack(fill=tk.X, padx=20, pady=10)

        x_var = tk.DoubleVar(value=obj.position.x)
        y_var = tk.DoubleVar(value=obj.position.y)

        ttk.Label(pos_frame, text="X:").pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(
            pos_frame, from_=0, to=800, textvariable=x_var, width=8, increment=1
        ).pack(side=tk.LEFT, padx=5)
        ttk.Label(pos_frame, text="Y:").pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(
            pos_frame, from_=0, to=600, textvariable=y_var, width=8, increment=1
        ).pack(side=tk.LEFT, padx=5)

        # Velocity controls
        vel_frame = ttk.LabelFrame(dialog, text="Velocity")
        vel_frame.pack(fill=tk.X, padx=20, pady=10)

        vx_var = tk.DoubleVar(value=obj.velocity.x)
        vy_var = tk.DoubleVar(value=obj.velocity.y)

        ttk.Label(vel_frame, text="VX:").pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(
            vel_frame, from_=-500, to=500, textvariable=vx_var, width=8, increment=10
        ).pack(side=tk.LEFT, padx=5)
        ttk.Label(vel_frame, text="VY:").pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(
            vel_frame, from_=-500, to=500, textvariable=vy_var, width=8, increment=10
        ).pack(side=tk.LEFT, padx=5)

        # Color
        color_frame = ttk.LabelFrame(dialog, text="Appearance")
        color_frame.pack(fill=tk.X, padx=20, pady=10)

        color_var = tk.StringVar(value=getattr(obj, "color", "blue"))
        ttk.Label(color_frame, text="Color:").pack(side=tk.LEFT, padx=5)
        color_combo = ttk.Combobox(
            color_frame,
            textvariable=color_var,
            values=[
                "red",
                "blue",
                "green",
                "yellow",
                "purple",
                "orange",
                "black",
                "white",
            ],
        )
        color_combo.pack(side=tk.LEFT, padx=5)

        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)

        def apply_changes():
            try:
                # Update object properties
                game_manager.move_object(obj_name, x_var.get(), y_var.get())
                game_manager.set_object_velocity(obj_name, vx_var.get(), vy_var.get())
                obj.color = color_var.get()

                messagebox.showinfo(
                    "Success", f"Object '{obj_name}' updated successfully!"
                )
                self.refresh_objects()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update object: {e}")

        ttk.Button(button_frame, text="✅ Apply", command=apply_changes).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="❌ Cancel", command=dialog.destroy).pack(
            side=tk.LEFT, padx=5
        )

    def delete_object(self):
        """Delete selected object"""
        selection = self.objects_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an object to delete")
            return

        item = self.objects_tree.item(selection[0])
        obj_name = item["values"][0]

        if messagebox.askyesno("Confirm Delete", f"Delete object '{obj_name}'?"):
            try:
                game_manager = getattr(self.ide.interpreter, "game_manager", None)
                if game_manager:
                    game_manager.remove_object(obj_name)
                    messagebox.showinfo(
                        "Success", f"Object '{obj_name}' deleted successfully!"
                    )
                    self.refresh_objects()
                else:
                    messagebox.showerror("Error", "Game engine not available")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete object: {e}")

    def refresh_objects(self):
        """Refresh the objects list"""
        # Clear existing items
        for item in self.objects_tree.get_children():
            self.objects_tree.delete(item)

        try:
            game_manager = getattr(self.ide.interpreter, "game_manager", None)
            if game_manager and hasattr(game_manager, "game_objects"):
                for name, obj in game_manager.game_objects.items():
                    obj_type = getattr(obj, "obj_type", "unknown")
                    position = f"({obj.position.x:.1f}, {obj.position.y:.1f})"
                    size = f"{obj.width}x{obj.height}"
                    velocity = f"({obj.velocity.x:.1f}, {obj.velocity.y:.1f})"

                    self.objects_tree.insert(
                        "", "end", values=(name, obj_type, position, size, velocity)
                    )
        except Exception as e:
            print(f"Error refreshing objects: {e}")

    def clear_all_objects(self):
        """Clear all game objects"""
        if messagebox.askyesno(
            "Confirm", "Clear all game objects? This cannot be undone."
        ):
            try:
                game_manager = getattr(self.ide.interpreter, "game_manager", None)
                if game_manager:
                    game_manager.reset_world()
                    messagebox.showinfo("Success", "All game objects cleared!")
                    self.refresh_objects()
                else:
                    messagebox.showerror("Error", "Game engine not available")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear objects: {e}")

    def apply_gravity(self):
        """Apply gravity setting"""
        try:
            gravity = self.gravity_var.get()
            game_manager = getattr(self.ide.interpreter, "game_manager", None)
            if game_manager and hasattr(game_manager, "physics"):
                game_manager.physics.gravity = gravity
                messagebox.showinfo("Physics", f"Gravity set to {gravity:.1f} m/s²")
                self.update_physics_info()
            else:
                messagebox.showerror("Error", "Physics engine not available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set gravity: {e}")

    def start_physics(self):
        """Start physics simulation"""
        try:
            game_manager = getattr(self.ide.interpreter, "game_manager", None)
            if game_manager:
                game_manager.start_game_loop()
                messagebox.showinfo("Physics", "Physics simulation started")
                self.update_physics_info()
            else:
                messagebox.showerror("Error", "Game engine not available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start physics: {e}")

    def pause_physics(self):
        """Pause physics simulation"""
        try:
            game_manager = getattr(self.ide.interpreter, "game_manager", None)
            if game_manager:
                game_manager.running = False
                messagebox.showinfo("Physics", "Physics simulation paused")
                self.update_physics_info()
            else:
                messagebox.showerror("Error", "Game engine not available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to pause physics: {e}")

    def stop_physics(self):
        """Stop physics simulation"""
        try:
            game_manager = getattr(self.ide.interpreter, "game_manager", None)
            if game_manager:
                game_manager.stop_game_loop()
                messagebox.showinfo("Physics", "Physics simulation stopped")
                self.update_physics_info()
            else:
                messagebox.showerror("Error", "Game engine not available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop physics: {e}")

    def step_physics(self):
        """Single step physics simulation"""
        try:
            game_manager = getattr(self.ide.interpreter, "game_manager", None)
            if game_manager and hasattr(game_manager, "physics"):
                game_manager.physics.step(1.0 / 60.0)  # Single frame at 60 FPS
                messagebox.showinfo("Physics", "Physics stepped one frame")
                self.refresh_objects()
                self.update_physics_info()
            else:
                messagebox.showerror("Error", "Physics engine not available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to step physics: {e}")

    def update_physics_info(self):
        """Update physics information display"""
        try:
            game_manager = getattr(self.ide.interpreter, "game_manager", None)
            if game_manager:
                gravity = (
                    getattr(game_manager.physics, "gravity", 9.8)
                    if hasattr(game_manager, "physics")
                    else 9.8
                )
                active_objects = (
                    len(game_manager.game_objects)
                    if hasattr(game_manager, "game_objects")
                    else 0
                )
                frame_count = getattr(game_manager, "frame_count", 0)
                running = getattr(game_manager, "running", False)
                fps = getattr(game_manager, "fps", 60)

                info_text = f"""Physics System Status:

Gravity: {gravity:.1f} m/s²
Active Objects: {active_objects}
Frame Count: {frame_count}
Frame Rate: {fps} FPS
Simulation: {'Running' if running else 'Stopped'}
Total Time: {getattr(game_manager, 'total_time', 0):.2f}s

Physics Engine: {'Available' if hasattr(game_manager, 'physics') else 'Not Available'}
Renderer: {'Available' if hasattr(game_manager, 'renderer') else 'Not Available'}
Canvas: {'Connected' if getattr(game_manager, 'canvas', None) else 'Not Connected'}

Controls:
• Use Start/Stop to control simulation
• Use Single Step for frame-by-frame analysis
• Adjust gravity with the slider above
"""
            else:
                info_text = """Physics System Status:

⚠️ Game engine not initialized
Please run a game-related command first to initialize the engine.

Available Commands:
• CREATE_OBJECT - Create game objects
• START_PHYSICS - Initialize physics simulation
• SET_GRAVITY - Configure gravity settings
"""

            self.physics_info.delete("1.0", tk.END)
            self.physics_info.insert("1.0", info_text)

        except Exception as e:
            error_text = f"Error updating physics info: {e}"
            self.physics_info.delete("1.0", tk.END)
            self.physics_info.insert("1.0", error_text)

    def render_preview(self):
        """Render scene preview"""
        try:
            self.preview_canvas.delete("all")

            game_manager = getattr(self.ide.interpreter, "game_manager", None)
            if game_manager and hasattr(game_manager, "game_objects"):
                # Draw a basic representation of game objects
                canvas_width = self.preview_canvas.winfo_width() or 600
                canvas_height = self.preview_canvas.winfo_height() or 400

                if not game_manager.game_objects:
                    self.preview_canvas.create_text(
                        canvas_width // 2,
                        canvas_height // 2,
                        text="No game objects to preview\nCreate objects in the Game Objects tab",
                        font=("Arial", 12),
                        fill="gray",
                        justify=tk.CENTER,
                    )
                else:
                    # Scale factor to fit objects in preview
                    scale_x = canvas_width / 800  # Assuming game world is 800x600
                    scale_y = canvas_height / 600

                    for name, obj in game_manager.game_objects.items():
                        x = obj.position.x * scale_x
                        y = obj.position.y * scale_y
                        w = obj.width * scale_x
                        h = obj.height * scale_y

                        # Choose color
                        color = getattr(obj, "color", "blue")

                        # Draw object
                        self.preview_canvas.create_rectangle(
                            x, y, x + w, y + h, fill=color, outline="black"
                        )
                        self.preview_canvas.create_text(
                            x + w // 2,
                            y + h // 2,
                            text=name,
                            font=("Arial", 8),
                            fill="white",
                        )

                    # Draw physics info
                    info_text = f"Objects: {len(game_manager.game_objects)}"
                    if hasattr(game_manager, "physics"):
                        info_text += f" | Gravity: {getattr(game_manager.physics, 'gravity', 9.8):.1f}"
                    self.preview_canvas.create_text(
                        10,
                        10,
                        text=info_text,
                        anchor=tk.NW,
                        font=("Arial", 10),
                        fill="black",
                    )
            else:
                self.preview_canvas.create_text(
                    300,
                    200,
                    text="Game Engine Not Available\nInitialize game system first",
                    font=("Arial", 14),
                    fill="red",
                    justify=tk.CENTER,
                )

        except Exception as e:
            self.preview_canvas.create_text(
                300,
                200,
                text=f"Preview Error:\n{str(e)[:100]}",
                font=("Arial", 12),
                fill="red",
                justify=tk.CENTER,
            )

    def toggle_auto_refresh(self):
        """Toggle auto-refresh of preview"""
        self.auto_refresh = not self.auto_refresh
        status = "enabled" if self.auto_refresh else "disabled"
        messagebox.showinfo("Auto Refresh", f"Auto-refresh {status}")

        if self.auto_refresh:
            self._auto_refresh_preview()

    def _auto_refresh_preview(self):
        """Internal auto-refresh method"""
        if self.auto_refresh and self.window:
            self.render_preview()
            self.window.after(1000, self._auto_refresh_preview)  # Refresh every second

    def save_scene(self):
        """Save current scene"""
        try:
            from tkinter import filedialog
            import json

            game_manager = getattr(self.ide.interpreter, "game_manager", None)
            if not game_manager or not hasattr(game_manager, "game_objects"):
                messagebox.showerror("Error", "No game objects to save")
                return

            filename = filedialog.asksaveasfilename(
                title="Save Scene",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            )

            if filename:
                scene_data = {
                    "objects": [],
                    "physics": {
                        "gravity": (
                            getattr(game_manager.physics, "gravity", 9.8)
                            if hasattr(game_manager, "physics")
                            else 9.8
                        )
                    },
                }

                for name, obj in game_manager.game_objects.items():
                    obj_data = {
                        "name": name,
                        "type": getattr(obj, "obj_type", "sprite"),
                        "position": {"x": obj.position.x, "y": obj.position.y},
                        "size": {"width": obj.width, "height": obj.height},
                        "velocity": {"x": obj.velocity.x, "y": obj.velocity.y},
                        "color": getattr(obj, "color", "blue"),
                    }
                    scene_data["objects"].append(obj_data)

                with open(filename, "w") as f:
                    json.dump(scene_data, f, indent=2)

                messagebox.showinfo("Success", f"Scene saved to {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save scene: {e}")

    def load_scene(self):
        """Load scene from file"""
        try:
            from tkinter import filedialog
            import json

            filename = filedialog.askopenfilename(
                title="Load Scene",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            )

            if filename:
                with open(filename, "r") as f:
                    scene_data = json.load(f)

                game_manager = getattr(self.ide.interpreter, "game_manager", None)
                if not game_manager:
                    messagebox.showerror("Error", "Game engine not available")
                    return

                # Clear existing objects
                game_manager.reset_world()

                # Set physics
                if "physics" in scene_data and hasattr(game_manager, "physics"):
                    game_manager.physics.gravity = scene_data["physics"].get(
                        "gravity", 9.8
                    )
                    self.gravity_var.set(game_manager.physics.gravity)

                # Load objects
                for obj_data in scene_data.get("objects", []):
                    game_manager.create_object(
                        obj_data["name"],
                        obj_data.get("type", "sprite"),
                        obj_data["position"]["x"],
                        obj_data["position"]["y"],
                        obj_data["size"]["width"],
                        obj_data["size"]["height"],
                        obj_data.get("color", "blue"),
                    )

                    # Set velocity
                    if "velocity" in obj_data:
                        game_manager.set_object_velocity(
                            obj_data["name"],
                            obj_data["velocity"]["x"],
                            obj_data["velocity"]["y"],
                        )

                messagebox.showinfo("Success", f"Scene loaded from {filename}")
                self.refresh_objects()
                self.render_preview()
                self.update_physics_info()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load scene: {e}")

    def run_demo(self, demo_type):
        """Run game demonstration"""
        try:
            game_manager = getattr(self.ide.interpreter, "game_manager", None)
            if not game_manager:
                messagebox.showerror("Error", "Game engine not available")
                return

            # Clear existing objects
            game_manager.reset_world()

            if demo_type == "pong":
                # Create Pong demo
                game_manager.create_object(
                    "left_paddle", "paddle", 20, 250, 10, 60, "white"
                )
                game_manager.create_object(
                    "right_paddle", "paddle", 770, 250, 10, 60, "white"
                )
                game_manager.create_object("ball", "ball", 400, 300, 10, 10, "white")
                game_manager.set_object_velocity("ball", 100, 50)

            elif demo_type == "physics":
                # Create physics demo with falling objects
                import random

                for i in range(5):
                    x = random.randint(50, 750)
                    color = random.choice(["red", "blue", "green", "yellow", "purple"])
                    game_manager.create_object(
                        f"ball_{i}", "ball", x, 50 + i * 30, 20, 20, color
                    )
                # Create platforms
                game_manager.create_platform(100, 500, 200, 20)
                game_manager.create_platform(400, 400, 200, 20)
                game_manager.create_platform(600, 300, 150, 20)

            elif demo_type == "platformer":
                # Create platformer demo
                game_manager.create_object("player", "player", 50, 450, 20, 30, "blue")
                # Create platforms
                game_manager.create_platform(0, 580, 800, 20)  # Ground
                game_manager.create_platform(200, 500, 150, 20)
                game_manager.create_platform(400, 400, 150, 20)
                game_manager.create_platform(600, 300, 150, 20)
                # Create enemies
                game_manager.create_object("enemy1", "enemy", 300, 470, 15, 15, "red")
                game_manager.create_object("enemy2", "enemy", 500, 370, 15, 15, "red")

            elif demo_type == "snake":
                # Create snake demo
                game_manager.create_object(
                    "snake_head", "snake", 400, 300, 20, 20, "green"
                )
                game_manager.create_object(
                    "snake_body1", "snake", 380, 300, 20, 20, "darkgreen"
                )
                game_manager.create_object(
                    "snake_body2", "snake", 360, 300, 20, 20, "darkgreen"
                )
                game_manager.create_object("food", "food", 200, 200, 15, 15, "red")
                game_manager.set_object_velocity("snake_head", 20, 0)

            messagebox.showinfo(
                "Demo Started",
                f"{demo_type.title()} demo created successfully!\nUse Physics tab to start simulation.",
            )
            self.refresh_objects()
            self.render_preview()
            self.update_physics_info()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to run {demo_type} demo: {e}")

    def run_custom_demo(self):
        """Run custom demo with parameters"""
        try:
            objects = self.demo_objects.get()
            gravity = self.demo_gravity.get()

            game_manager = getattr(self.ide.interpreter, "game_manager", None)
            if not game_manager:
                messagebox.showerror("Error", "Game engine not available")
                return

            # Clear existing objects
            game_manager.reset_world()

            # Set gravity
            if hasattr(game_manager, "physics"):
                game_manager.physics.gravity = gravity
                self.gravity_var.set(gravity)

            # Create random objects
            import random

            colors = [
                "red",
                "blue",
                "green",
                "yellow",
                "purple",
                "orange",
                "pink",
                "cyan",
            ]

            for i in range(objects):
                x = random.randint(50, 750)
                y = random.randint(50, 200)
                size = random.randint(10, 40)
                color = random.choice(colors)
                vx = random.randint(-50, 50)
                vy = random.randint(-20, 20)

                game_manager.create_object(
                    f"obj_{i}", "sprite", x, y, size, size, color
                )
                game_manager.set_object_velocity(f"obj_{i}", vx, vy)

            # Create some platforms
            game_manager.create_platform(0, 580, 800, 20)  # Ground
            game_manager.create_platform(200, 450, 150, 20)
            game_manager.create_platform(450, 350, 150, 20)

            messagebox.showinfo(
                "Custom Demo",
                f"Custom demo created with {objects} objects and gravity {gravity}!\nUse Physics tab to start simulation.",
            )
            self.refresh_objects()
            self.render_preview()
            self.update_physics_info()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to run custom demo: {e}")

    def close(self):
        """Close the dialog"""
        if self.window:
            self.window.destroy()
            self.window = None


class VirtualEnvironmentManager:
    """Manages virtual environment for Time_Warp IDE and package installation"""

    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
        self.venv_dir = os.path.join(self.base_dir, "timewarp_venv")
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
            self.python_exe = os.path.join(self.venv_dir, "bin", "python")
            self.pip_exe = os.path.join(self.venv_dir, "bin", "pip")

            self.log_status(f"Virtual environment created at: {self.venv_dir}")
            return True

        except Exception as e:
            self.log_status(f"Failed to create virtual environment: {e}")
            return False

    def initialize(self) -> bool:
        """Initialize virtual environment for Time_Warp"""
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
            result = subprocess.run(
                [str(self.pip_exe), "install", package_spec],
                capture_output=True,
                text=True,
                timeout=300,
            )  # 5 minute timeout

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

    def install_timewarp_dependencies(self) -> bool:
        """Install all dependencies needed for Time_Warp functionality"""
        dependencies = [
            ("matplotlib", "3.7.0"),  # For plotting features
            ("pillow", "10.0.0"),  # For image processing
            ("requests", "2.31.0"),  # For web operations
        ]

        self.log_status("Installing Time_Warp dependencies...")
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
            result = subprocess.run(
                [str(self.pip_exe), "list", "--format=freeze"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                return result.stdout.strip().split("\n")
            else:
                self.log_status(f"Failed to list packages: {result.stderr}")
                return []

        except Exception as e:
            self.log_status(f"Error listing packages: {e}")
            return []
