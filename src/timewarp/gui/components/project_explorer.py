"""
Project Explorer for Time_Warp IDE
File tree view for managing Time_Warp projects and files.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog


class ProjectExplorer:
    """File tree view for managing Time_Warp projects and files"""

    def __init__(self, ide):
        self.ide = ide
        self.current_project_path = None
        self.tree_widget = None
        self.explorer_window = None
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
            "spt": "🎯",  # Time_Warp files
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
        item = self.tree_widget.selection()[0] if self.tree_widget.selection() else None
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
        item = self.tree_widget.selection()[0] if self.tree_widget.selection() else None
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
        item = self.tree_widget.identify_row(event.y)
        if not item:
            return

        self.tree_widget.selection_set(item)
        values = self.tree_widget.item(item, "values")

        context_menu = tk.Menu(self.tree_widget, tearoff=0)

        if len(values) >= 2:
            file_path, item_type = values[0], values[1]

            if item_type == "file":
                context_menu.add_command(
                    label="Open", command=lambda: self.open_file(file_path)
                )
                context_menu.add_separator()
                context_menu.add_command(
                    label="Rename", command=lambda: self.rename_item(file_path)
                )
                context_menu.add_command(
                    label="Delete", command=lambda: self.delete_item(file_path)
                )
            elif item_type == "folder":
                context_menu.add_command(
                    label="New File", command=lambda: self.new_file_in_folder(file_path)
                )
                context_menu.add_separator()
                context_menu.add_command(
                    label="Rename", command=lambda: self.rename_item(file_path)
                )
                context_menu.add_command(
                    label="Delete", command=lambda: self.delete_item(file_path)
                )

        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def rename_item(self, item_path):
        """Rename a file or folder"""
        old_name = os.path.basename(item_path)
        new_name = simpledialog.askstring(
            "Rename", f"New name for '{old_name}':", initialvalue=old_name
        )
        if new_name and new_name != old_name:
            try:
                new_path = os.path.join(os.path.dirname(item_path), new_name)
                os.rename(item_path, new_path)
                self.refresh_tree()
            except Exception as e:
                messagebox.showerror("Error", f"Could not rename:\n{str(e)}")

    def delete_item(self, item_path):
        """Delete a file or folder"""
        item_name = os.path.basename(item_path)
        if messagebox.askyesno(
            "Delete", f"Are you sure you want to delete '{item_name}'?"
        ):
            try:
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    import shutil

                    shutil.rmtree(item_path)
                self.refresh_tree()
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete:\n{str(e)}")

    def new_file_in_folder(self, folder_path):
        """Create a new file in specific folder"""
        old_project_path = self.current_project_path
        self.current_project_path = folder_path
        self.new_file()
        self.current_project_path = old_project_path
