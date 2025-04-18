#!/usr/bin/env python3
"""
自定义构建脚本，用于解决依赖问题并禁用代码签名
"""
import os
import sys
import shutil
import subprocess
import py2app.util

# 禁用代码签名
def dummy_codesign_adhoc(bundle):
    print(f"跳过代码签名: {bundle}")
    return True

py2app.util.codesign_adhoc = dummy_codesign_adhoc

# 清理之前的构建
if os.path.exists('build'):
    shutil.rmtree('build')
if os.path.exists('dist'):
    shutil.rmtree('dist')

# 首先，用最小的依赖构建应用程序
print("第一阶段：构建基本应用...")
setup_cmd = [
    sys.executable, 'setup.py', 'py2app', 
    '--semi-standalone',
    '--packages=PySide6,openai,PyPDF2,docx,pandas,numpy,PIL,certifi,httpx,anyio'
]
subprocess.run(setup_cmd, check=True)

# 然后，直接复制缺失的依赖到应用程序包中
print("\n第二阶段：复制额外的依赖...")
site_packages = os.path.join(os.path.dirname(os.__file__), 'site-packages')
app_resources = os.path.join('dist', 'Resume Matching App.app', 'Contents', 'Resources', 'lib', 'python3.13')

# 准备要复制的包列表
packages_to_copy = [
    'jaraco',
    'more_itertools',
    'autocommand',
    'setuptools',
    'pkg_resources',
]

# 复制包
for package in packages_to_copy:
    src = os.path.join(site_packages, package)
    dst = os.path.join(app_resources, package)
    
    if os.path.exists(src):
        print(f"复制 {package}...")
        if os.path.isdir(src):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
    else:
        print(f"警告: 找不到包 {package}")

print("\n构建完成！")
print("应用程序已生成在 dist/Resume Matching App.app") 