#!/usr/bin/env python3
"""
Time_Warp Tool Manager - Enhanced plugin system specifically for tools
Extends the base plugin system with tool-specific functionality
"""

import os
import json
import importlib.util
import sys
from typing import Dict, List, Optional, Any
import tkinter as tk
from tkinter import ttk, messagebox

# Import base plugin system
from plugins import PluginManager, TimeWarpPlugin
from ..core.framework import Time_WarpFramework, ToolPlugin


class ToolManager(PluginManager):
    """Enhanced plugin manager specifically for tool plugins"""

    def __init__(self, ide_instance, framework: Time_WarpFramework):
        # Initialize base plugin manager but override plugins directory
        self.ide = ide_instance
        self.framework = framework
        self.tools_dir = os.path.join(os.path.dirname(__file__), "plugins")
        self.loaded_tools: Dict[str, ToolPlugin] = {}
        self.active_tools: Dict[str, ToolPlugin] = {}
        self.tool_manifests: Dict[str, Dict] = {}

        # Ensure tools directory exists
        if not os.path.exists(self.tools_dir):
            os.makedirs(self.tools_dir)

        print(f"🔧 ToolManager initialized with directory: {self.tools_dir}")

    def scan_tools(self) -> List[str]:
        """Scan tools directory for available tool plugins"""
        available_tools = []

        if not os.path.exists(self.tools_dir):
            return available_tools

        for item in os.listdir(self.tools_dir):
            tool_path = os.path.join(self.tools_dir, item)

            if os.path.isdir(tool_path):
                manifest_path = os.path.join(tool_path, "manifest.json")
                plugin_file = os.path.join(tool_path, "plugin.py")

                if os.path.exists(manifest_path) and os.path.exists(plugin_file):
                    available_tools.append(item)

        return available_tools

    def load_tool_manifest(self, tool_name: str) -> Optional[Dict]:
        """Load tool manifest file"""
        manifest_path = os.path.join(self.tools_dir, tool_name, "manifest.json")

        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
                self.tool_manifests[tool_name] = manifest
                return manifest
        except Exception as e:
            print(f"Error loading manifest for {tool_name}: {e}")
            return None

    def load_tool(self, tool_name: str) -> bool:
        """Load a tool plugin from the tools directory"""
        if tool_name in self.loaded_tools:
            return True

        tool_path = os.path.join(self.tools_dir, tool_name)
        plugin_file = os.path.join(tool_path, "plugin.py")

        if not os.path.exists(plugin_file):
            print(f"Tool plugin file not found: {plugin_file}")
            return False

        # Load manifest
        manifest = self.load_tool_manifest(tool_name)
        if not manifest:
            return False

        try:
            # Load the tool plugin module
            spec = importlib.util.spec_from_file_location(
                f"tool_{tool_name}", plugin_file
            )
            if spec is None or spec.loader is None:
                print(f"Could not load tool plugin spec for {tool_name}")
                return False

            plugin_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin_module)

            # Create tool plugin instance
            if hasattr(plugin_module, "TimeWarpPlugin"):
                # Create instance with framework
                tool_instance = plugin_module.Time_WarpPlugin(self.ide, self.framework)

                # Verify it's a ToolPlugin
                if not isinstance(tool_instance, ToolPlugin):
                    print(f"Tool {tool_name} is not a ToolPlugin instance")
                    return False

                # Set tool info from manifest
                tool_instance.name = manifest.get("name", tool_name)
                tool_instance.version = manifest.get("version", "1.0.0")
                tool_instance.author = manifest.get("author", "Unknown")
                tool_instance.description = manifest.get("description", "")
                tool_instance.category = manifest.get("category", "general")

                # Register with framework
                if self.framework.register_tool(tool_instance):
                    self.loaded_tools[tool_name] = tool_instance
                    print(f"✅ Tool loaded: {tool_name}")
                    return True
                else:
                    print(f"Failed to register tool with framework: {tool_name}")
                    return False
            else:
                print(f"Tool {tool_name} does not contain a TimeWarpPlugin class")
                return False

        except Exception as e:
            print(f"Error loading tool {tool_name}: {e}")
            return False

    def activate_tool(self, tool_name: str) -> bool:
        """Activate a loaded tool"""
        if tool_name not in self.loaded_tools:
            if not self.load_tool(tool_name):
                return False

        return self.framework.activate_tool(self.loaded_tools[tool_name].name)

    def deactivate_tool(self, tool_name: str) -> bool:
        """Deactivate an active tool"""
        if tool_name in self.loaded_tools:
            return self.framework.deactivate_tool(self.loaded_tools[tool_name].name)
        return True

    def unload_tool(self, tool_name: str) -> bool:
        """Unload a tool completely"""
        if tool_name in self.loaded_tools:
            tool_instance = self.loaded_tools[tool_name]
            framework_name = tool_instance.name

            # Unregister from framework
            if self.framework.unregister_tool(framework_name):
                del self.loaded_tools[tool_name]

                if tool_name in self.tool_manifests:
                    del self.tool_manifests[tool_name]

                print(f"❌ Tool unloaded: {tool_name}")
                return True
        return False

    def show_tool(self, tool_name: str) -> bool:
        """Show a tool's dialog/window"""
        if tool_name in self.loaded_tools:
            framework_name = self.loaded_tools[tool_name].name
            return self.framework.show_tool(framework_name)
        return False

    def get_tool_info(self, tool_name: str) -> Optional[Dict]:
        """Get information about a tool"""
        if tool_name in self.loaded_tools:
            return self.loaded_tools[tool_name].get_info()
        elif tool_name in self.tool_manifests:
            return self.tool_manifests[tool_name]
        else:
            manifest = self.load_tool_manifest(tool_name)
            return manifest

    def list_available_tools(self) -> List[str]:
        """List all available tools"""
        return self.scan_tools()

    def list_loaded_tools(self) -> List[str]:
        """List all loaded tools"""
        return list(self.loaded_tools.keys())

    def list_active_tools(self) -> List[str]:
        """List all active tools"""
        return [name for name, tool in self.loaded_tools.items() if tool.is_active()]

    def list_tools_by_category(self, category: str) -> List[str]:
        """List tools in a specific category"""
        return [
            name
            for name, tool in self.loaded_tools.items()
            if tool.category == category
        ]

    def is_tool_active(self, tool_name: str) -> bool:
        """Check if a tool is active"""
        if tool_name in self.loaded_tools:
            return self.loaded_tools[tool_name].is_active()
        return False

    def is_tool_loaded(self, tool_name: str) -> bool:
        """Check if a tool is loaded"""
        return tool_name in self.loaded_tools

    def auto_load_tools(self) -> None:
        """Automatically load all available tools"""
        available_tools = self.scan_tools()

        for tool_name in available_tools:
            if not self.is_tool_loaded(tool_name):
                print(f"🔄 Auto-loading tool: {tool_name}")
                self.load_tool(tool_name)

    def get_categories(self) -> List[str]:
        """Get all tool categories"""
        categories = set()
        for tool in self.loaded_tools.values():
            categories.add(tool.category)
        return list(categories)


class ToolManagerDialog:
    """Enhanced tool management interface"""

    def __init__(self, ide_instance, tool_manager: ToolManager):
        self.ide = ide_instance
        self.tool_manager = tool_manager
        self.window = None

    def show(self):
        """Show the tool management dialog"""
        if self.window:
            self.window.lift()
            return

        self.window = tk.Toplevel(self.ide.root)
        self.window.title("🛠️ Tool Manager")
        self.window.geometry("900x650")
        self.window.transient(self.ide.root)

        # Create main layout
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(
            header_frame, text="🛠️ Time_Warp Tool Manager", font=("Arial", 16, "bold")
        ).pack(side=tk.LEFT)

        header_buttons = ttk.Frame(header_frame)
        header_buttons.pack(side=tk.RIGHT)

        ttk.Button(header_buttons, text="🔄 Refresh", command=self.refresh_tools).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(
            header_buttons, text="⚡ Auto-Load All", command=self.auto_load_all_tools
        ).pack(side=tk.LEFT, padx=2)

        # Create notebook for different tool sections
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Installed Tools Tab
        installed_frame = ttk.Frame(notebook)
        notebook.add(installed_frame, text="🔧 Installed Tools")
        self.setup_installed_tools_tab(installed_frame)

        # Categories Tab
        categories_frame = ttk.Frame(notebook)
        notebook.add(categories_frame, text="📂 Categories")
        self.setup_categories_tab(categories_frame)

        # Tool Development Tab
        dev_frame = ttk.Frame(notebook)
        notebook.add(dev_frame, text="⚙️ Development")
        self.setup_development_tab(dev_frame)

        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self.close)

        # Initialize
        self.refresh_tools()

    def setup_installed_tools_tab(self, parent):
        """Setup the installed tools tab"""
        # Tool list
        list_frame = ttk.LabelFrame(parent, text="Available Tools")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Treeview for tools
        columns = ("Name", "Version", "Category", "Status", "Description")
        self.tools_tree = ttk.Treeview(
            list_frame, columns=columns, show="headings", height=15
        )

        column_widths = {
            "Name": 150,
            "Version": 80,
            "Category": 100,
            "Status": 80,
            "Description": 300,
        }
        for col in columns:
            self.tools_tree.heading(col, text=col)
            self.tools_tree.column(col, width=column_widths.get(col, 150))

        self.tools_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        tree_scroll = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.tools_tree.yview
        )
        self.tools_tree.config(yscrollcommand=tree_scroll.set)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Tool details
        details_frame = ttk.LabelFrame(parent, text="Tool Details")
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

        ttk.Button(button_frame, text="🔧 Load Tool", command=self.load_tool).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="✅ Activate", command=self.activate_tool).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(
            button_frame, text="❌ Deactivate", command=self.deactivate_tool
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🚀 Show Tool", command=self.show_tool).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="🗑️ Unload", command=self.unload_tool).pack(
            side=tk.LEFT, padx=5
        )

        # Bind selection event
        self.tools_tree.bind("<<TreeviewSelect>>", self.on_tool_select)

    def setup_categories_tab(self, parent):
        """Setup the categories tab"""
        # Categories frame
        cat_frame = ttk.LabelFrame(parent, text="Tool Categories")
        cat_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Category list
        self.category_listbox = tk.Listbox(cat_frame, font=("Arial", 11))
        self.category_listbox.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        cat_scroll = ttk.Scrollbar(
            cat_frame, orient=tk.VERTICAL, command=self.category_listbox.yview
        )
        self.category_listbox.config(yscrollcommand=cat_scroll.set)
        cat_scroll.pack(side=tk.LEFT, fill=tk.Y, pady=5)

        # Tools in category
        tools_in_cat_frame = ttk.Frame(cat_frame)
        tools_in_cat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(
            tools_in_cat_frame, text="Tools in Category:", font=("Arial", 12, "bold")
        ).pack(anchor="w")

        self.category_tools_tree = ttk.Treeview(
            tools_in_cat_frame, columns=("Name", "Status"), show="headings", height=12
        )

        self.category_tools_tree.heading("Name", text="Tool Name")
        self.category_tools_tree.heading("Status", text="Status")
        self.category_tools_tree.column("Name", width=200)
        self.category_tools_tree.column("Status", width=100)

        self.category_tools_tree.pack(fill=tk.BOTH, expand=True)

        # Bind category selection
        self.category_listbox.bind("<<ListboxSelect>>", self.on_category_select)

    def setup_development_tab(self, parent):
        """Setup the development tab"""
        ttk.Label(
            parent, text="Tool Development Guide", font=("Arial", 14, "bold")
        ).pack(pady=10)

        guide_text = tk.Text(parent, height=25, font=("Arial", 10), wrap=tk.WORD)
        guide_scroll = ttk.Scrollbar(
            parent, orient=tk.VERTICAL, command=guide_text.yview
        )
        guide_text.config(yscrollcommand=guide_scroll.set)
        guide_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        guide_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        tool_guide = """🛠️ Time_Warp TOOL DEVELOPMENT GUIDE

📋 Tool Plugin Structure:
A Time_Warp tool plugin extends the ToolPlugin base class and provides professional functionality.

Required Files:
• plugin.py - Main tool implementation (must contain TimeWarpPlugin class)
• manifest.json - Tool metadata and configuration
• README.md - Documentation and usage guide

📄 Sample manifest.json:
{
  "name": "My Tool",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "Professional tool description",
  "category": "debugging",
  "entry_point": "plugin.py",
  "api_version": "1.0",
  "permissions": ["interpreter", "filesystem", "ui"],
  "dependencies": [],
  "keywords": ["tool", "functionality"]
}

🐍 Sample plugin.py:
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from ..core.framework import ToolPlugin
import tkinter as tk
from tkinter import ttk

class MyToolPlugin(ToolPlugin):
    def __init__(self, ide_instance, framework):
        super().__init__(ide_instance, framework)
        self.name = "My Tool"
        self.version = "1.0.0"
        self.category = "general"
    
    def initialize(self) -> bool:
        # Initialize tool resources
        return True
    
    def activate(self) -> bool:
        # Add menu items, subscribe to events
        self.add_menu_item("Tools", "🔧 My Tool", self.show_tool_dialog)
        return True
    
    def deactivate(self) -> bool:
        # Clean up when deactivated
        return True
    
    def create_ui(self, parent_widget) -> tk.Widget:
        # Create tool's main UI
        main_frame = ttk.Frame(parent_widget)
        ttk.Label(main_frame, text="My Tool Interface").pack(pady=20)
        return main_frame

# Required: Plugin entry point
TimeWarpPlugin = MyToolPlugin

🔧 Tool Categories:
• debugging - Debugging and analysis tools
• hardware - Hardware interface tools  
• iot - IoT and device management tools
• visualization - Data visualization tools
• learning - Educational and tutorial tools
• utilities - General utility tools
• development - Development assistance tools

🚀 Framework Integration:
• Event System: Subscribe to interpreter_ready, code_executed, execution_error
• Component Registry: Register/retrieve shared components
• Menu Integration: Add custom menu items and toolbar buttons
• UI Framework: Professional tabbed interfaces with error handling

💡 Best Practices:
• Follow the ToolPlugin lifecycle (initialize → activate → deactivate → destroy)
• Use framework event system for loose coupling
• Implement comprehensive error handling
• Provide professional UI with proper layouts
• Use meaningful categories and descriptions
• Handle resource cleanup properly
• Subscribe to relevant framework events
• Add comprehensive logging and status updates

📊 Professional Features:
• Multi-tab interfaces for complex functionality
• Real-time data monitoring and updates
• Export/import capabilities for tool data
• Configuration persistence
• Professional error handling and user feedback
• Integration with Time_Warp interpreter system
• Comprehensive help and documentation"""

        guide_text.insert("1.0", tool_guide)
        guide_text.config(state=tk.DISABLED)

    def refresh_tools(self):
        """Refresh the tools list"""
        # Clear existing items
        for item in self.tools_tree.get_children():
            self.tools_tree.delete(item)

        # Get available tools
        available_tools = self.tool_manager.list_available_tools()

        for tool_name in available_tools:
            info = self.tool_manager.get_tool_info(tool_name)
            if info:
                is_loaded = self.tool_manager.is_tool_loaded(tool_name)
                is_active = (
                    self.tool_manager.is_tool_active(tool_name) if is_loaded else False
                )

                if is_active:
                    status = "Active"
                elif is_loaded:
                    status = "Loaded"
                else:
                    status = "Available"

                self.tools_tree.insert(
                    "",
                    "end",
                    values=(
                        info.get("name", tool_name),
                        info.get("version", "1.0.0"),
                        info.get("category", "general"),
                        status,
                        info.get("description", "No description"),
                    ),
                )

        # Refresh categories
        self.refresh_categories()

    def refresh_categories(self):
        """Refresh the categories list"""
        self.category_listbox.delete(0, tk.END)

        categories = self.tool_manager.get_categories()
        for category in sorted(categories):
            self.category_listbox.insert(tk.END, category.title())

    def on_tool_select(self, event):
        """Handle tool selection"""
        selection = self.tools_tree.selection()
        if selection:
            item = self.tools_tree.item(selection[0])
            tool_display_name = item["values"][0]

            # Find the actual tool name from the display name
            for tool_name in self.tool_manager.list_available_tools():
                info = self.tool_manager.get_tool_info(tool_name)
                if info and info.get("name") == tool_display_name:
                    tool_info = f"""Tool: {info.get('name', 'Unknown')}
Version: {info.get('version', '1.0.0')}
Author: {info.get('author', 'Unknown')}
Category: {info.get('category', 'general')}
Status: {'Active' if self.tool_manager.is_tool_active(tool_name) else 'Loaded' if self.tool_manager.is_tool_loaded(tool_name) else 'Available'}

Description:
{info.get('description', 'No description available.')}

Keywords: {', '.join(info.get('keywords', []))}
Dependencies: {', '.join(info.get('dependencies', []))}"""

                    self.details_text.delete("1.0", tk.END)
                    self.details_text.insert("1.0", tool_info)
                    break

    def on_category_select(self, event):
        """Handle category selection"""
        selection = self.category_listbox.curselection()
        if selection:
            category = self.category_listbox.get(selection[0]).lower()

            # Clear category tools tree
            for item in self.category_tools_tree.get_children():
                self.category_tools_tree.delete(item)

            # Get tools in category
            tools_in_category = self.tool_manager.list_tools_by_category(category)

            for tool_name in tools_in_category:
                tool = self.tool_manager.loaded_tools.get(tool_name)
                if tool:
                    status = "Active" if tool.is_active() else "Loaded"
                    self.category_tools_tree.insert(
                        "", "end", values=(tool.name, status)
                    )

    def load_tool(self):
        """Load selected tool"""
        selection = self.tools_tree.selection()
        if selection:
            item = self.tools_tree.item(selection[0])
            tool_display_name = item["values"][0]

            # Find actual tool name
            for tool_name in self.tool_manager.list_available_tools():
                info = self.tool_manager.get_tool_info(tool_name)
                if info and info.get("name") == tool_display_name:
                    if self.tool_manager.load_tool(tool_name):
                        messagebox.showinfo(
                            "Tool Loaded",
                            f"Tool '{tool_display_name}' loaded successfully",
                        )
                        self.refresh_tools()
                    else:
                        messagebox.showerror(
                            "Error", f"Failed to load tool '{tool_display_name}'"
                        )
                    break

    def activate_tool(self):
        """Activate selected tool"""
        selection = self.tools_tree.selection()
        if selection:
            item = self.tools_tree.item(selection[0])
            tool_display_name = item["values"][0]

            # Find actual tool name
            for tool_name in self.tool_manager.list_available_tools():
                info = self.tool_manager.get_tool_info(tool_name)
                if info and info.get("name") == tool_display_name:
                    if self.tool_manager.activate_tool(tool_name):
                        messagebox.showinfo(
                            "Tool Activated",
                            f"Tool '{tool_display_name}' activated successfully",
                        )
                        self.refresh_tools()
                    else:
                        messagebox.showerror(
                            "Error", f"Failed to activate tool '{tool_display_name}'"
                        )
                    break

    def deactivate_tool(self):
        """Deactivate selected tool"""
        selection = self.tools_tree.selection()
        if selection:
            item = self.tools_tree.item(selection[0])
            tool_display_name = item["values"][0]

            # Find actual tool name
            for tool_name in self.tool_manager.list_available_tools():
                info = self.tool_manager.get_tool_info(tool_name)
                if info and info.get("name") == tool_display_name:
                    if self.tool_manager.deactivate_tool(tool_name):
                        messagebox.showinfo(
                            "Tool Deactivated",
                            f"Tool '{tool_display_name}' deactivated successfully",
                        )
                        self.refresh_tools()
                    else:
                        messagebox.showerror(
                            "Error", f"Failed to deactivate tool '{tool_display_name}'"
                        )
                    break

    def show_tool(self):
        """Show selected tool"""
        selection = self.tools_tree.selection()
        if selection:
            item = self.tools_tree.item(selection[0])
            tool_display_name = item["values"][0]

            # Find actual tool name
            for tool_name in self.tool_manager.list_available_tools():
                info = self.tool_manager.get_tool_info(tool_name)
                if info and info.get("name") == tool_display_name:
                    if self.tool_manager.show_tool(tool_name):
                        self.close()  # Close tool manager when showing tool
                    else:
                        messagebox.showerror(
                            "Error", f"Failed to show tool '{tool_display_name}'"
                        )
                    break

    def unload_tool(self):
        """Unload selected tool"""
        selection = self.tools_tree.selection()
        if selection:
            item = self.tools_tree.item(selection[0])
            tool_display_name = item["values"][0]

            if messagebox.askyesno(
                "Unload Tool", f"Are you sure you want to unload '{tool_display_name}'?"
            ):
                # Find actual tool name
                for tool_name in self.tool_manager.list_available_tools():
                    info = self.tool_manager.get_tool_info(tool_name)
                    if info and info.get("name") == tool_display_name:
                        if self.tool_manager.unload_tool(tool_name):
                            messagebox.showinfo(
                                "Tool Unloaded",
                                f"Tool '{tool_display_name}' unloaded successfully",
                            )
                            self.refresh_tools()
                        else:
                            messagebox.showerror(
                                "Error", f"Failed to unload tool '{tool_display_name}'"
                            )
                        break

    def auto_load_all_tools(self):
        """Auto-load all available tools"""
        if messagebox.askyesno("Auto-Load Tools", "Load all available tools?"):
            self.tool_manager.auto_load_tools()
            self.refresh_tools()
            messagebox.showinfo(
                "Auto-Load Complete", "All available tools have been loaded"
            )

    def close(self):
        """Close the dialog"""
        if self.window:
            self.window.destroy()
            self.window = None
