#!/usr/bin/env python3
"""
自定义构建脚本，绕过代码签名步骤
"""
import os
import sys
import subprocess
import shutil
import tempfile

# 清理先前的构建
if os.path.exists('build'):
    shutil.rmtree('build')
if os.path.exists('dist'):
    shutil.rmtree('dist')

# 创建一个临时的setup.py文件
setup_content = """
from setuptools import setup

APP = ['resume_matching_app_pyside6.py']
DATA_FILES = [
    ('', ['settings.json', 'job_history.json']),
]
OPTIONS = {
    'argv_emulation': False,
    'packages': [
        'PySide6',
        'openai',
        'PyPDF2',
        'docx',
        'pandas',
        'numpy',
        'PIL',
        'certifi',
        'httpx',
        'anyio',
    ],
    'includes': [
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'json',
        'os',
        'sys',
        'threading',
        'datetime',
    ],
    'excludes': [
        'matplotlib',
        'tkinter',
        'PyInstaller',
        'pip',
    ],
    'plist': {
        'CFBundleName': 'Resume Matching App',
        'CFBundleDisplayName': 'Resume Matching App',
        'CFBundleIdentifier': 'com.resumematcher.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'LSMinimumSystemVersion': '10.13',
        'NSPrincipalClass': 'NSApplication',
    },
    'strip': False,
    'arch': 'universal2',
    'optimize': 0,
    'iconfile': 'icon.icns',
}

setup(
    name='Resume Matching App',
    version='1.0.0',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=[
        'PySide6',
        'openai',
        'PyPDF2',
        'python-docx',
        'pandas',
        'pillow',
    ],
)
"""

# 创建猴子补丁文件，替换codesign_adhoc函数
monkey_patch = """
# 猴子补丁，禁用代码签名
import py2app.util
original_codesign_adhoc = py2app.util.codesign_adhoc

def dummy_codesign_adhoc(bundle):
    print(f"跳过代码签名: {bundle}")
    return True

py2app.util.codesign_adhoc = dummy_codesign_adhoc
"""

print("开始构建应用...")

# 创建临时补丁文件
with open('monkey_patch.py', 'w') as f:
    f.write(monkey_patch)

# 创建临时setup文件
with open('temp_setup.py', 'w') as f:
    f.write(setup_content)

try:
    # 运行打包命令，使用猴子补丁禁用代码签名
    cmd = [
        sys.executable, "-c",
        f"import monkey_patch; exec(open('temp_setup.py').read()); import sys; sys.argv = ['setup.py', 'py2app', '--semi-standalone']; from setuptools import setup"
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    
    print("构建完成！应用程序位于dist目录。")
except subprocess.CalledProcessError as e:
    print(f"构建失败: {e}")
    sys.exit(1)
finally:
    # 清理临时文件
    if os.path.exists('temp_setup.py'):
        os.remove('temp_setup.py')
    if os.path.exists('monkey_patch.py'):
        os.remove('monkey_patch.py')