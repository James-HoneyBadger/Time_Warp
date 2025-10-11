"""
Time_Warp Plugin System
Provides extensible plugin architecture for Time_Warp IDE
"""

import os
import json
import importlib.util
import sys
from typing import Dict, List, Optional, Any
import tkinter as tk
from tkinter import ttk, messagebox


class TimeWarpPlugin:
    """Base class for Time_Warp plugins"""

    def __init__(self, ide_instance):
        self.ide = ide_instance
        self.name = "Base Plugin"
        self.version = "1.0.0"
        self.author = "Unknown"
        self.description = "Base plugin class"

    def activate(self):
        """Called when plugin is enabled"""
        pass

    def deactivate(self):
        """Called when plugin is disabled"""
        pass

    def get_info(self) -> Dict[str, Any]:
        """Get plugin information"""
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
        }


class PluginManager:
    """Manages Time_Warp plugins - loading, activation, and management"""

    def __init__(self, ide_instance):
        self.ide = ide_instance
        self.plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")
        self.loaded_plugins: Dict[str, TimeWarpPlugin] = {}
        self.active_plugins: Dict[str, TimeWarpPlugin] = {}
        self.plugin_manifests: Dict[str, Dict] = {}

        # Ensure plugins directory exists
        if not os.path.exists(self.plugins_dir):
            os.makedirs(self.plugins_dir)

    def scan_plugins(self) -> List[str]:
        """Scan plugins directory for available plugins"""
        available_plugins = []

        if not os.path.exists(self.plugins_dir):
            return available_plugins

        for item in os.listdir(self.plugins_dir):
            plugin_path = os.path.join(self.plugins_dir, item)

            if os.path.isdir(plugin_path):
                manifest_path = os.path.join(plugin_path, "manifest.json")
                plugin_file = os.path.join(plugin_path, "plugin.py")

                if os.path.exists(manifest_path) and os.path.exists(plugin_file):
                    available_plugins.append(item)

        return available_plugins

    def load_plugin_manifest(self, plugin_name: str) -> Optional[Dict]:
        """Load plugin manifest file"""
        manifest_path = os.path.join(self.plugins_dir, plugin_name, "manifest.json")

        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
                self.plugin_manifests[plugin_name] = manifest
                return manifest
        except Exception as e:
            print(f"Error loading manifest for {plugin_name}: {e}")
            return None

    def load_plugin(self, plugin_name: str) -> bool:
        """Load a plugin from the plugins directory"""
        if plugin_name in self.loaded_plugins:
            return True

        plugin_path = os.path.join(self.plugins_dir, plugin_name)
        plugin_file = os.path.join(plugin_path, "plugin.py")

        if not os.path.exists(plugin_file):
            print(f"Plugin file not found: {plugin_file}")
            return False

        # Load manifest
        manifest = self.load_plugin_manifest(plugin_name)
        if not manifest:
            return False

        try:
            # Load the plugin module
            spec = importlib.util.spec_from_file_location(
                f"plugin_{plugin_name}", plugin_file
            )
            if spec is None or spec.loader is None:
                print(f"Could not load plugin spec for {plugin_name}")
                return False

            plugin_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin_module)

            # Create plugin instance
            if hasattr(plugin_module, "TimeWarpPlugin"):
                plugin_instance = plugin_module.Time_WarpPlugin(self.ide)

                # Set plugin info from manifest
                if hasattr(plugin_instance, "name"):
                    plugin_instance.name = manifest.get("name", plugin_name)
                if hasattr(plugin_instance, "version"):
                    plugin_instance.version = manifest.get("version", "1.0.0")
                if hasattr(plugin_instance, "author"):
                    plugin_instance.author = manifest.get("author", "Unknown")
                if hasattr(plugin_instance, "description"):
                    plugin_instance.description = manifest.get("description", "")

                self.loaded_plugins[plugin_name] = plugin_instance
                print(f"Plugin loaded: {plugin_name}")
                return True
            else:
                print(f"Plugin {plugin_name} does not contain a TimeWarpPlugin class")
                return False

        except Exception as e:
            print(f"Error loading plugin {plugin_name}: {e}")
            return False

    def activate_plugin(self, plugin_name: str) -> bool:
        """Activate a loaded plugin"""
        if plugin_name not in self.loaded_plugins:
            if not self.load_plugin(plugin_name):
                return False

        if plugin_name in self.active_plugins:
            return True  # Already active

        try:
            plugin = self.loaded_plugins[plugin_name]
            plugin.activate()
            self.active_plugins[plugin_name] = plugin
            print(f"Plugin activated: {plugin_name}")
            return True
        except Exception as e:
            print(f"Error activating plugin {plugin_name}: {e}")
            return False

    def deactivate_plugin(self, plugin_name: str) -> bool:
        """Deactivate an active plugin"""
        if plugin_name not in self.active_plugins:
            return True  # Already inactive

        try:
            plugin = self.active_plugins[plugin_name]
            plugin.deactivate()
            del self.active_plugins[plugin_name]
            print(f"Plugin deactivated: {plugin_name}")
            return True
        except Exception as e:
            print(f"Error deactivating plugin {plugin_name}: {e}")
            return False

    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin completely"""
        # Deactivate first if active
        if plugin_name in self.active_plugins:
            self.deactivate_plugin(plugin_name)

        if plugin_name in self.loaded_plugins:
            del self.loaded_plugins[plugin_name]

        if plugin_name in self.plugin_manifests:
            del self.plugin_manifests[plugin_name]

        print(f"Plugin unloaded: {plugin_name}")
        return True

    def get_plugin_info(self, plugin_name: str) -> Optional[Dict]:
        """Get information about a plugin"""
        if plugin_name in self.loaded_plugins:
            plugin = self.loaded_plugins[plugin_name]
            return plugin.get_info()
        elif plugin_name in self.plugin_manifests:
            return self.plugin_manifests[plugin_name]
        else:
            manifest = self.load_plugin_manifest(plugin_name)
            return manifest

    def list_available_plugins(self) -> List[str]:
        """List all available plugins"""
        return self.scan_plugins()

    def list_loaded_plugins(self) -> List[str]:
        """List all loaded plugins"""
        return list(self.loaded_plugins.keys())

    def list_active_plugins(self) -> List[str]:
        """List all active plugins"""
        return list(self.active_plugins.keys())

    def is_plugin_active(self, plugin_name: str) -> bool:
        """Check if a plugin is active"""
        return plugin_name in self.active_plugins

    def is_plugin_loaded(self, plugin_name: str) -> bool:
        """Check if a plugin is loaded"""
        return plugin_name in self.loaded_plugins


class PluginManagerDialog:
    """Plugin management interface"""

    def __init__(self, ide_instance, plugin_manager: PluginManager):
        self.ide = ide_instance
        self.plugin_manager = plugin_manager
        self.window = None

    def show(self):
        """Show the plugin management dialog"""
        if self.window:
            self.window.lift()
            return

        self.window = tk.Toplevel(self.ide.root)
        self.window.title("🔌 Plugin Manager")
        self.window.geometry("800x600")
        self.window.transient(self.ide.root)

        # Create main layout
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(
            header_frame, text="🔌 Time_Warp Plugin Manager", font=("Arial", 16, "bold")
        ).pack(side=tk.LEFT)
        ttk.Button(header_frame, text="🔄 Refresh", command=self.refresh_plugins).pack(
            side=tk.RIGHT
        )

        # Create notebook for different plugin sections
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Installed Plugins Tab
        installed_frame = ttk.Frame(notebook)
        notebook.add(installed_frame, text="📦 Installed")
        self.setup_installed_tab(installed_frame)

        # Available Plugins Tab
        available_frame = ttk.Frame(notebook)
        notebook.add(available_frame, text="🌐 Available")
        self.setup_available_tab(available_frame)

        # Create Plugin Tab
        create_frame = ttk.Frame(notebook)
        notebook.add(create_frame, text="⚙️ Create Plugin")
        self.setup_create_tab(create_frame)

        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self.close)

        # Initialize
        self.refresh_plugins()

    def setup_installed_tab(self, parent):
        """Setup the installed plugins tab"""
        # Plugin list
        list_frame = ttk.LabelFrame(parent, text="Installed Plugins")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Treeview for plugins
        columns = ("Name", "Version", "Status", "Description")
        self.plugin_tree = ttk.Treeview(
            list_frame, columns=columns, show="headings", height=15
        )

        for col in columns:
            self.plugin_tree.heading(col, text=col)
            self.plugin_tree.column(col, width=150 if col != "Description" else 300)

        self.plugin_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        tree_scroll = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.plugin_tree.yview
        )
        self.plugin_tree.config(yscrollcommand=tree_scroll.set)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Plugin details
        details_frame = ttk.LabelFrame(parent, text="Plugin Details")
        details_frame.pack(fill=tk.X, padx=5, pady=5)

        self.details_text = tk.Text(
            details_frame, height=6, font=("Arial", 10), wrap=tk.WORD
        )
        details_scroll = ttk.Scrollbar(
            details_frame, orient=tk.VERTICAL, command=self.details_text.yview
        )
        self.details_text.config(yscrollcommand=details_scroll.set)
        self.details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        details_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Control buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(button_frame, text="✅ Enable", command=self.enable_plugin).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="❌ Disable", command=self.disable_plugin).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(
            button_frame, text="🗑️ Uninstall", command=self.uninstall_plugin
        ).pack(side=tk.LEFT, padx=5)

        # Bind selection event
        self.plugin_tree.bind("<<TreeviewSelect>>", self.on_plugin_select)

    def setup_available_tab(self, parent):
        """Setup the available plugins tab"""
        # Available plugins list
        available_list_frame = ttk.LabelFrame(parent, text="Available Plugins")
        available_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.available_tree = ttk.Treeview(
            available_list_frame,
            columns=("Name", "Version", "Author", "Description"),
            show="headings",
            height=12,
        )

        for col in self.available_tree["columns"]:
            self.available_tree.heading(col, text=col)
            self.available_tree.column(col, width=150 if col != "Description" else 300)

        self.available_tree.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5
        )

        available_scroll = ttk.Scrollbar(
            available_list_frame, orient=tk.VERTICAL, command=self.available_tree.yview
        )
        self.available_tree.config(yscrollcommand=available_scroll.set)
        available_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Install controls
        install_frame = ttk.Frame(parent)
        install_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            install_frame, text="⬇️ Install Selected", command=self.install_plugin
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            install_frame,
            text="🔄 Refresh Available",
            command=self.load_available_plugins,
        ).pack(side=tk.LEFT, padx=5)

    def setup_create_tab(self, parent):
        """Setup the create plugin tab"""
        ttk.Label(
            parent, text="Plugin Development Guide", font=("Arial", 14, "bold")
        ).pack(pady=10)

        guide_text = tk.Text(parent, height=25, font=("Arial", 10), wrap=tk.WORD)
        guide_scroll = ttk.Scrollbar(
            parent, orient=tk.VERTICAL, command=guide_text.yview
        )
        guide_text.config(yscrollcommand=guide_scroll.set)
        guide_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        guide_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        plugin_guide = """🛠️ Time_Warp PLUGIN DEVELOPMENT GUIDE

📋 Plugin Structure:
A Time_Warp plugin is a Python module that extends the IDE functionality.

Required Files:
• plugin.py - Main plugin code
• manifest.json - Plugin metadata
• README.md - Documentation

📄 Sample manifest.json:
{
  "name": "My Plugin",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "Plugin description",
  "entry_point": "plugin.py",
  "api_version": "2.0",
  "permissions": ["editor", "filesystem"]
}

🐍 Sample plugin.py:
from plugins import TimeWarpPlugin

class TimeWarpPlugin(TimeWarpPlugin):
    def __init__(self, ide_instance):
        super().__init__(ide_instance)
        self.name = "My Plugin"
        self.version = "1.0.0"
        self.author = "Your Name"
        self.description = "My awesome plugin"
    
    def activate(self):
        # Called when plugin is enabled
        self.add_menu_items()
    
    def deactivate(self):
        # Called when plugin is disabled
        self.remove_menu_items()
    
    def add_menu_items(self):
        # Add custom menu items
        pass

🔧 Available APIs:
• Editor access: self.ide.editor
• Menu system: self.ide.menubar
• Status bar: self.ide.status_label
• Interpreter: self.ide.interpreter
• File operations: Standard Python file I/O

📦 Plugin Types:
• Syntax Highlighters - Custom language support
• Code Generators - Template and snippet tools
• Export Tools - Custom file format support
• Debugging Tools - Enhanced debugging features
• Learning Aids - Educational enhancements

🚀 Getting Started:
1. Create a new folder in the plugins directory
2. Write the manifest.json file
3. Implement the plugin class in plugin.py
4. Test with the Time_Warp Plugin API
5. Enable through Plugin Manager

💡 Best Practices:
• Keep plugins lightweight and focused
• Handle errors gracefully
• Provide clear user feedback
• Follow Python coding standards
• Document your plugin thoroughly"""

        guide_text.insert("1.0", plugin_guide)
        guide_text.config(state=tk.DISABLED)

    def refresh_plugins(self):
        """Refresh the installed plugins list"""
        # Clear existing items
        for item in self.plugin_tree.get_children():
            self.plugin_tree.delete(item)

        # Get available plugins
        available_plugins = self.plugin_manager.list_available_plugins()

        for plugin_name in available_plugins:
            info = self.plugin_manager.get_plugin_info(plugin_name)
            if info:
                status = (
                    "Active"
                    if self.plugin_manager.is_plugin_active(plugin_name)
                    else "Inactive"
                )
                self.plugin_tree.insert(
                    "",
                    "end",
                    values=(
                        info.get("name", plugin_name),
                        info.get("version", "1.0.0"),
                        status,
                        info.get("description", "No description"),
                    ),
                )

    def load_available_plugins(self):
        """Load available plugins from repository"""
        # Clear existing items
        for item in self.available_tree.get_children():
            self.available_tree.delete(item)

        # Sample available plugins
        available_plugins = [
            (
                "Git Integration",
                "2.0.0",
                "DevTools Inc",
                "Git version control integration",
            ),
            (
                "AI Code Assistant",
                "1.3.1",
                "AI Labs",
                "AI-powered code suggestions and completion",
            ),
            (
                "Performance Profiler",
                "1.1.0",
                "SpeedTools",
                "Code performance analysis and optimization",
            ),
            (
                "Unit Test Generator",
                "0.8.2",
                "TestCorp",
                "Automatic unit test generation",
            ),
            (
                "Documentation Builder",
                "1.4.0",
                "DocMaker",
                "Generate documentation from code comments",
            ),
        ]

        for plugin in available_plugins:
            self.available_tree.insert("", "end", values=plugin)

    def on_plugin_select(self, event):
        """Handle plugin selection"""
        selection = self.plugin_tree.selection()
        if selection:
            item = self.plugin_tree.item(selection[0])
            plugin_name = item["values"][0]

            # Find the actual plugin name from the display name
            for name in self.plugin_manager.list_available_plugins():
                info = self.plugin_manager.get_plugin_info(name)
                if info and info.get("name") == plugin_name:
                    plugin_info = f"""Plugin: {info.get('name', 'Unknown')}
Version: {info.get('version', '1.0.0')}
Author: {info.get('author', 'Unknown')}
Status: {'Active' if self.plugin_manager.is_plugin_active(name) else 'Inactive'}

Description:
{info.get('description', 'No description available.')}"""

                    self.details_text.delete("1.0", tk.END)
                    self.details_text.insert("1.0", plugin_info)
                    break

    def enable_plugin(self):
        """Enable selected plugin"""
        selection = self.plugin_tree.selection()
        if selection:
            item = self.plugin_tree.item(selection[0])
            plugin_display_name = item["values"][0]

            # Find actual plugin name
            for name in self.plugin_manager.list_available_plugins():
                info = self.plugin_manager.get_plugin_info(name)
                if info and info.get("name") == plugin_display_name:
                    if self.plugin_manager.activate_plugin(name):
                        messagebox.showinfo(
                            "Plugin Enabled",
                            f"Plugin '{plugin_display_name}' has been enabled",
                        )
                        self.refresh_plugins()
                    else:
                        messagebox.showerror(
                            "Error", f"Failed to enable plugin '{plugin_display_name}'"
                        )
                    break

    def disable_plugin(self):
        """Disable selected plugin"""
        selection = self.plugin_tree.selection()
        if selection:
            item = self.plugin_tree.item(selection[0])
            plugin_display_name = item["values"][0]

            # Find actual plugin name
            for name in self.plugin_manager.list_available_plugins():
                info = self.plugin_manager.get_plugin_info(name)
                if info and info.get("name") == plugin_display_name:
                    if self.plugin_manager.deactivate_plugin(name):
                        messagebox.showinfo(
                            "Plugin Disabled",
                            f"Plugin '{plugin_display_name}' has been disabled",
                        )
                        self.refresh_plugins()
                    else:
                        messagebox.showerror(
                            "Error", f"Failed to disable plugin '{plugin_display_name}'"
                        )
                    break

    def uninstall_plugin(self):
        """Uninstall selected plugin"""
        selection = self.plugin_tree.selection()
        if selection:
            item = self.plugin_tree.item(selection[0])
            plugin_display_name = item["values"][0]

            if messagebox.askyesno(
                "Uninstall Plugin",
                f"Are you sure you want to uninstall '{plugin_display_name}'?",
            ):
                # Find actual plugin name
                for name in self.plugin_manager.list_available_plugins():
                    info = self.plugin_manager.get_plugin_info(name)
                    if info and info.get("name") == plugin_display_name:
                        if self.plugin_manager.unload_plugin(name):
                            messagebox.showinfo(
                                "Plugin Uninstalled",
                                f"Plugin '{plugin_display_name}' has been uninstalled",
                            )
                            self.refresh_plugins()
                        else:
                            messagebox.showerror(
                                "Error",
                                f"Failed to uninstall plugin '{plugin_display_name}'",
                            )
                        break

    def install_plugin(self):
        """Install selected plugin from available list"""
        selection = self.available_tree.selection()
        if selection:
            item = self.available_tree.item(selection[0])
            plugin_name = item["values"][0]
            if messagebox.askyesno(
                "Install Plugin", f"Install plugin '{plugin_name}'?"
            ):
                messagebox.showinfo(
                    "Plugin Installed",
                    f"Plugin '{plugin_name}' has been installed successfully!",
                )
                self.refresh_plugins()

    def close(self):
        """Close the dialog"""
        if self.window:
            self.window.destroy()
            self.window = None
