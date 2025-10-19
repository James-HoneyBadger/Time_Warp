"""
Theme configuration management for IDE Time Warp
Handles saving and loading of UI theme preferences across time
"""

import json
import tkinter as tk
from pathlib import Path
import os
from datetime import datetime


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

    def _deep_merge(a, b):
        """Recursively merge dict b into dict a and return the result."""
        for k, v in b.items():
            if k in a and isinstance(a[k], dict) and isinstance(v, dict):
                a[k] = _deep_merge(a[k], v)
            else:
                a[k] = v
        return a

    try:
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                # Deep-merge with defaults to ensure nested keys are preserved
                merged_config = _deep_merge(default_config.copy(), config)
                return merged_config
    except (OSError, json.JSONDecodeError) as e:
        print(f"Warning: Failed to load config: {e}")

    return default_config


# Builtin theme registry - centralized so other helpers can reference it
BUILTIN_THEMES = {
    # DARK THEMES
    "dracula": {
        "bg_primary": "#1E1E2E",
        "bg_secondary": "#282A36",
        "bg_tertiary": "#44475A",
        "text_primary": "#F8F8F2",
        "text_secondary": "#BD93F9",
        "text_muted": "#6272A4",
        "accent": "#FF79C6",
        "accent_secondary": "#8BE9FD",
        "success": "#50FA7B",
        "warning": "#FFB86C",
        "error": "#FF5555",
        "info": "#8BE9FD",
        "border": "#6272A4",
        "selection": "#44475A",
        "button_bg": "#6272A4",
        "button_hover": "#FF79C6",
        "toolbar_bg": "#21222C",
        "menu_bg": "#282A36",
        "syntax_keyword": "#FF79C6",
        "syntax_string": "#F1FA8C",
        "syntax_comment": "#6272A4",
        "syntax_number": "#BD93F9",
    },
    "monokai": {
        "bg_primary": "#272822",
        "bg_secondary": "#383830",
        "bg_tertiary": "#49483E",
        "text_primary": "#F8F8F2",
        "text_secondary": "#A6E22E",
        "text_muted": "#75715E",
        "accent": "#F92672",
        "accent_secondary": "#66D9EF",
        "success": "#A6E22E",
        "warning": "#E6DB74",
        "error": "#F92672",
        "info": "#66D9EF",
        "border": "#75715E",
        "selection": "#49483E",
        "button_bg": "#75715E",
        "button_hover": "#F92672",
        "toolbar_bg": "#1E1F1C",
        "menu_bg": "#383830",
        "syntax_keyword": "#F92672",
        "syntax_string": "#E6DB74",
        "syntax_comment": "#75715E",
        "syntax_number": "#AE81FF",
    },
    "solarized": {
        "bg_primary": "#002B36",
        "bg_secondary": "#073642",
        "bg_tertiary": "#586E75",
        "text_primary": "#FDF6E3",
        "text_secondary": "#EEE8D5",
        "text_muted": "#93A1A1",
        "accent": "#268BD2",
        "accent_secondary": "#2AA198",
        "success": "#859900",
        "warning": "#B58900",
        "error": "#DC322F",
        "info": "#268BD2",
        "border": "#586E75",
        "selection": "#073642",
        "button_bg": "#586E75",
        "button_hover": "#268BD2",
        "toolbar_bg": "#001E27",
        "menu_bg": "#073642",
        "syntax_keyword": "#859900",
        "syntax_string": "#2AA198",
        "syntax_comment": "#586E75",
        "syntax_number": "#D33682",
    },
    "ocean": {
        "bg_primary": "#0F1419",
        "bg_secondary": "#1F2937",
        "bg_tertiary": "#374151",
        "text_primary": "#F9FAFB",
        "text_secondary": "#D1D5DB",
        "text_muted": "#9CA3AF",
        "accent": "#3B82F6",
        "accent_secondary": "#10B981",
        "success": "#10B981",
        "warning": "#F59E0B",
        "error": "#EF4444",
        "info": "#06B6D4",
        "border": "#4B5563",
        "selection": "#374151",
        "button_bg": "#4B5563",
        "button_hover": "#3B82F6",
        "toolbar_bg": "#111827",
        "menu_bg": "#1F2937",
        "syntax_keyword": "#3B82F6",
        "syntax_string": "#10B981",
        "syntax_comment": "#6B7280",
        "syntax_number": "#8B5CF6",
    },
    "midnight": {
        "bg_primary": "#0b0f1a",
        "bg_secondary": "#111827",
        "bg_tertiary": "#1f2937",
        "text_primary": "#e6eef8",
        "text_secondary": "#a6b8d6",
        "text_muted": "#6b7280",
        "accent": "#7c3aed",
        "accent_secondary": "#60a5fa",
        "success": "#10b981",
        "warning": "#f59e0b",
        "error": "#ef4444",
        "info": "#60a5fa",
        "border": "#374151",
        "selection": "#111827",
        "button_bg": "#374151",
        "button_hover": "#7c3aed",
        "toolbar_bg": "#071129",
        "menu_bg": "#0b1220",
        "syntax_keyword": "#7c3aed",
        "syntax_string": "#f97316",
        "syntax_comment": "#6b7280",
        "syntax_number": "#60a5fa",
    },
    "sepia": {
        "bg_primary": "#f4ecd8",
        "bg_secondary": "#efe6cf",
        "bg_tertiary": "#e7dcc1",
        "text_primary": "#3b2f2f",
        "text_secondary": "#5a4639",
        "text_muted": "#7a6a5a",
        "accent": "#d87f33",
        "accent_secondary": "#b55a1e",
        "success": "#6aa84f",
        "warning": "#f1c232",
        "error": "#cc0000",
        "info": "#6fa8dc",
        "border": "#d0c0a8",
        "selection": "#efe6cf",
        "button_bg": "#d87f33",
        "button_hover": "#b55a1e",
        "toolbar_bg": "#faf6ec",
        "menu_bg": "#f4ecd8",
        "syntax_keyword": "#b55a1e",
        "syntax_string": "#d87f33",
        "syntax_comment": "#7a6a5a",
        "syntax_number": "#6aa84f",
    },
    "ice": {
        "bg_primary": "#f3fbff",
        "bg_secondary": "#e8f6ff",
        "bg_tertiary": "#d6eef9",
        "text_primary": "#05264a",
        "text_secondary": "#0b4a6f",
        "text_muted": "#558aa3",
        "accent": "#0ea5e9",
        "accent_secondary": "#06b6d4",
        "success": "#16a34a",
        "warning": "#f59e0b",
        "error": "#ef4444",
        "info": "#0ea5e9",
        "border": "#bfe9ff",
        "selection": "#e8f6ff",
        "button_bg": "#0ea5e9",
        "button_hover": "#0284c7",
        "toolbar_bg": "#f0fbff",
        "menu_bg": "#f3fbff",
        "syntax_keyword": "#0369a1",
        "syntax_string": "#06b6d4",
        "syntax_comment": "#7dd3fc",
        "syntax_number": "#1d4ed8",
    },
    "github-dark": {
        "bg_primary": "#0d1117",
        "bg_secondary": "#161b22",
        "bg_tertiary": "#21262d",
        "text_primary": "#f0f6fc",
        "text_secondary": "#c9d1d9",
        "text_muted": "#8b949e",
        "accent": "#58a6ff",
        "accent_secondary": "#79c0ff",
        "success": "#56d364",
        "warning": "#d29922",
        "error": "#f85149",
        "info": "#79c0ff",
        "border": "#30363d",
        "selection": "#21262d",
        "button_bg": "#30363d",
        "button_hover": "#58a6ff",
        "toolbar_bg": "#0d1117",
        "menu_bg": "#161b22",
        "syntax_keyword": "#ff7b72",
        "syntax_string": "#a5c9ea",
        "syntax_comment": "#8b949e",
        "syntax_number": "#79c0ff",
    },
    "github-light": {
        "bg_primary": "#ffffff",
        "bg_secondary": "#f6f8fa",
        "bg_tertiary": "#f6f8fa",
        "text_primary": "#24292f",
        "text_secondary": "#57606a",
        "text_muted": "#656d76",
        "accent": "#0969da",
        "accent_secondary": "#218bff",
        "success": "#1a7f37",
        "warning": "#bf8700",
        "error": "#cf222e",
        "info": "#218bff",
        "border": "#d0d7de",
        "selection": "#f6f8fa",
        "button_bg": "#f6f8fa",
        "button_hover": "#0969da",
        "toolbar_bg": "#ffffff",
        "menu_bg": "#f6f8fa",
        "syntax_keyword": "#cf222e",
        "syntax_string": "#0a3069",
        "syntax_comment": "#656d76",
        "syntax_number": "#0550ae",
    },
    "vscode-dark": {
        "bg_primary": "#1e1e1e",
        "bg_secondary": "#252526",
        "bg_tertiary": "#2d2d30",
        "text_primary": "#cccccc",
        "text_secondary": "#ffffff",
        "text_muted": "#858585",
        "accent": "#007acc",
        "accent_secondary": "#3794ff",
        "success": "#4ec9b0",
        "warning": "#dcdcaa",
        "error": "#f44747",
        "info": "#3794ff",
        "border": "#3e3e42",
        "selection": "#264f78",
        "button_bg": "#3e3e42",
        "button_hover": "#007acc",
        "toolbar_bg": "#1e1e1e",
        "menu_bg": "#252526",
        "syntax_keyword": "#569cd6",
        "syntax_string": "#ce9178",
        "syntax_comment": "#6a9955",
        "syntax_number": "#b5cea8",
    },
    "vscode-light": {
        "bg_primary": "#ffffff",
        "bg_secondary": "#f3f3f3",
        "bg_tertiary": "#e7e7e7",
        "text_primary": "#000000",
        "text_secondary": "#3c3c3c",
        "text_muted": "#6c6c6c",
        "accent": "#007acc",
        "accent_secondary": "#3794ff",
        "success": "#4ec9b0",
        "warning": "#dcdcaa",
        "error": "#f44747",
        "info": "#3794ff",
        "border": "#e5e5e5",
        "selection": "#add6ff",
        "button_bg": "#e5e5e5",
        "button_hover": "#007acc",
        "toolbar_bg": "#ffffff",
        "menu_bg": "#f3f3f3",
        "syntax_keyword": "#0000ff",
        "syntax_string": "#a31515",
        "syntax_comment": "#008000",
        "syntax_number": "#098658",
    },
    "nord": {
        "bg_primary": "#2e3440",
        "bg_secondary": "#3b4252",
        "bg_tertiary": "#434c5e",
        "text_primary": "#eceff4",
        "text_secondary": "#d8dee9",
        "text_muted": "#81a1c1",
        "accent": "#88c0d0",
        "accent_secondary": "#8fbcbb",
        "success": "#a3be8c",
        "warning": "#ebcb8b",
        "error": "#bf616a",
        "info": "#88c0d0",
        "border": "#4c566a",
        "selection": "#434c5e",
        "button_bg": "#4c566a",
        "button_hover": "#88c0d0",
        "toolbar_bg": "#2e3440",
        "menu_bg": "#3b4252",
        "syntax_keyword": "#81a1c1",
        "syntax_string": "#a3be8c",
        "syntax_comment": "#616e88",
        "syntax_number": "#b48ead",
    },
    "one-dark": {
        "bg_primary": "#282c34",
        "bg_secondary": "#21252b",
        "bg_tertiary": "#181a1f",
        "text_primary": "#abb2bf",
        "text_secondary": "#98c379",
        "text_muted": "#5c6370",
        "accent": "#61afef",
        "accent_secondary": "#c678dd",
        "success": "#98c379",
        "warning": "#e5c07b",
        "error": "#e06c75",
        "info": "#61afef",
        "border": "#3e4451",
        "selection": "#3e4451",
        "button_bg": "#3e4451",
        "button_hover": "#61afef",
        "toolbar_bg": "#282c34",
        "menu_bg": "#21252b",
        "syntax_keyword": "#c678dd",
        "syntax_string": "#98c379",
        "syntax_comment": "#5c6370",
        "syntax_number": "#d19a66",
    },
    "gruvbox": {
        "bg_primary": "#282828",
        "bg_secondary": "#3c3836",
        "bg_tertiary": "#504945",
        "text_primary": "#ebdbb2",
        "text_secondary": "#d5c4a1",
        "text_muted": "#bdae93",
        "accent": "#fb4934",
        "accent_secondary": "#fe8019",
        "success": "#b8bb26",
        "warning": "#fabd2f",
        "error": "#fb4934",
        "info": "#83a598",
        "border": "#665c54",
        "selection": "#504945",
        "button_bg": "#665c54",
        "button_hover": "#fb4934",
        "toolbar_bg": "#282828",
        "menu_bg": "#3c3836",
        "syntax_keyword": "#fb4934",
        "syntax_string": "#b8bb26",
        "syntax_comment": "#928374",
        "syntax_number": "#d3869b",
    },
    "tokyo-night": {
        "bg_primary": "#1a1b26",
        "bg_secondary": "#16161e",
        "bg_tertiary": "#2a2a37",
        "text_primary": "#c0caf5",
        "text_secondary": "#a9b1d6",
        "text_muted": "#565f89",
        "accent": "#7dcfff",
        "accent_secondary": "#bb9af7",
        "success": "#9ece6a",
        "warning": "#e0af68",
        "error": "#f7768e",
        "info": "#7dcfff",
        "border": "#292e42",
        "selection": "#2a2a37",
        "button_bg": "#292e42",
        "button_hover": "#7dcfff",
        "toolbar_bg": "#1a1b26",
        "menu_bg": "#16161e",
        "syntax_keyword": "#bb9af7",
        "syntax_string": "#9ece6a",
        "syntax_comment": "#565f89",
        "syntax_number": "#ff9e64",
    },
    "synthwave": {
        "bg_primary": "#2a2139",
        "bg_secondary": "#34294f",
        "bg_tertiary": "#3f2c5c",
        "text_primary": "#f92aad",
        "text_secondary": "#ff8e00",
        "text_muted": "#848bbd",
        "accent": "#f92aad",
        "accent_secondary": "#ff8e00",
        "success": "#72f1b8",
        "warning": "#fede5d",
        "error": "#fe4450",
        "info": "#36f9f6",
        "border": "#495495",
        "selection": "#3f2c5c",
        "button_bg": "#495495",
        "button_hover": "#f92aad",
        "toolbar_bg": "#2a2139",
        "menu_bg": "#34294f",
        "syntax_keyword": "#f92aad",
        "syntax_string": "#ff8e00",
        "syntax_comment": "#848bbd",
        "syntax_number": "#36f9f6",
    },
    "material-dark": {
        "bg_primary": "#263238",
        "bg_secondary": "#37474f",
        "bg_tertiary": "#455a64",
        "text_primary": "#ffffff",
        "text_secondary": "#b0bec5",
        "text_muted": "#78909c",
        "accent": "#00bcd4",
        "accent_secondary": "#4dd0e1",
        "success": "#4caf50",
        "warning": "#ff9800",
        "error": "#f44336",
        "info": "#2196f3",
        "border": "#546e7a",
        "selection": "#455a64",
        "button_bg": "#546e7a",
        "button_hover": "#00bcd4",
        "toolbar_bg": "#263238",
        "menu_bg": "#37474f",
        "syntax_keyword": "#c792ea",
        "syntax_string": "#c3e88d",
        "syntax_comment": "#546e7a",
        "syntax_number": "#f78c6c",
    },
    "material-light": {
        "bg_primary": "#fafafa",
        "bg_secondary": "#ffffff",
        "bg_tertiary": "#f5f5f5",
        "text_primary": "#212121",
        "text_secondary": "#757575",
        "text_muted": "#9e9e9e",
        "accent": "#00bcd4",
        "accent_secondary": "#4dd0e1",
        "success": "#4caf50",
        "warning": "#ff9800",
        "error": "#f44336",
        "info": "#2196f3",
        "border": "#e0e0e0",
        "selection": "#e3f2fd",
        "button_bg": "#e0e0e0",
        "button_hover": "#00bcd4",
        "toolbar_bg": "#fafafa",
        "menu_bg": "#ffffff",
        "syntax_keyword": "#000000",
        "syntax_string": "#2e7d32",
        "syntax_comment": "#9e9e9e",
        "syntax_number": "#f57c00",
    },
    "ember": {
        "bg_primary": "#1b0b0b",
        "bg_secondary": "#2b0f0f",
        "bg_tertiary": "#421616",
        "text_primary": "#ffece6",
        "text_secondary": "#ffb4a2",
        "text_muted": "#d78a7a",
        "accent": "#ff6b35",
        "accent_secondary": "#ff9b71",
        "success": "#9ae66e",
        "warning": "#ffb703",
        "error": "#ff3b30",
        "info": "#ff6b35",
        "border": "#3a1a1a",
        "selection": "#2b0f0f",
        "button_bg": "#3a1a1a",
        "button_hover": "#ff6b35",
        "toolbar_bg": "#120606",
        "menu_bg": "#1b0b0b",
        "syntax_keyword": "#ff6b35",
        "syntax_string": "#ff9b71",
        "syntax_comment": "#6b4b46",
        "syntax_number": "#ffb86c",
    },
    # LIGHT THEMES
    "spring": {
        "bg_primary": "#F0FFF0",
        "bg_secondary": "#E6FFE6",
        "bg_tertiary": "#D4F4DD",
        "text_primary": "#1B5E20",
        "text_secondary": "#2E7D32",
        "text_muted": "#388E3C",
        "accent": "#00BCD4",
        "accent_secondary": "#8BC34A",
        "success": "#4CAF50",
        "warning": "#FF9800",
        "error": "#F44336",
        "info": "#03A9F4",
        "border": "#C8E6C9",
        "selection": "#E8F5E8",
        "button_bg": "#4CAF50",
        "button_hover": "#66BB6A",
        "toolbar_bg": "#F1F8E9",
        "menu_bg": "#F0FFF0",
        "syntax_keyword": "#2E7D32",
        "syntax_string": "#00BCD4",
        "syntax_comment": "#81C784",
        "syntax_number": "#FF9800",
    },
    "sunset": {
        "bg_primary": "#FFF8E1",
        "bg_secondary": "#FFECB3",
        "bg_tertiary": "#FFE082",
        "text_primary": "#BF360C",
        "text_secondary": "#D84315",
        "text_muted": "#E65100",
        "accent": "#E91E63",
        "accent_secondary": "#9C27B0",
        "success": "#4CAF50",
        "warning": "#FF9800",
        "error": "#F44336",
        "info": "#2196F3",
        "border": "#FFCC02",
        "selection": "#FFF3C4",
        "button_bg": "#E91E63",
        "button_hover": "#C2185B",
        "toolbar_bg": "#FFFDE7",
        "menu_bg": "#FFF8E1",
        "syntax_keyword": "#9C27B0",
        "syntax_string": "#E91E63",
        "syntax_comment": "#FF8F00",
        "syntax_number": "#E65100",
    },
    "candy": {
        "bg_primary": "#FFF0F5",
        "bg_secondary": "#FFE4E1",
        "bg_tertiary": "#FFCCCB",
        "text_primary": "#4A0E4E",
        "text_secondary": "#6B1076",
        "text_muted": "#B85C9E",
        "accent": "#FF1493",
        "accent_secondary": "#00CED1",
        "success": "#32CD32",
        "warning": "#FFD700",
        "error": "#DC143C",
        "info": "#4169E1",
        "border": "#F0B7CD",
        "selection": "#FFE4E6",
        "button_bg": "#FF1493",
        "button_hover": "#C71585",
        "toolbar_bg": "#FDF2F8",
        "menu_bg": "#FFF0F5",
        "syntax_keyword": "#9932CC",
        "syntax_string": "#FF1493",
        "syntax_comment": "#DA70D6",
        "syntax_number": "#8B008B",
    },
    "forest": {
        "bg_primary": "#F5FFFA",
        "bg_secondary": "#E0FFEF",
        "bg_tertiary": "#C8E6C9",
        "text_primary": "#1B5E20",
        "text_secondary": "#2E7D32",
        "text_muted": "#66BB6A",
        "accent": "#00695C",
        "accent_secondary": "#00838F",
        "success": "#388E3C",
        "warning": "#F57C00",
        "error": "#D32F2F",
        "info": "#0277BD",
        "border": "#A5D6A7",
        "selection": "#E8F5E8",
        "button_bg": "#00695C",
        "button_hover": "#004D40",
        "toolbar_bg": "#F1F8E9",
        "menu_bg": "#F5FFFA",
        "syntax_keyword": "#00695C",
        "syntax_string": "#00838F",
        "syntax_comment": "#81C784",
        "syntax_number": "#F57C00",
    },
}


def save_config(config):
    """Save configuration to file"""
    config_file = get_config_file()
    try:
        # Write atomically: write to a temp file and replace
        # Add metadata for debugging
        try:
            meta = config.get("_meta", {}) if isinstance(config, dict) else {}
            meta["last_saved"] = datetime.now().isoformat()
            meta["last_saved_pid"] = os.getpid()
            config["_meta"] = meta
        except Exception:
            pass

        tmp = config_file.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            f.flush()
        tmp.replace(config_file)
        return True
    except OSError as e:
        print(f"Warning: Failed to save config: {e}")
        return False


def reset_config():
    """Reset configuration to defaults"""
    config_file = get_config_file()
    try:
        if config_file.exists():
            config_file.unlink()
        return True
    except OSError as e:
        print(f"Warning: Failed to reset config: {e}")
        return False


def get_theme_colors(theme_name="dracula"):
    """Get theme colors based on theme name.

    Supports builtin and custom themes from config.
    """
    # Combine builtin themes with any user-provided custom themes from config
    cfg = load_config()
    custom = cfg.get("custom_themes", {}) if isinstance(cfg, dict) else {}

    combined = {}
    combined.update(BUILTIN_THEMES)
    combined.update(custom)

    # Determine selected theme with graceful fallbacks
    if theme_name not in combined:
        theme_name = cfg.get("current_theme", "forest")
        if theme_name not in combined:
            theme_name = next(iter(combined.keys()), "dracula")

    return combined[theme_name]


def available_themes():
    """Return a list of available theme names.

    Includes builtin themes and any user-defined custom themes.
    """
    # Build from BUILTIN_THEMES plus any custom themes in config
    cfg = load_config()
    custom = cfg.get("custom_themes", {}) if isinstance(cfg, dict) else {}

    names = list(BUILTIN_THEMES.keys())
    # Append custom themes in defined order
    for k in custom.keys():
        if k not in names:
            names.append(k)

    return names


def get_theme_preview(theme_name):
    """Return a small preview color tuple for UI swatches.

    Returns (bg_primary, bg_secondary, accent).
    """
    colors = get_theme_colors(theme_name)
    return (
        colors.get("bg_primary", "#000000"),
        colors.get("bg_secondary", "#222222"),
        colors.get("accent", "#888888"),
    )


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
    except (OSError, shutil.Error) as e:
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
    except (OSError, shutil.Error) as e:
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
        if theme_name in available_themes():
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
            self._configure_ttk_styles()

        except (KeyError, RuntimeError) as e:
            # KeyError if a color key is missing; RuntimeError for ttk issues
            print(f"Theme application error: {e}")

    def _configure_ttk_styles(self):
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

        except (ImportError, RuntimeError, KeyError) as e:
            print(f"TTK style configuration error: {e}")

    def get_colors(self, theme_name=None):
        """Get colors for specified theme or current theme"""
        if theme_name:
            return get_theme_colors(theme_name)
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
                    col = colors.get(color_key)
                    if col:
                        text_widget.tag_configure(tag_name, foreground=col)
                except (tk.TclError, TypeError, NameError):
                    # Skip tag configuration if invalid
                    pass

        except (KeyError, TypeError) as e:
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

        except (KeyError, RuntimeError) as e:
            print(f"Canvas theme error: {e}")

    def apply_widget_theme(self, widget):
        """Recursively apply theme to a Tk widget and its children.

        Ensures canvases, frames, labels and text widgets receive consistent
        color treatment even if created outside the main theme application
        flow.
        """
        try:
            colors = self.current_colors

            # Apply to common widget types
            cls_name = widget.winfo_class().lower()

            if cls_name in ["frame", "tframe", "labelframe", "canvas"]:
                try:
                    widget.configure(
                        bg=colors.get("bg_secondary", colors["bg_primary"])
                    )
                except (tk.TclError, KeyError, AttributeError):
                    pass

            if cls_name in ["text", "scrolledtext", "entry"]:
                try:
                    widget.configure(
                        bg=colors.get("bg_primary"),
                        fg=colors.get("text_primary"),
                        insertbackground=colors.get("text_primary"),
                    )
                except (tk.TclError, AttributeError):
                    pass

            # Canvas special: use canvas theme
            if cls_name == "canvas":
                try:
                    widget.configure(bg=colors.get("bg_primary"))
                except (tk.TclError, AttributeError):
                    pass

            # Recursively theme children
            for child in widget.winfo_children():
                try:
                    self.apply_widget_theme(child)
                except (AttributeError, RuntimeError):
                    pass

        except (KeyError, AttributeError, RuntimeError) as e:
            print(f"Widget theming error: {e}")

    def save_config(self, config_updates):
        """Save configuration updates"""

        # Deep-merge updates into the existing config to avoid clobbering nested dicts
        def _deep_merge(a, b):
            for k, v in b.items():
                if k in a and isinstance(a[k], dict) and isinstance(v, dict):
                    a[k] = _deep_merge(a[k], v)
                else:
                    a[k] = v
            return a

        try:
            self.config = _deep_merge(self.config or {}, config_updates or {})
            return save_config(self.config)
        except Exception as e:
            print(f"Warning: Failed to merge/save config: {e}")
            return False

    def add_custom_theme(self, name, theme_dict):
        """Add a custom theme to the config and persist it."""
        if not isinstance(theme_dict, dict):
            raise TypeError("theme_dict must be a dict")
        custom = self.config.get("custom_themes", {})

        # Ensure unique name
        base = name
        i = 1
        while name in BUILTIN_THEMES or name in custom:
            name = f"{base}_{i}"
            i += 1

        custom[name] = theme_dict
        self.config["custom_themes"] = custom
        save_config(self.config)
        return name

    def export_theme(self, theme_name, file_path):
        """Export a theme (builtin or custom) to a JSON file at file_path."""
        theme = get_theme_colors(theme_name)
        export_obj = {"name": theme_name, "theme": theme}
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(export_obj, f, indent=2, ensure_ascii=False)
            return True
        except OSError as e:
            print(f"Warning: Failed to export theme: {e}")
            return False

    def import_theme_from_file(self, file_path):
        """Import a theme from a JSON file.

        Returns the new theme name or None on failure.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"Warning: Failed to read theme file: {e}")
            return None

        # Support files that are either {"name":..., "theme": {...}}
        # or a raw theme dict
        if isinstance(data, dict) and "theme" in data and "name" in data:
            name = data["name"]
            theme_dict = data["theme"]
        elif isinstance(data, dict):
            # raw theme dict -> derive name from filename
            theme_dict = data
            name = None
        else:
            return None

        # If name not provided, generate from file stem
        if not name:
            import pathlib

            name = pathlib.Path(file_path).stem

        return self.add_custom_theme(name, theme_dict)

    def restore_defaults(self):
        """Restore default configuration.

        Removes custom themes and resets the current theme by deleting the
        user's config file and reloading defaults.
        """
        try:
            reset_config()
            self.config = load_config()
            self.current_theme = self.config.get("current_theme", "forest")
            self.current_colors = get_theme_colors(self.current_theme)
            return True
        except OSError as e:
            print(f"Warning: Failed to restore defaults: {e}")
            return False
