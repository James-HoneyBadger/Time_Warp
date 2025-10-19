# Sample Time_Warp Plugin

A demonstration plugin for the Time_Warp IDE plugin system.

## Features

- **Sample Action**: Shows a greeting dialog demonstrating basic plugin functionality
- **Insert Template**: Inserts a PILOT program template into the editor
- **Plugin Info**: Displays detailed information about the plugin
- **Menu Integration**: Adds items to the IDE's Tools menu

## Installation

This plugin comes pre-installed with Time_Warp as a demonstration of the plugin system.

## Usage


1. Open the Plugin Manager from Tools → Plugin Manager
2. Find "Sample Plugin" in the Installed tab
3. Click "Enable" to activate the plugin
4. New menu items will appear in the Tools menu:
   - 🔧 Sample Action
   - 📝 Insert Template
   - ℹ️ Plugin Info

## Plugin API Reference

Your plugin class receives the IDE instance as `self.ide`. Key APIs:

- `self.ide.editor` — Main text editor widget (Tkinter Text)
- `self.ide.menubar` — Main menu bar (Tkinter Menu)
- `self.ide.status_label` — Status bar label (if present)
- `self.ide.interpreter` — Time_WarpInterpreter instance
- `self.ide.output_panel` — Output panel widget
- `self.ide.turtle_canvas` — Turtle graphics canvas

### Example: Add a menu item
```python
tools_menu = None
for i in range(self.ide.menubar.index("end") + 1):
   if self.ide.menubar.entrycget(i, "label") == "Tools":
      tools_menu = self.ide.menubar.nametowidget(self.ide.menubar.entrycget(i, "menu"))
      break
if tools_menu:
   tools_menu.add_command(label="My Plugin Action", command=self.my_action)
```

### Example: Insert text in editor
```python
self.ide.editor.insert("insert", "Hello from plugin!")
```

### Example: Show a message box
```python
from tkinter import messagebox
messagebox.showinfo("Plugin", "Action complete!")
```

See the sample plugin code for more advanced usage.

## Development Notes

This plugin demonstrates:

- Proper plugin class inheritance
- Menu item management
- Editor interaction
- Error handling
- User feedback
- Plugin information display

Use this as a reference when creating your own Time_Warp plugins.

## Requirements

- Time_Warp IDE v2.0+
- Python 3.7+
- tkinter (included with Python)

## License

This plugin is distributed under the same license as Time_Warp IDE.