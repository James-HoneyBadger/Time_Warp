# Sample TimeWarp Plugin

A demonstration plugin for the TimeWarp IDE plugin system.

## Features

- **Sample Action**: Shows a greeting dialog demonstrating basic plugin functionality
- **Insert Template**: Inserts a PILOT program template into the editor
- **Plugin Info**: Displays detailed information about the plugin
- **Menu Integration**: Adds items to the IDE's Tools menu

## Installation

This plugin comes pre-installed with TimeWarp as a demonstration of the plugin system.

## Usage

1. Open the Plugin Manager from Tools → Plugin Manager
2. Find "Sample Plugin" in the Installed tab
3. Click "Enable" to activate the plugin
4. New menu items will appear in the Tools menu:
   - 🔧 Sample Action
   - 📝 Insert Template
   - ℹ️ Plugin Info

## Development Notes

This plugin demonstrates:

- Proper plugin class inheritance
- Menu item management
- Editor interaction
- Error handling
- User feedback
- Plugin information display

Use this as a reference when creating your own TimeWarp plugins.

## Requirements

- TimeWarp IDE v2.0+
- Python 3.7+
- tkinter (included with Python)

## License

This plugin is distributed under the same license as TimeWarp IDE.