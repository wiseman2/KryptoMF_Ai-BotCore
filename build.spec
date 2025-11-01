# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for KryptoMF Bot

This creates a standalone executable that users can download and run
without needing Python installed.

Build commands:
    # CLI only (open source)
    pyinstaller build.spec

    # With GUI (premium)
    pyinstaller build_gui.spec
"""

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config/example_config.yaml', 'config'),
        ('README.md', '.'),
        ('QUICKSTART.md', '.'),
    ],
    hiddenimports=[
        'ccxt',
        'keyring',
        'keyring.backends',
        'keyring.backends.Windows',
        'keyring.backends.macOS',
        'keyring.backends.SecretService',
        'colorama',
        'yaml',
        'pandas',
        'numpy',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PySide6',  # Exclude GUI for CLI build
        'PyQt6',
        'tkinter',
        'matplotlib',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='KryptoMF-Bot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # CLI mode
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # TODO: Add icon
)

