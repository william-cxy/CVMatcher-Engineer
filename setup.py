"""
This is a setup.py script generated for Resume Matching App
"""
# 禁用代码签名
import py2app.util

def dummy_codesign_adhoc(bundle):
    print(f"跳过代码签名: {bundle}")
    return True

py2app.util.codesign_adhoc = dummy_codesign_adhoc

from setuptools import setup

APP = ['resume_matching_app_pyside6.py']
DATA_FILES = [
    ('', ['settings.json', 'job_history.json']),
]
OPTIONS = {
    'argv_emulation': False,
    'packages': [
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'openai',
        'PyPDF2',
        'docx',
        'pandas.core',
        'pandas.io.parsers',
        'pandas.io.formats',
        'PIL',
    ],
    'includes': [
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
        'scipy',
        'sklearn',
        'pytest',
        'notebook',
        'IPython',
        'jupyter',
        'setuptools',
        'wheel',
        'pkg_resources',
        'distutils',
        'site',
        'unittest',
        'pydoc',
        'email',
        'html',
        'http',
        'xml',
        'logging',
        'pandas.tests',
        'pandas.plotting',
        'pandas.tseries',
        'pandas.arrays',
        'pandas.api',
        'numpy.distutils',
        'numpy.testing',
        'numpy.f2py',
        'numpy.core.tests',
        'numpy.lib.tests',
        'numpy.linalg.tests',
        'numpy.random.tests',
        'PySide6.Qt3D*',
        'PySide6.QtBluetooth*',
        'PySide6.QtCharts*',
        'PySide6.QtConcurrent*',
        'PySide6.QtDataVisualization*',
        'PySide6.QtDesigner*',
        'PySide6.QtHelp*',
        'PySide6.QtLocation*',
        'PySide6.QtMultimedia*',
        'PySide6.QtNetwork*',
        'PySide6.QtNfc*',
        'PySide6.QtOpenGL*',
        'PySide6.QtPositioning*',
        'PySide6.QtPrintSupport*',
        'PySide6.QtQml*',
        'PySide6.QtQuick*',
        'PySide6.QtRemoteObjects*',
        'PySide6.QtSensors*',
        'PySide6.QtSerialPort*',
        'PySide6.QtSql*',
        'PySide6.QtSvg*',
        'PySide6.QtTest*',
        'PySide6.QtUiTools*',
        'PySide6.QtWebChannel*',
        'PySide6.QtWebEngine*',
        'PySide6.QtWebSockets*',
        'PySide6.QtXml*',
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
    'strip': True,
    'arch': 'universal2',
    'optimize': 2,
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
        'Pillow',
    ],
) 