"""
Theme configuration management for IDE Time Warp
Handles saving and loading of UI theme preferences across time
"""

import json
import os
from pathlib import Path


def get_config_dir():
    """Get the configuration directory for Time Warp"""
    home_dir = Path.home()
    config_dir = home_dir / ".Time_Warp"
    config_dir.mkdir(exist_ok=True)
    return config_dir


def get_config_file():
    """Get the path to the configuration file"""
    return get_config_dir() / "config.json"


def load_config():
    """Load configuration from file"""
    config_file = get_config_file()

    # Default configuration
    default_config = {
        "dark_mode": False,
        "current_theme": "forest",  # Default theme - easy on the eyes
        "font_size": 11,
        "font_family": "Consolas",
        "theme_colors": {
            "primary": "#4A90E2",
            "secondary": "#7B68EE",
            "accent": "#FF6B6B",
            "success": "#4ECDC4",
            "warning": "#FFD93D",
            "info": "#6C5CE7",
        },
        "editor_settings": {
            "line_numbers": True,
            "syntax_highlighting": True,
            "auto_indent": True,
            "word_wrap": False,
            "tab_size": 4,
        },
        "window_settings": {
            "width": 1200,
            "height": 800,
            "maximized": False,
            "remember_size": True,
        },
        "advanced_features": {
            "code_completion": True,
            "real_time_syntax_check": True,
            "code_folding": True,
            "minimap": False,
        },
    }

    try:
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                # Merge with defaults to ensure all keys exist
                merged_config = default_config.copy()
                merged_config.update(config)
                return merged_config
    except Exception as e:
        print(f"Warning: Failed to load config: {e}")

    return default_config


def save_config(config):
    """Save configuration to file"""
    config_file = get_config_file()

    try:
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Warning: Failed to save config: {e}")
        return False


def reset_config():
    """Reset configuration to defaults"""
    config_file = get_config_file()
    try:
        if config_file.exists():
            config_file.unlink()
        return True
    except Exception as e:
        print(f"Warning: Failed to reset config: {e}")
        return False


def get_theme_colors(theme_name="dracula"):
    """Get theme colors based on theme name - each theme has a fixed brightness level"""

    # Theme definitions - dark themes: dracula, monokai, solarized, ocean
    # Light themes: spring, sunset, candy, forest
    themes = {
        # DARK THEMES
        "dracula": {
            "bg_primary": "#1E1E2E",  # Rich dark purple-blue
            "bg_secondary": "#282A36",  # Slightly lighter dark
            "bg_tertiary": "#44475A",  # Medium gray-purple
            "text_primary": "#F8F8F2",  # Bright white
            "text_secondary": "#BD93F9",  # Light purple
            "text_muted": "#6272A4",  # Muted blue
            "accent": "#FF79C6",  # Bright pink
            "accent_secondary": "#8BE9FD",  # Cyan
            "success": "#50FA7B",  # Bright green
            "warning": "#FFB86C",  # Orange
            "error": "#FF5555",  # Red
            "info": "#8BE9FD",  # Cyan
            "border": "#6272A4",  # Muted blue
            "selection": "#44475A",  # Selection background
            "button_bg": "#6272A4",  # Button background
            "button_hover": "#FF79C6",  # Button hover
            "toolbar_bg": "#21222C",  # Toolbar background
            "menu_bg": "#282A36",  # Menu background
            "syntax_keyword": "#FF79C6",  # Keywords
            "syntax_string": "#F1FA8C",  # Strings
            "syntax_comment": "#6272A4",  # Comments
            "syntax_number": "#BD93F9",  # Numbers
        },
        "monokai": {
            "bg_primary": "#272822",  # Dark olive green
            "bg_secondary": "#383830",  # Lighter olive
            "bg_tertiary": "#49483E",  # Medium olive
            "text_primary": "#F8F8F2",  # Bright white
            "text_secondary": "#A6E22E",  # Bright green
            "text_muted": "#75715E",  # Muted brown
            "accent": "#F92672",  # Bright magenta
            "accent_secondary": "#66D9EF",  # Cyan
            "success": "#A6E22E",  # Bright green
            "warning": "#E6DB74",  # Yellow
            "error": "#F92672",  # Magenta
            "info": "#66D9EF",  # Cyan
            "border": "#75715E",  # Muted brown
            "selection": "#49483E",  # Selection background
            "button_bg": "#75715E",  # Button background
            "button_hover": "#F92672",  # Button hover
            "toolbar_bg": "#1E1F1C",  # Toolbar background
            "menu_bg": "#383830",  # Menu background
            "syntax_keyword": "#F92672",  # Keywords
            "syntax_string": "#E6DB74",  # Strings
            "syntax_comment": "#75715E",  # Comments
            "syntax_number": "#AE81FF",  # Numbers
        },
        "solarized": {
            "bg_primary": "#002B36",  # Dark blue-green
            "bg_secondary": "#073642",  # Slightly lighter
            "bg_tertiary": "#586E75",  # Medium gray
            "text_primary": "#FDF6E3",  # Light cream (much more readable)
            "text_secondary": "#EEE8D5",  # Light beige (better contrast)
            "text_muted": "#93A1A1",  # Muted gray
            "accent": "#268BD2",  # Blue
            "accent_secondary": "#2AA198",  # Cyan
            "success": "#859900",  # Green
            "warning": "#B58900",  # Yellow
            "error": "#DC322F",  # Red
            "info": "#268BD2",  # Blue
            "border": "#586E75",  # Medium gray
            "selection": "#073642",  # Selection background
            "button_bg": "#586E75",  # Button background
            "button_hover": "#268BD2",  # Button hover
            "toolbar_bg": "#001E27",  # Toolbar background
            "menu_bg": "#073642",  # Menu background
            "syntax_keyword": "#859900",  # Keywords
            "syntax_string": "#2AA198",  # Strings
            "syntax_comment": "#586E75",  # Comments
            "syntax_number": "#D33682",  # Numbers
        },
        "ocean": {
            "bg_primary": "#0F1419",  # Very dark blue
            "bg_secondary": "#1F2937",  # Dark blue-gray
            "bg_tertiary": "#374151",  # Medium blue-gray
            "text_primary": "#F9FAFB",  # Near white
            "text_secondary": "#D1D5DB",  # Light gray
            "text_muted": "#9CA3AF",  # Muted gray
            "accent": "#3B82F6",  # Blue
            "accent_secondary": "#10B981",  # Green
            "success": "#10B981",  # Emerald
            "warning": "#F59E0B",  # Amber
            "error": "#EF4444",  # Red
            "info": "#06B6D4",  # Cyan
            "border": "#4B5563",  # Gray
            "selection": "#374151",  # Selection background
            "button_bg": "#4B5563",  # Button background
            "button_hover": "#3B82F6",  # Button hover
            "toolbar_bg": "#111827",  # Toolbar background
            "menu_bg": "#1F2937",  # Menu background
            "syntax_keyword": "#3B82F6",  # Keywords
            "syntax_string": "#10B981",  # Strings
            "syntax_comment": "#6B7280",  # Comments
            "syntax_number": "#8B5CF6",  # Numbers
        },
        # LIGHT THEMES
        "spring": {
            "bg_primary": "#F0FFF0",  # Honeydew
            "bg_secondary": "#E6FFE6",  # Light mint
            "bg_tertiary": "#D4F4DD",  # Pale green
            "text_primary": "#1B5E20",  # Darker green (better contrast)
            "text_secondary": "#2E7D32",  # Forest green
            "text_muted": "#388E3C",  # Darker medium green (more readable)
            "accent": "#00BCD4",  # Cyan
            "accent_secondary": "#8BC34A",  # Light green
            "success": "#4CAF50",  # Green
            "warning": "#FF9800",  # Orange
            "error": "#F44336",  # Red
            "info": "#03A9F4",  # Light blue
            "border": "#C8E6C9",  # Light green border
            "selection": "#E8F5E8",  # Very light green
            "button_bg": "#4CAF50",  # Button background
            "button_hover": "#66BB6A",  # Button hover
            "toolbar_bg": "#F1F8E9",  # Toolbar background
            "menu_bg": "#F0FFF0",  # Menu background
            "syntax_keyword": "#2E7D32",  # Keywords
            "syntax_string": "#00BCD4",  # Strings
            "syntax_comment": "#81C784",  # Comments
            "syntax_number": "#FF9800",  # Numbers
        },
        "sunset": {
            "bg_primary": "#FFF8E1",  # Light yellow
            "bg_secondary": "#FFECB3",  # Pale yellow
            "bg_tertiary": "#FFE082",  # Light gold
            "text_primary": "#BF360C",  # Darker red-orange (better contrast)
            "text_secondary": "#D84315",  # Deep orange (more readable)
            "text_muted": "#E65100",  # Darker orange (better visibility)
            "accent": "#E91E63",  # Pink
            "accent_secondary": "#9C27B0",  # Purple
            "success": "#4CAF50",  # Green
            "warning": "#FF9800",  # Orange
            "error": "#F44336",  # Red
            "info": "#2196F3",  # Blue
            "border": "#FFCC02",  # Gold border
            "selection": "#FFF3C4",  # Light cream
            "button_bg": "#E91E63",  # Button background
            "button_hover": "#C2185B",  # Button hover
            "toolbar_bg": "#FFFDE7",  # Toolbar background
            "menu_bg": "#FFF8E1",  # Menu background
            "syntax_keyword": "#9C27B0",  # Keywords
            "syntax_string": "#E91E63",  # Strings
            "syntax_comment": "#FF8F00",  # Comments
            "syntax_number": "#E65100",  # Numbers
        },
        "candy": {
            "bg_primary": "#FFF0F5",  # Lavender blush
            "bg_secondary": "#FFE4E1",  # Misty rose
            "bg_tertiary": "#FFCCCB",  # Light coral
            "text_primary": "#4A0E4E",  # Much darker magenta (better contrast)
            "text_secondary": "#6B1076",  # Darker orchid (better readability)
            "text_muted": "#B85C9E",  # More muted orchid (easier to read)
            "accent": "#FF1493",  # Deep pink
            "accent_secondary": "#00CED1",  # Dark turquoise
            "success": "#32CD32",  # Lime green
            "warning": "#FFD700",  # Gold
            "error": "#DC143C",  # Crimson
            "info": "#4169E1",  # Royal blue
            "border": "#F0B7CD",  # Pink border
            "selection": "#FFE4E6",  # Light pink
            "button_bg": "#FF1493",  # Button background
            "button_hover": "#C71585",  # Button hover
            "toolbar_bg": "#FDF2F8",  # Toolbar background
            "menu_bg": "#FFF0F5",  # Menu background
            "syntax_keyword": "#9932CC",  # Keywords
            "syntax_string": "#FF1493",  # Strings
            "syntax_comment": "#DA70D6",  # Comments
            "syntax_number": "#8B008B",  # Numbers
        },
        "forest": {
            "bg_primary": "#F5FFFA",  # Mint cream
            "bg_secondary": "#E0FFEF",  # Light mint
            "bg_tertiary": "#C8E6C9",  # Light green
            "text_primary": "#1B5E20",  # Dark green
            "text_secondary": "#2E7D32",  # Green
            "text_muted": "#66BB6A",  # Light green
            "accent": "#00695C",  # Dark teal
            "accent_secondary": "#00838F",  # Dark cyan
            "success": "#388E3C",  # Green
            "warning": "#F57C00",  # Orange
            "error": "#D32F2F",  # Red
            "info": "#0277BD",  # Light blue
            "border": "#A5D6A7",  # Light green border
            "selection": "#E8F5E8",  # Very light green
            "button_bg": "#00695C",  # Button background
            "button_hover": "#004D40",  # Button hover
            "toolbar_bg": "#F1F8E9",  # Toolbar background
            "menu_bg": "#F5FFFA",  # Menu background
            "syntax_keyword": "#00695C",  # Keywords
            "syntax_string": "#00838F",  # Strings
            "syntax_comment": "#81C784",  # Comments
            "syntax_number": "#F57C00",  # Numbers
        },
    }

    # Get the requested theme
    if theme_name not in themes:
        theme_name = "forest"  # Fallback to default

    return themes[theme_name]


def backup_config():
    """Create a backup of the current configuration"""
    config_file = get_config_file()
    if not config_file.exists():
        return False

    try:
        backup_file = config_file.with_suffix(".json.backup")
        import shutil

        shutil.copy2(config_file, backup_file)
        return True
    except Exception as e:
        print(f"Warning: Failed to backup config: {e}")
        return False


def restore_config_from_backup():
    """Restore configuration from backup"""
    config_dir = get_config_dir()
    backup_file = config_dir / "config.json.backup"
    config_file = get_config_file()

    try:
        if backup_file.exists():
            import shutil

            shutil.copy2(backup_file, config_file)
            return True
    except Exception as e:
        print(f"Warning: Failed to restore config from backup: {e}")

    return False


class ThemeManager:
    """Enhanced theme manager for IDE Time Warp with time-traveling styling"""

    def __init__(self):
        """Initialize theme manager"""
        self.config = load_config()
        self.current_theme = self.config.get("current_theme", "dracula")
        # Initialize with default dark theme colors
        self.current_colors = get_theme_colors(self.current_theme)
        
    def set_theme(self, theme_name):
        """Set the current theme"""
        if theme_name in ['dracula', 'monokai', 'solarized', 'ocean', 
                          'spring', 'sunset', 'candy', 'forest']:
            self.current_theme = theme_name
            self.current_colors = get_theme_colors(theme_name)
            
            # Save to config
            self.config["current_theme"] = theme_name
            save_config(self.config)
        else:
            raise ValueError(f"Unknown theme: {theme_name}")

    def apply_theme(self, root, theme_name="dracula"):
        """Apply comprehensive theme to the root window and all components"""
        try:
            self.current_colors = get_theme_colors(theme_name)

            # Configure root window with gradient-like appearance
            root.configure(bg=self.current_colors["bg_primary"])

            # Configure ttk styles for modern appearance
            self._configure_ttk_styles(root)

        except Exception as e:
            print(f"Theme application error: {e}")

    def _configure_ttk_styles(self, root):
        """Configure ttk widget styles for modern appearance"""
        try:
            import tkinter.ttk as ttk

            style = ttk.Style()
            colors = self.current_colors

            # Configure modern button style
            style.configure(
                "Modern.TButton",
                background=colors["accent"],
                foreground="white",
                borderwidth=0,
                focuscolor=colors["accent_secondary"],
                relief="flat",
                padding=(12, 8),
            )

            style.map(
                "Modern.TButton",
                background=[
                    ("active", colors["button_hover"]),
                    ("pressed", colors["accent_secondary"]),
                ],
            )

            # Configure modern frame style
            style.configure(
                "Modern.TFrame",
                background=colors["bg_secondary"],
                relief="flat",
                borderwidth=1,
            )

            # Configure modern notebook (tab) style
            style.configure(
                "Modern.TNotebook",
                background=colors["bg_secondary"],
                borderwidth=0,
                tabmargins=[2, 5, 2, 0],
            )

            style.configure(
                "Modern.TNotebook.Tab",
                background=colors["bg_tertiary"],
                foreground=colors["text_primary"],
                padding=[20, 8],
                borderwidth=0,
            )

            style.map(
                "Modern.TNotebook.Tab",
                background=[
                    ("selected", colors["accent"]),
                    ("active", colors["accent_secondary"]),
                ],
                foreground=[("selected", "white"), ("active", "white")],
            )

            # Configure modern label style
            style.configure(
                "Modern.TLabel",
                background=colors["bg_secondary"],
                foreground=colors["text_primary"],
            )

            # Configure modern entry style
            style.configure(
                "Modern.TEntry",
                fieldbackground=colors["bg_primary"],
                borderwidth=2,
                relief="flat",
                insertcolor=colors["accent"],
            )

            # Configure modern menu style
            style.configure(
                "Modern.TMenubutton",
                background=colors["accent"],
                foreground="white",
                borderwidth=0,
                relief="flat",
                padding=(10, 6),
            )

            # Configure modern scrollbar style
            style.configure(
                "Modern.Vertical.TScrollbar",
                background=colors["bg_tertiary"],
                troughcolor=colors["bg_secondary"],
                arrowcolor=colors["text_muted"],
                borderwidth=0,
            )

        except Exception as e:
            print(f"TTK style configuration error: {e}")

    def get_colors(self, theme_name=None):
        """Get colors for specified theme or current theme"""
        if theme_name:
            # Temporarily switch to requested theme to get colors
            old_theme = self.current_theme
            self.set_theme(theme_name)
            colors = self.current_colors.copy()
            self.set_theme(old_theme)  # Switch back
            return colors
        return self.current_colors

    def apply_text_widget_theme(self, text_widget):
        """Apply theme to text widgets with syntax highlighting colors"""
        try:
            colors = self.current_colors

            text_widget.configure(
                bg=colors["bg_primary"],
                fg=colors["text_primary"],
                insertbackground=colors["accent"],
                selectbackground=colors["selection"],
                selectforeground=colors["text_primary"],
                relief="flat",
                borderwidth=0,
                highlightthickness=2,
                highlightcolor=colors["accent"],
                highlightbackground=colors["border"],
            )

            # Configure syntax highlighting tags if they exist
            for tag_name, color_key in [
                ("keyword", "syntax_keyword"),
                ("string", "syntax_string"),
                ("comment", "syntax_comment"),
                ("number", "syntax_number"),
            ]:
                try:
                    text_widget.tag_configure(tag_name, foreground=colors[color_key])
                except:
                    pass

        except Exception as e:
            print(f"Text widget theme error: {e}")

    def apply_canvas_theme(self, canvas):
        """Apply theme to canvas widgets"""
        try:
            colors = self.current_colors

            canvas.configure(
                bg=colors["bg_primary"],
                highlightthickness=2,
                highlightcolor=colors["accent"],
                highlightbackground=colors["border"],
            )

        except Exception as e:
            print(f"Canvas theme error: {e}")

    def save_config(self, config_updates):
        """Save configuration updates"""
        self.config.update(config_updates)
        save_config(self.config)
