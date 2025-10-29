# -*- mode: python ; coding: utf-8 -*-
import sys


a = Analysis(
    ['POsaver.py'],
    pathex=[],
    binaries=[],
    datas=[('share.png', '.'), ('layout.css', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

# Build the main executable. On macOS we'll also wrap this into a .app bundle below.
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='POsaver',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    # On macOS a GUI app typically should set console=False; keep console=True here
    # so the build works for CLI use too. The BUNDLE below will set GUI semantics if needed.
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# On macOS, create a .app bundle so the CI can upload a .app for end users.
if sys.platform == 'darwin':
    try:
        # BUNDLE wraps the produced exe into a macOS .app bundle
        app = BUNDLE(
            exe,
            name='POsaver.app',
            icon=None,
            bundle_identifier=None,
        )
    except Exception:
        # If BUNDLE isn't available or fails, fallback to leaving the EXE in dist/
        pass
