#!/usr/bin/env python3
"""
Time_Warp Core Framework - Base architecture for modular tool system
Provides event management, plugin interfaces, and standardized component registration
"""

import sys
import os
import threading
import queue
from typing import Dict, List, Optional, Any, Callable
from abc import ABC, abstractmethod
from datetime import datetime
import json
import tkinter as tk
from tkinter import ttk


class EventManager:
    """Centralized event management system for framework components"""

    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
        self._lock = threading.RLock()

    def subscribe(self, event_name: str, callback: Callable) -> None:
        """Subscribe to an event with a callback function"""
        with self._lock:
            if event_name not in self._listeners:
                self._listeners[event_name] = []
            self._listeners[event_name].append(callback)

    def unsubscribe(self, event_name: str, callback: Callable) -> None:
        """Unsubscribe from an event"""
        with self._lock:
            if event_name in self._listeners:
                try:
                    self._listeners[event_name].remove(callback)
                except ValueError:
                    pass

    def emit(self, event_name: str, *args, **kwargs) -> None:
        """Emit an event to all subscribers"""
        with self._lock:
            if event_name in self._listeners:
                for callback in self._listeners[event_name].copy():
                    try:
                        callback(*args, **kwargs)
                    except Exception as e:
                        print(f"Error in event callback for {event_name}: {e}")

    def clear_event(self, event_name: str) -> None:
        """Clear all listeners for a specific event"""
        with self._lock:
            if event_name in self._listeners:
                del self._listeners[event_name]

    def clear_all(self) -> None:
        """Clear all event listeners"""
        with self._lock:
            self._listeners.clear()


class ComponentRegistry:
    """Registry for framework components and tools"""

    def __init__(self):
        self._components: Dict[str, Any] = {}
        self._lock = threading.RLock()

    def register(self, name: str, component: Any) -> None:
        """Register a component"""
        with self._lock:
            self._components[name] = component

    def unregister(self, name: str) -> None:
        """Unregister a component"""
        with self._lock:
            if name in self._components:
                del self._components[name]

    def get(self, name: str) -> Optional[Any]:
        """Get a registered component"""
        with self._lock:
            return self._components.get(name)

    def list_components(self) -> List[str]:
        """List all registered component names"""
        with self._lock:
            return list(self._components.keys())

    def has_component(self, name: str) -> bool:
        """Check if a component is registered"""
        with self._lock:
            return name in self._components


class ToolPlugin(ABC):
    """Base class for Time_Warp tool plugins with standardized lifecycle and UI integration"""

    def __init__(self, ide_instance, framework):
        self.ide = ide_instance
        self.framework = framework
        self.event_manager = framework.event_manager if framework else None
        self.registry = framework.registry if framework else None

        # Tool metadata
        self.name = "Base Tool"
        self.version = "1.0.0"
        self.author = "Time_Warp IDE"
        self.description = "Base tool plugin"
        self.category = "general"

        # Tool state
        self._active = False
        self._initialized = False
        self._ui_elements = {}
        self._menu_items = []
        self._toolbar_items = []

        # Event callbacks
        self._event_callbacks = {}

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the tool - called once during plugin loading"""
        pass

    @abstractmethod
    def activate(self) -> bool:
        """Activate the tool - called when tool is enabled"""
        pass

    @abstractmethod
    def deactivate(self) -> bool:
        """Deactivate the tool - called when tool is disabled"""
        pass

    @abstractmethod
    def create_ui(self, parent_widget) -> tk.Widget:
        """Create the tool's main UI widget"""
        pass

    def destroy(self) -> bool:
        """Destroy the tool - called during plugin unloading"""
        try:
            # Clean up UI elements
            for element in self._ui_elements.values():
                if hasattr(element, "destroy"):
                    element.destroy()
            self._ui_elements.clear()

            # Unsubscribe from events
            for event_name, callback in self._event_callbacks.items():
                self.event_manager.unsubscribe(event_name, callback)
            self._event_callbacks.clear()

            # Remove menu items
            self._cleanup_menu_items()

            # Remove toolbar items
            self._cleanup_toolbar_items()

            return True
        except Exception as e:
            print(f"Error destroying tool {self.name}: {e}")
            return False

    def get_info(self) -> Dict[str, Any]:
        """Get tool information"""
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "category": self.category,
            "active": self._active,
            "initialized": self._initialized,
        }

    def is_active(self) -> bool:
        """Check if tool is active"""
        return self._active

    def is_initialized(self) -> bool:
        """Check if tool is initialized"""
        return self._initialized

    def add_menu_item(
        self, menu_path: str, label: str, command: Callable, accelerator: str = None
    ) -> None:
        """Add a menu item for this tool"""
        try:
            menu_item = {
                "path": menu_path,
                "label": label,
                "command": command,
                "accelerator": accelerator,
            }
            self._menu_items.append(menu_item)

            # Add to IDE menu system
            if hasattr(self.ide, "add_tool_menu_item"):
                self.ide.add_tool_menu_item(menu_path, label, command, accelerator)

        except Exception as e:
            print(f"Error adding menu item for {self.name}: {e}")

    def add_toolbar_item(
        self, label: str, command: Callable, icon: str = None, tooltip: str = None
    ) -> None:
        """Add a toolbar item for this tool"""
        try:
            toolbar_item = {
                "label": label,
                "command": command,
                "icon": icon,
                "tooltip": tooltip,
            }
            self._toolbar_items.append(toolbar_item)

            # Add to IDE toolbar
            if hasattr(self.ide, "add_tool_toolbar_item"):
                self.ide.add_tool_toolbar_item(label, command, icon, tooltip)

        except Exception as e:
            print(f"Error adding toolbar item for {self.name}: {e}")

    def subscribe_event(self, event_name: str, callback: Callable) -> None:
        """Subscribe to framework events"""
        if self.event_manager:
            self.event_manager.subscribe(event_name, callback)
        self._event_callbacks[event_name] = callback

    def emit_event(self, event_name: str, *args, **kwargs) -> None:
        """Emit a framework event"""
        if self.event_manager:
            self.event_manager.emit(event_name, *args, **kwargs)

    def register_component(self, name: str, component: Any) -> None:
        """Register a component with the framework"""
        self.registry.register(f"{self.name}_{name}", component)

    def get_component(self, name: str) -> Optional[Any]:
        """Get a registered component"""
        return self.registry.get(name)

    def show_tool_dialog(self) -> None:
        """Show the tool's main dialog/window"""
        if hasattr(self, "_tool_window") and self._tool_window:
            self._tool_window.lift()
            return

        self._tool_window = tk.Toplevel(self.ide.root)
        self._tool_window.title(f"🛠️ {self.name}")
        self._tool_window.geometry("1000x700")
        self._tool_window.transient(self.ide.root)

        # Create tool UI
        main_widget = self.create_ui(self._tool_window)
        if main_widget:
            main_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Handle window closing
        def on_close():
            self._tool_window.destroy()
            self._tool_window = None

        self._tool_window.protocol("WM_DELETE_WINDOW", on_close)

    def _cleanup_menu_items(self) -> None:
        """Clean up menu items"""
        for item in self._menu_items:
            if hasattr(self.ide, "remove_tool_menu_item"):
                self.ide.remove_tool_menu_item(item["path"], item["label"])
        self._menu_items.clear()

    def _cleanup_toolbar_items(self) -> None:
        """Clean up toolbar items"""
        for item in self._toolbar_items:
            if hasattr(self.ide, "remove_tool_toolbar_item"):
                self.ide.remove_tool_toolbar_item(item["label"])
        self._toolbar_items.clear()


class Time_WarpFramework:
    """Core framework for Time_Warp IDE - manages tools, events, and components"""

    def __init__(self, ide_instance):
        self.ide = ide_instance
        self.event_manager = EventManager()
        self.registry = ComponentRegistry()

        # Tool management
        self._tools: Dict[str, ToolPlugin] = {}
        self._tool_categories: Dict[str, List[str]] = {}

        # Configuration
        self._config = {}
        self._config_file = os.path.expanduser("~/.time_warp/framework_config.json")

        # Initialize
        self._ensure_config_dir()
        self._load_config()

        print("🚀 Time_Warp Framework initialized")

    def register_tool(self, tool: ToolPlugin) -> bool:
        """Register a tool plugin"""
        try:
            tool_name = tool.name

            if tool_name in self._tools:
                print(f"Tool {tool_name} already registered")
                return False

            # Initialize the tool
            if not tool.initialize():
                print(f"Failed to initialize tool {tool_name}")
                return False

            tool._initialized = True
            self._tools[tool_name] = tool

            # Add to category
            category = tool.category
            if category not in self._tool_categories:
                self._tool_categories[category] = []
            self._tool_categories[category].append(tool_name)

            # Register with component registry
            self.registry.register(f"tool_{tool_name}", tool)

            # Emit registration event
            self.event_manager.emit("tool_registered", tool_name, tool)

            print(f"✅ Tool registered: {tool_name}")
            return True

        except Exception as e:
            print(f"Error registering tool {tool.name}: {e}")
            return False

    def unregister_tool(self, tool_name: str) -> bool:
        """Unregister a tool plugin"""
        try:
            if tool_name not in self._tools:
                return True

            tool = self._tools[tool_name]

            # Deactivate if active
            if tool.is_active():
                self.deactivate_tool(tool_name)

            # Destroy the tool
            tool.destroy()

            # Remove from registry
            self.registry.unregister(f"tool_{tool_name}")

            # Remove from category
            category = tool.category
            if category in self._tool_categories:
                if tool_name in self._tool_categories[category]:
                    self._tool_categories[category].remove(tool_name)
                if not self._tool_categories[category]:
                    del self._tool_categories[category]

            # Remove from tools
            del self._tools[tool_name]

            # Emit unregistration event
            self.event_manager.emit("tool_unregistered", tool_name)

            print(f"❌ Tool unregistered: {tool_name}")
            return True

        except Exception as e:
            print(f"Error unregistering tool {tool_name}: {e}")
            return False

    def activate_tool(self, tool_name: str) -> bool:
        """Activate a tool"""
        try:
            if tool_name not in self._tools:
                print(f"Tool {tool_name} not found")
                return False

            tool = self._tools[tool_name]

            if tool.is_active():
                return True  # Already active

            if not tool.activate():
                print(f"Failed to activate tool {tool_name}")
                return False

            tool._active = True

            # Emit activation event
            self.event_manager.emit("tool_activated", tool_name, tool)

            print(f"🟢 Tool activated: {tool_name}")
            return True

        except Exception as e:
            print(f"Error activating tool {tool_name}: {e}")
            return False

    def deactivate_tool(self, tool_name: str) -> bool:
        """Deactivate a tool"""
        try:
            if tool_name not in self._tools:
                return True

            tool = self._tools[tool_name]

            if not tool.is_active():
                return True  # Already inactive

            if not tool.deactivate():
                print(f"Failed to deactivate tool {tool_name}")
                return False

            tool._active = False

            # Emit deactivation event
            self.event_manager.emit("tool_deactivated", tool_name, tool)

            print(f"🔴 Tool deactivated: {tool_name}")
            return True

        except Exception as e:
            print(f"Error deactivating tool {tool_name}: {e}")
            return False

    def get_tool(self, tool_name: str) -> Optional[ToolPlugin]:
        """Get a registered tool"""
        return self._tools.get(tool_name)

    def list_tools(self) -> List[str]:
        """List all registered tools"""
        return list(self._tools.keys())

    def list_active_tools(self) -> List[str]:
        """List all active tools"""
        return [name for name, tool in self._tools.items() if tool.is_active()]

    def list_tools_by_category(self, category: str) -> List[str]:
        """List tools in a specific category"""
        return self._tool_categories.get(category, [])

    def list_categories(self) -> List[str]:
        """List all tool categories"""
        return list(self._tool_categories.keys())

    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a tool"""
        tool = self.get_tool(tool_name)
        return tool.get_info() if tool else None

    def show_tool(self, tool_name: str) -> bool:
        """Show a tool's dialog/window"""
        try:
            tool = self.get_tool(tool_name)
            if not tool:
                print(f"Tool {tool_name} not found")
                return False

            # Activate if not active
            if not tool.is_active():
                if not self.activate_tool(tool_name):
                    return False

            # Show tool dialog
            tool.show_tool_dialog()
            return True

        except Exception as e:
            print(f"Error showing tool {tool_name}: {e}")
            return False

    def _ensure_config_dir(self) -> None:
        """Ensure configuration directory exists"""
        config_dir = os.path.dirname(self._config_file)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)

    def _load_config(self) -> None:
        """Load framework configuration"""
        try:
            if os.path.exists(self._config_file):
                with open(self._config_file, "r", encoding="utf-8") as f:
                    self._config = json.load(f)
            else:
                self._config = {
                    "active_tools": [],
                    "tool_settings": {},
                    "framework_version": "1.0.0",
                }
                self._save_config()
        except Exception as e:
            print(f"Error loading framework config: {e}")
            self._config = {}

    def _save_config(self) -> None:
        """Save framework configuration"""
        try:
            with open(self._config_file, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2)
        except Exception as e:
            print(f"Error saving framework config: {e}")

    def get_config(self, key: str, default=None):
        """Get configuration value"""
        return self._config.get(key, default)

    def set_config(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self._config[key] = value
        self._save_config()

    def shutdown(self) -> None:
        """Shutdown the framework"""
        print("🛑 Shutting down Time_Warp Framework...")

        # Deactivate all active tools
        for tool_name in self.list_active_tools():
            self.deactivate_tool(tool_name)

        # Unregister all tools
        for tool_name in self.list_tools():
            self.unregister_tool(tool_name)

        # Clear event manager
        self.event_manager.clear_all()

        # Clear registry
        self.registry._components.clear()

        print("✅ Time_Warp Framework shutdown complete")
