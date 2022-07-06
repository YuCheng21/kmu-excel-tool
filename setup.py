import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    'include_files': [
        'ui/',
        'input/',
    ],
    "excludes": [],
}

# base="Win32GUI" should be used only for Windows GUI app
base = None
if sys.platform == "win32":
    base = "Win32GUI"

target = Executable(
    script='app.py',
    base=base,
    icon='ui/favicon.ico'
)

setup(
    name='KMU_SCBC',
    version='1.0',
    description='乳癌副作用轉換工具',
    author='Thomas Feng',
    options={'build_exe': build_exe_options},
    executables=[target]
)
