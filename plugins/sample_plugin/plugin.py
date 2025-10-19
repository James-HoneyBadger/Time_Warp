"""
Sample Time_Warp Plugin
Demonstrates the plugin system capabilities
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Add the parent directory to path to import the base plugin class
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


# Base plugin class
class BasePlugin:
    def __init__(self, ide_instance):
        self.ide = ide_instance
        self.name = "Base Plugin"
        self.version = "1.0.0"
        self.author = "Unknown"
        self.description = "Base plugin class"

    def activate(self):
        pass

    def deactivate(self):
        pass

    def get_info(self):
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
        }


class TimeWarpPlugin(BasePlugin):
    """Sample plugin implementation"""

    def __init__(self, ide_instance):
        super().__init__(ide_instance)
        self.name = "Sample Plugin"
        self.version = "1.0.0"
        self.author = "Time_Warp Developer"
        self.description = (
            "A sample plugin demonstrating Time_Warp plugin system capabilities"
        )
        self.menu_items = []

    def activate(self):
        """Activate the plugin - add menu items and functionality"""
        try:
            self.add_menu_items()
            if hasattr(self.ide, "status_label"):
                self.ide.status_label.config(text="Sample Plugin activated!")
            print(f"✅ {self.name} activated successfully")
        except Exception as e:
            print(f"❌ Error activating {self.name}: {e}")

    def deactivate(self):
        """Deactivate the plugin - remove menu items"""
        try:
            self.remove_menu_items()
            if hasattr(self.ide, "status_label"):
                self.ide.status_label.config(text="Sample Plugin deactivated")
            print(f"🔌 {self.name} deactivated")
        except Exception as e:
            print(f"❌ Error deactivating {self.name}: {e}")

    def add_menu_items(self):
        """Add plugin-specific menu items"""
        try:
            # Add to Tools menu if it exists
            if hasattr(self.ide, "menubar"):
                # Try to find the Tools menu
                tools_menu = None
                for i in range(self.ide.menubar.index("end") + 1):
                    try:
                        if self.ide.menubar.entryconfig(i, "label")[4][1] == "Tools":
                            tools_menu = self.ide.menubar.nametowidget(
                                self.ide.menubar.entryconfig(i, "menu")[4][1]
                            )
                            break
                    except:
                        continue

                if tools_menu:
                    # Add separator
                    tools_menu.add_separator()

                    # Add plugin menu items
                    tools_menu.add_command(
                        label="🔧 Sample Action", command=self.sample_action
                    )
                    tools_menu.add_command(
                        label="📝 Insert Template", command=self.insert_template
                    )
                    tools_menu.add_command(
                        label="ℹ️ Plugin Info", command=self.show_plugin_info
                    )

                    self.menu_items = [
                        "🔧 Sample Action",
                        "📝 Insert Template",
                        "ℹ️ Plugin Info",
                    ]

        except Exception as e:
            print(f"Error adding menu items: {e}")

    def remove_menu_items(self):
        """Remove plugin menu items"""
        try:
            if hasattr(self.ide, "menubar") and self.menu_items:
                # Find Tools menu and remove our items
                tools_menu = None
                for i in range(self.ide.menubar.index("end") + 1):
                    try:
                        if self.ide.menubar.entryconfig(i, "label")[4][1] == "Tools":
                            tools_menu = self.ide.menubar.nametowidget(
                                self.ide.menubar.entryconfig(i, "menu")[4][1]
                            )
                            break
                    except:
                        continue

                if tools_menu:
                    # Remove our menu items (simplified - in real implementation, track menu indices)
                    # For demo purposes, we'll just clear the reference
                    pass

                self.menu_items = []

        except Exception as e:
            print(f"Error removing menu items: {e}")

    def sample_action(self):
        """Sample plugin action"""
        messagebox.showinfo(
            "Sample Plugin",
            f"Hello from {self.name}!\n\n"
            f"This is a demonstration of the Time_Warp plugin system.\n"
            f"Version: {self.version}\n"
            f"Author: {self.author}",
        )

    def insert_template(self):
        """Insert a code template"""
        template = """T:Sample PILOT Program Template
T:Created by Sample Plugin
T:
A:What is your name?
*name
T:Hello, *name!
T:This template was inserted by a plugin.
E:
"""

        try:
            if hasattr(self.ide, "editor"):
                # Insert template at cursor position
                self.ide.editor.insert(tk.INSERT, template)
                messagebox.showinfo(
                    "Template Inserted", "PILOT program template has been inserted!"
                )
            else:
                messagebox.showwarning(
                    "No Editor", "No editor found to insert template"
                )
        except Exception as e:
            messagebox.showerror("Error", f"Could not insert template: {e}")

    def show_plugin_info(self):
        """Show detailed plugin information"""
        info = self.get_info()
        info_text = f"""Plugin Information:

Name: {info['name']}
Version: {info['version']}
Author: {info['author']}

Description:
{info['description']}

Features:
• Sample menu actions
• Code template insertion
• Plugin system demonstration
• Error handling examples

This plugin demonstrates how to:
- Add custom menu items
- Interact with the editor
- Handle activation/deactivation
- Provide user feedback
- Follow plugin best practices"""

        # Create info window
        info_window = tk.Toplevel(self.ide.root)
        info_window.title(f"{self.name} - Information")
        info_window.geometry("400x300")
        info_window.transient(self.ide.root)

        # Info text
        text_widget = tk.Text(info_window, wrap=tk.WORD, font=("Arial", 10))
        scrollbar = tk.Scrollbar(info_window, command=text_widget.yview)
        text_widget.config(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        text_widget.insert("1.0", info_text)
        text_widget.config(state=tk.DISABLED)

    def get_info(self):
        """Get detailed plugin information"""
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "features": [
                "Sample menu actions",
                "Code template insertion",
                "Plugin system demonstration",
                "Error handling examples",
            ],
            "permissions": ["editor", "filesystem", "menu"],
        }
