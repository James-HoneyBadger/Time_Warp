# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Time_Warp IDE macOS Application Bundle
Creates a standalone macOS .app bundle with all dependencies
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
    # GUI components
    ('gui', 'gui'),
    # Examples and documentation
    ('examples', 'examples'),
    ('docs', 'docs'),
]

# Add demo files if they exist
import glob
for pattern in ['*.pilot', '*.bas', '*.logo', '*.timewarp']:
    for file in glob.glob(pattern):
        data_files.append((file, '.'))

# Add documentation and configuration files
for doc in ['README.md', 'requirements.txt', 'CHANGELOG.md']:
    if os.path.exists(doc):
        data_files.append((doc, '.'))

# Hidden imports - modules that PyInstaller might miss
hidden_imports = [
    # Tkinter and GUI
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'tkinter.scrolledtext',
    'tkinter.simpledialog',
    'tkinter.colorchooser',
    'tkinter.font',
    # Pygame for enhanced graphics
    'pygame',
    'pygame.mixer',
    'pygame.display',
    'pygame.draw',
    'pygame.surface',
    'pygame.image',
    'pygame.font',
    'pygame.transform',
    # PIL for image processing
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'PIL.ImageDraw',
    'PIL.ImageFont',
    # Standard library modules
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
    'turtle',
    'webbrowser',
    'tempfile',
    'shutil',
    'zipfile',
    'tarfile',
    'configparser',
    # Language executors
    'core.interpreter',
    'core.languages.basic',
    'core.languages.pilot', 
    'core.languages.logo',
    'core.languages.python_executor',
    'core.languages.javascript_executor',
    'core.languages.perl',
    # Enhanced features
    'core.enhanced_error_handler',
    'core.framework',
    'core.features.tutorial_system',
    'core.features.ai_assistant',
    'core.features.gamification',
    # Hardware and IoT modules (optional)
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
    # GUI components
    'gui.components.multi_tab_editor',
    'gui.components.enhanced_graphics_canvas',
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
        # Windows-specific modules
        'win32api',
        'win32con',
        'win32gui',
        'winsound',
        # Linux-specific modules  
        'pwd',
        'grp',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove duplicate files
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Create macOS executable
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Time_Warp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disable UPX on macOS as it can cause issues with code signing
    console=False,  # GUI application
    disable_windowed_traceback=False,
    icon='assets/icon.icns' if os.path.exists('assets/icon.icns') else None,
)

# Create macOS app bundle
app = BUNDLE(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='Time_Warp.app',
    icon='assets/icon.icns' if os.path.exists('assets/icon.icns') else None,
    bundle_identifier='org.time-warp-ide.Time_Warp',
    version='1.2.0',
    info_plist={
        'CFBundleName': 'Time_Warp IDE',
        'CFBundleDisplayName': 'Time_Warp IDE',
        'CFBundleVersion': '1.2.0',
        'CFBundleShortVersionString': '1.2.0',
        'CFBundleIdentifier': 'org.time-warp-ide.Time_Warp',
        'CFBundleInfoDictionaryVersion': '6.0',
        'CFBundlePackageType': 'APPL',
        'CFBundleExecutable': 'Time_Warp',
        'CFBundleIconFile': 'icon.icns',
        'LSMinimumSystemVersion': '10.13.0',  # macOS High Sierra
        'LSApplicationCategoryType': 'public.app-category.education',
        'LSUIElement': False,
        'NSHighResolutionCapable': True,
        'NSSupportsAutomaticGraphicsSwitching': True,
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeExtensions': ['pilot'],
                'CFBundleTypeName': 'PILOT Program',
                'CFBundleTypeRole': 'Editor',
                'LSHandlerRank': 'Owner',
                'LSItemContentTypes': ['org.time-warp-ide.pilot-program'],
            },
            {
                'CFBundleTypeExtensions': ['bas'],
                'CFBundleTypeName': 'BASIC Program',
                'CFBundleTypeRole': 'Editor', 
                'LSHandlerRank': 'Owner',
                'LSItemContentTypes': ['org.time-warp-ide.basic-program'],
            },
            {
                'CFBundleTypeExtensions': ['logo'],
                'CFBundleTypeName': 'Logo Program',
                'CFBundleTypeRole': 'Editor',
                'LSHandlerRank': 'Owner', 
                'LSItemContentTypes': ['org.time-warp-ide.logo-program'],
            },
            {
                'CFBundleTypeExtensions': ['py'],
                'CFBundleTypeName': 'Python Program',
                'CFBundleTypeRole': 'Editor',
                'LSHandlerRank': 'Alternative',
                'LSItemContentTypes': ['public.python-script'],
            },
        ],
        'UTExportedTypeDeclarations': [
            {
                'UTTypeIdentifier': 'org.time-warp-ide.pilot-program',
                'UTTypeDescription': 'PILOT Program',
                'UTTypeConformsTo': ['public.text', 'public.source-code'],
                'UTTypeTagSpecification': {
                    'public.filename-extension': ['pilot'],
                    'public.mime-type': ['text/plain'],
                },
            },
            {
                'UTTypeIdentifier': 'org.time-warp-ide.basic-program',
                'UTTypeDescription': 'BASIC Program',
                'UTTypeConformsTo': ['public.text', 'public.source-code'],
                'UTTypeTagSpecification': {
                    'public.filename-extension': ['bas'],
                    'public.mime-type': ['text/plain'],
                },
            },
            {
                'UTTypeIdentifier': 'org.time-warp-ide.logo-program',
                'UTTypeDescription': 'Logo Program',
                'UTTypeConformsTo': ['public.text', 'public.source-code'],
                'UTTypeTagSpecification': {
                    'public.filename-extension': ['logo'],
                    'public.mime-type': ['text/plain'],
                },
            },
        ],
        'NSRequiresAquaSystemAppearance': False,  # Support dark mode
        'CFBundleSupportedPlatforms': ['MacOSX'],
        'DTPlatformName': 'macosx',
        'CFBundleGetInfoString': 'Time_Warp IDE 1.2.0 - Educational Programming Environment',
        'NSHumanReadableCopyright': 'Copyright © 2024 Time_Warp Development Team. All rights reserved.',
    },
)