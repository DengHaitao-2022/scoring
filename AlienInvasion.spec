# AlienInvasion.spec

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['alien_invasion.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('images/*', 'images'),  # 包含 images 文件夹中的所有文件
        ('SimHei.ttf', '.'),     # 包含 SimHei.ttf 文件
        ('bj.mp3', '.'),         # 包含 bj.mp3 文件
        ('ship_hit.mp3', '.')    # 包含 ship_hit 文件
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AlienInvasion',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 设置为 False 以隐藏控制台窗口
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AlienInvasion',
)