# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Time_Warp IDE
Creates a standalone Linux executable with all dependencies
"""

import os
import sys
from pathlib import Path

# Get the project root directory
project_root = Path('.').absolute()

# Define data files to include
data_files = [
    # Core language modules
    ('core', 'core'),
    # Tools and utilities  
    ('tools', 'tools'),
    # Games directory (if exists)
    ('games', 'games'),
    # Plugins directory (if exists)
    ('plugins', 'plugins'),
]

# Add demo files if they exist
import glob
for pattern in ['*.pilot', '*.bas', '*.logo', '*.timewarp']:
    for file in glob.glob(pattern):
        data_files.append((file, '.'))

# Add documentation
for doc in ['README.md', 'requirements.txt']:
    if os.path.exists(doc):
        data_files.append((doc, '.'))

# Hidden imports - modules that PyInstaller might miss
hidden_imports = [
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'tkinter.scrolledtext',
    'pygame',
    'pygame.mixer',
    'pygame.display',
    'pygame.draw',
    'pygame.surface',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'subprocess',
    'threading',
    'json',
    'os',
    'sys',
    'pathlib',
    'platform',
    'time',
    'datetime',
    'math',
    'random',
    're',
    'collections',
    'itertools',
    'functools',
    # Language executors
    'core.interpreter',
    'core.languages.basic',
    'core.languages.pilot', 
    'core.languages.logo',
    'core.languages.python_executor',
    'core.languages.javascript_executor',
    'core.languages.perl',
    # Hardware and IoT modules
    'core.hardware.raspberry_pi',
    'core.iot.smart_home',
    'core.iot.sensors',
    # Tools
    'tools.theme',
    'tools.file_manager',
    # Games
    'games.engine.physics',
    'games.engine.rendering',
    'games.basic_games',
    # Plugins
    'plugins.sample_plugin',
]

# Collect all Python files in core directories
def collect_py_files(directory):
    """Recursively collect all .py files from a directory"""
    py_files = []
    if os.path.exists(directory):
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, '.')
                    py_files.append(rel_path)
    return py_files

# Collect additional Python modules
additional_modules = []
for directory in ['core', 'tools', 'games', 'plugins']:
    additional_modules.extend(collect_py_files(directory))

# Analysis configuration
a = Analysis(
    ['Time_Warp.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=data_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'jupyter',
        'notebook',
        'IPython',
        'tornado',
        'werkzeug',
        'flask',
        'django',
        'requests',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove duplicate files
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Create executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Time_Warp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress executable
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI application
    disable_windowed_traceback=False,
    icon=None,  # We'll add an icon later
)

# Optional: Create a directory distribution instead
# This can be useful for debugging
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles, 
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Time_Warp_dist'
)