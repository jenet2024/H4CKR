# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file — H4CKR
# Build : pyinstaller build.spec

import os
from pathlib import Path

BASE = Path(".").resolve()

a = Analysis(
    ["main.py"],
    pathex=[str(BASE)],
    binaries=[],
    datas=[
        ("src/assets/videos",  "src/assets/videos"),
        ("src/assets/enigmas", "src/assets/enigmas"),
        ("src/assets/audio",   "src/assets/audio"),
        ("src/assets/images",  "src/assets/images"),
        (".env",               "."),
    ],
    hiddenimports=[
        "pygame",
        "pyttsx3",
        "pyttsx3.drivers",
        "pyttsx3.drivers.sapi5",
        "requests",
        "PIL",
        "dotenv",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="H4CKR",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # Pas de console noire
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,              # Ajoutez "src/assets/images/icon.ico" si vous avez une icône
)
