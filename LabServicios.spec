# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('token.txt', '.'), ('config.py', '.'), ('styles.py', '.')],
    hiddenimports=['PIL', 'PIL.Image', 'PIL.ImageTk', 'reportlab', 'reportlab.pdfgen', 'requests', 'urllib3', 'tkinter', 'tkinter.ttk', 'main_app', 'login_window', 'auth_manager', 'api_client'],
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
    name='LabServicios',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=['vcruntime140.dll'],
    runtime_tmpdir='.',
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
