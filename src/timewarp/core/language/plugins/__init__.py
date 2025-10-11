"""
Time_Warp IDE Plugin System
Extensible architecture for adding new features and integrations
"""

from .manager import PluginManager
from .base import Plugin, PluginInterface, PluginType
from .loader import PluginLoader
from .registry import PluginRegistry

__all__ = [
    "PluginManager",
    "Plugin",
    "PluginInterface",
    "PluginType",
    "PluginLoader",
    "PluginRegistry",
]
