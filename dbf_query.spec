# -*- mode: python ; coding: utf-8 -*-

import os
import sys
import site

# Obtener la ruta del entorno virtual
venv_path = os.path.join(os.path.dirname(sys.executable), 'Lib', 'site-packages')

# Obtener la ruta de pywin32
site_packages_path = site.getsitepackages()[0]
pywin32_path = os.path.join(site_packages_path, 'pywin32_system32')

a = Analysis(
    ['dbf_query.py'],
    pathex=['/c/Users/USER/Desktop/Soporte TI/fast_api_csr', venv_path],
    binaries=[],
    datas=[],
    hiddenimports=['win32com', 'win32com.client', 'pythoncom', 'win32timezone'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
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
    name='dbf_query',
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
    entitlements_file=None
)