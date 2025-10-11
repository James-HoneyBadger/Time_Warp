#!/usr/bin/env python3
"""
File Explorer Panel for Time_Warp IDE
Tree-view file navigation with project support
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import os
from pathlib import Path
from typing import Dict, List, Optional, Callable, Union


class FileExplorer:
    """File explorer panel with project tree view"""
    
    def __init__(self, parent_widget, open_file_callback: Optional[Callable[[str], None]] = None):
        self.parent = parent_widget
        self.open_file_callback = open_file_callback
        self.current_project_path: Optional[str] = None
        
        self.setup_ui()
        self.populate_tree()
        
    def setup_ui(self):
        """Setup the file explorer UI"""
        # Main frame
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with project info
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        ttk.Label(header_frame, text="📁 Project Explorer", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        
        # Toolbar buttons
        toolbar_frame = ttk.Frame(self.frame)
        toolbar_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(
            toolbar_frame, 
            text="📂", 
            width=3,
            command=self.open_folder
        ).pack(side=tk.LEFT, padx=1)
        
        ttk.Button(
            toolbar_frame,
            text="🏠",
            width=3, 
            command=self.go_home
        ).pack(side=tk.LEFT, padx=1)
        
        ttk.Button(
            toolbar_frame,
            text="🔄",
            width=3,
            command=self.refresh
        ).pack(side=tk.LEFT, padx=1)
        
        ttk.Button(
            toolbar_frame,
            text="📄",
            width=3,
            command=self.new_file
        ).pack(side=tk.LEFT, padx=1)
        
        # Tree view
        tree_frame = ttk.Frame(self.frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollable tree
        self.tree = ttk.Treeview(tree_frame, show='tree')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack tree and scrollbars
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind events
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<Button-3>', self.on_right_click)  # Right-click context menu
        
        # Create context menu
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="Open", command=self.open_selected)
        self.context_menu.add_command(label="Open in New Tab", command=self.open_selected_new_tab)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="New File", command=self.new_file)
        self.context_menu.add_command(label="New Folder", command=self.new_folder)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Rename", command=self.rename_selected)
        self.context_menu.add_command(label="Delete", command=self.delete_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Properties", command=self.show_properties)
        
    def populate_tree(self):
        """Populate tree with files and folders"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Start with current project or home directory
        root_path = self.current_project_path or str(Path.home())
        
        try:
            self.add_directory_to_tree('', root_path, is_root=True)
        except PermissionError:
            # Fallback to home directory if permission denied
            self.current_project_path = str(Path.home())
            self.add_directory_to_tree('', self.current_project_path, is_root=True)
            
    def add_directory_to_tree(self, parent_item: str, dir_path: str, is_root: bool = False):
        """Add directory and its contents to tree"""
        try:
            path_obj = Path(dir_path)
            
            # Skip hidden directories unless root
            if not is_root and path_obj.name.startswith('.'):
                return
                
            # Create directory item
            dir_item = self.tree.insert(
                parent_item, 
                'end', 
                text=f"📁 {path_obj.name if not is_root else str(path_obj)}",
                values=[str(path_obj), 'directory'],
                open=is_root
            )
            
            # Get directory contents
            try:
                items = list(path_obj.iterdir())
                # Sort: directories first, then files
                items.sort(key=lambda x: (x.is_file(), x.name.lower()))
                
                for item in items:
                    if item.is_dir():
                        # Add subdirectory (lazy loading)
                        sub_item = self.tree.insert(
                            dir_item,
                            'end',
                            text=f"📁 {item.name}",
                            values=[str(item), 'directory']
                        )
                        # Add placeholder for lazy loading
                        self.tree.insert(sub_item, 'end', text='Loading...', values=['', 'placeholder'])
                    else:
                        # Add file with appropriate icon
                        icon = self.get_file_icon(item.suffix)
                        self.tree.insert(
                            dir_item,
                            'end',
                            text=f"{icon} {item.name}",
                            values=[str(item), 'file']
                        )
                        
            except PermissionError:
                # Add error indicator
                self.tree.insert(
                    dir_item,
                    'end',
                    text="❌ Permission Denied",
                    values=['', 'error']
                )
                
                        
        except Exception as e:
            print(f"Error adding directory {path_obj}: {e}")
            
    def get_file_icon(self, extension: str) -> str:
        """Get appropriate icon for file type"""
        extension = extension.lower()
        icon_map = {
            '.py': '🐍',
            '.js': '📜',
            '.pilot': '✈️',
            '.bas': '🔢',
            '.logo': '🐢',
            '.pl': '🔷',
            '.txt': '📄',
            '.md': '📝',
            '.json': '📋',
            '.html': '🌐',
            '.css': '🎨',
            '.xml': '📰',
            '.png': '🖼️',
            '.jpg': '🖼️',
            '.jpeg': '🖼️',
            '.gif': '🖼️',
            '.pdf': '📕',
            '.zip': '📦',
            '.tar': '📦',
            '.gz': '📦'
        }
        return icon_map.get(extension, '📄')
        
    def on_double_click(self, event):
        """Handle double-click on tree item"""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if not item:
            return
            
        values = self.tree.item(item, 'values')
        if not values:
            return
            
        path, item_type = values[0], values[1]
        
        if item_type == 'file':
            self.open_file(path)
        elif item_type == 'directory':
            # Expand/collapse directory
            if self.tree.item(item, 'open'):
                self.tree.item(item, open=False)
            else:
                self.expand_directory(item, path)
                
    def expand_directory(self, item, path):
        """Expand directory and load contents"""
        # Check if already loaded (not placeholder)
        children = self.tree.get_children(item)
        if children and self.tree.item(children[0], 'text') != 'Loading...':
            self.tree.item(item, open=True)
            return
            
        # Clear placeholder
        for child in children:
            self.tree.delete(child)
            
        # Load directory contents
        self.add_directory_contents(item, path)
        self.tree.item(item, open=True)
        
    def add_directory_contents(self, parent_item, dir_path):
        """Add contents of directory to tree"""
        try:
            dir_path = Path(dir_path)
            items = list(dir_path.iterdir())
            items.sort(key=lambda x: (x.is_file(), x.name.lower()))
            
            for item in items:
                if item.name.startswith('.'):  # Skip hidden files
                    continue
                    
                if item.is_dir():
                    sub_item = self.tree.insert(
                        parent_item,
                        'end',
                        text=f"📁 {item.name}",
                        values=[str(item), 'directory']
                    )
                    # Add placeholder for lazy loading
                    self.tree.insert(sub_item, 'end', text='Loading...', values=['', 'placeholder'])
                else:
                    icon = self.get_file_icon(item.suffix)
                    self.tree.insert(
                        parent_item,
                        'end',
                        text=f"{icon} {item.name}",
                        values=[str(item), 'file']
                    )
                    
        except PermissionError:
            self.tree.insert(
                parent_item,
                'end',
                text="❌ Permission Denied",
                values=['', 'error']
            )
            
    def on_right_click(self, event):
        """Handle right-click context menu"""
        # Select item under cursor
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
            
    def open_selected(self):
        """Open selected file"""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if not item:
            return
            
        values = self.tree.item(item, 'values')
        if values and values[1] == 'file':
            self.open_file(values[0])
            
    def open_selected_new_tab(self):
        """Open selected file in new tab"""
        self.open_selected()  # Same behavior for now
        
    def open_file(self, file_path: str):
        """Open file using callback"""
        if self.open_file_callback:
            self.open_file_callback(file_path)
            
    def open_folder(self):
        """Open folder dialog and set as project root"""
        folder_path = filedialog.askdirectory(title="Select Project Folder")
        if folder_path:
            self.current_project_path = folder_path
            self.populate_tree()
            
    def go_home(self):
        """Navigate to home directory"""
        self.current_project_path = str(Path.home())
        self.populate_tree()
        
    def refresh(self):
        """Refresh tree view"""
        self.populate_tree()
        
    def new_file(self):
        """Create new file in selected directory"""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if item:
            values = self.tree.item(item, 'values')
            if values[1] == 'directory':
                target_dir = values[0]
            else:
                # Get parent directory
                parent = self.tree.parent(item)
                if parent:
                    target_dir = self.tree.item(parent, 'values')[0]
                else:
                    target_dir = self.current_project_path or str(Path.home())
        else:
            target_dir = self.current_project_path or str(Path.home())
            
        filename = simpledialog.askstring(
            "New File",
            "Enter filename:",
            initialvalue="untitled.py"
        )
        
        if filename:
            file_path = Path(target_dir) / filename
            try:
                # Create empty file
                file_path.touch()
                self.refresh()
                # Open in editor
                self.open_file(str(file_path))
            except Exception as e:
                messagebox.showerror("Error", f"Could not create file: {e}")
                
    def new_folder(self):
        """Create new folder in selected directory"""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if item:
            values = self.tree.item(item, 'values')
            if values[1] == 'directory':
                target_dir = values[0]
            else:
                parent = self.tree.parent(item)
                target_dir = self.tree.item(parent, 'values')[0] if parent else self.current_project_path
        else:
            target_dir = self.current_project_path or str(Path.home())
            
        foldername = simpledialog.askstring(
            "New Folder",
            "Enter folder name:",
            initialvalue="New Folder"
        )
        
        if foldername and target_dir:
            try:
                folder_path = Path(target_dir) / foldername
                folder_path.mkdir(exist_ok=True)
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", f"Could not create folder: {e}")
                
    def rename_selected(self):
        """Rename selected file or folder"""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if not item:
            return
            
        values = self.tree.item(item, 'values')
        if not values or values[1] in ['error', 'placeholder']:
            return
            
        old_path = Path(values[0])
        new_name = simpledialog.askstring(
            "Rename",
            "Enter new name:",
            initialvalue=old_path.name
        )
        
        if new_name and new_name != old_path.name:
            try:
                new_path = old_path.parent / new_name
                old_path.rename(new_path)
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", f"Could not rename: {e}")
                
    def delete_selected(self):
        """Delete selected file or folder"""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if not item:
            return
            
        values = self.tree.item(item, 'values')
        if not values or values[1] in ['error', 'placeholder']:
            return
            
        path = Path(values[0])
        item_type = "folder" if values[1] == 'directory' else "file"
        
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete this {item_type}?\n\n{path.name}"
        )
        
        if result:
            try:
                if path.is_dir():
                    import shutil
                    shutil.rmtree(path)
                else:
                    path.unlink()
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete: {e}")
                
    def show_properties(self):
        """Show properties of selected file/folder"""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if not item:
            return
            
        values = self.tree.item(item, 'values')
        if not values or values[1] in ['error', 'placeholder']:
            return
            
        path = Path(values[0])
        
        try:
            stat = path.stat()
            size = stat.st_size
            
            # Format size
            if size < 1024:
                size_str = f"{size} bytes"
            elif size < 1024 * 1024:
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size / (1024 * 1024):.1f} MB"
                
            # Format dates
            import datetime
            modified = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            
            info = f"""Name: {path.name}
Type: {values[1].title()}
Size: {size_str}
Location: {path.parent}
Modified: {modified}"""
            
            messagebox.showinfo("Properties", info)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not get properties: {e}")
            
    def get_current_project_path(self) -> Optional[str]:
        """Get current project path"""
        return self.current_project_path
        
    def set_project_path(self, path: str):
        """Set project path and refresh"""
        self.current_project_path = path
        self.populate_tree()
    
    def apply_theme(self, colors):
        """Apply theme colors to file explorer"""
        try:
            # Configure treeview style first
            
            # Configure treeview style
            style = ttk.Style()
            style.configure(
                "Themed.Treeview",
                background=colors["bg_primary"],
                foreground=colors["text_primary"],
                fieldbackground=colors["bg_secondary"],
                borderwidth=0,
                relief="flat"
            )
            
            style.configure(
                "Themed.Treeview.Heading",
                background=colors["bg_tertiary"],
                foreground=colors["text_primary"],
                borderwidth=1,
                relief="flat"
            )
            
            # Apply the themed style
            self.tree.configure(style="Themed.Treeview")
            
        except Exception as e:
            print(f"⚠️ FileExplorer theme error: {e}")