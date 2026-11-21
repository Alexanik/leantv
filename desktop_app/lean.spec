# -*- mode: python ; coding: utf-8 -*-
import sys
import os

datas = [('resources/lean_home.apk', 'resources')]
binaries = []

if sys.platform == "darwin":
    if os.path.exists('resources/bin/macos/adb'):
        binaries.append(('resources/bin/macos/adb', 'resources'))
    elif os.path.exists('resources/adb'):
        binaries.append(('resources/adb', 'resources'))
elif sys.platform == "win32":
    if os.path.exists('resources/bin/windows/adb.exe'):
        binaries.append(('resources/bin/windows/adb.exe', 'resources'))
        binaries.append(('resources/bin/windows/AdbWinApi.dll', 'resources'))
        binaries.append(('resources/bin/windows/AdbWinUsbApi.dll', 'resources'))
else:
    if os.path.exists('resources/bin/linux/adb'):
        binaries.append(('resources/bin/linux/adb', 'resources'))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
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
    a.binaries,
    a.datas,
    [],
    name='lean',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
