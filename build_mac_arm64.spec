# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['resume_matching_app_pyside6.py'],
    pathex=[],
    binaries=[],
    datas=[('settings.json', '.')],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtNetwork',
        'openai',
        'PyPDF2',
        'docx',
        'pandas',
        'openpyxl'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'tkinter', 'scipy.spatial.cKDTree',
        'scipy.special._ellip_harm_2', 'scipy.special._ufuncs',
        'scipy.sparse.csgraph', 'scipy.stats._stats',
        'PIL.ImageQt', 'PyQt5', 'PyQt6', 'IPython'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    target_arch='arm64'
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='简历匹配分析工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch='arm64',
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='简历匹配分析工具.app',
    info_plist={
        'NSHighResolutionCapable': 'True',
        'CFBundleIdentifier': 'com.williamcxy.cvmatcher',
        'CFBundleName': '简历匹配分析工具',
        'CFBundleDisplayName': '简历匹配分析工具',
        'CFBundleVersion': '1.0.0',
        'LSMinimumSystemVersion': '11.0',
        'NSAppleArchitecturePriority': ['arm64'],
    },
) 