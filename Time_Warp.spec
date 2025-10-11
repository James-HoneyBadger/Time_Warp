# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['Time_Warp.py'],
    pathex=[],
    binaries=[],
    datas=[('core', 'core'), ('tools', 'tools'), ('examples', 'examples')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Time_Warp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Time_Warp',
)
app = BUNDLE(
    coll,
    name='Time_Warp.app',
    icon=None,
    bundle_identifier=None,
)
