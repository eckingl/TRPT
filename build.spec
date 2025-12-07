# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 打包配置
农业土壤普查报告生成系统

使用方法:
    pyinstaller build.spec

输出:
    dist/土壤普查报告系统.exe
"""

import sys
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(SPECPATH)
BACKEND_DIR = ROOT_DIR / 'backend'
FRONTEND_DIR = ROOT_DIR / 'frontend'
FRONTEND_DIST = FRONTEND_DIR / 'dist'

# 检查前端是否已构建
if not FRONTEND_DIST.exists():
    print("警告: 前端未构建，请先运行 'cd frontend && npm run build'")

block_cipher = None

# 收集数据文件
datas = [
    # 前端构建产物
    (str(FRONTEND_DIST), 'frontend/dist') if FRONTEND_DIST.exists() else None,
    # 后端模板文件（如果有）
    (str(BACKEND_DIR / 'templates'), 'templates') if (BACKEND_DIR / 'templates').exists() else None,
]
# 过滤掉 None
datas = [d for d in datas if d is not None]

# 隐藏导入（PyInstaller 可能无法自动检测的模块）
hiddenimports = [
    # FastAPI 相关
    'uvicorn',
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'fastapi',
    'starlette',
    'starlette.routing',
    'starlette.middleware',
    'starlette.middleware.cors',
    'starlette.staticfiles',
    # Pydantic
    'pydantic',
    'pydantic_settings',
    'pydantic.deprecated.decorator',
    # 数据处理
    'pandas',
    'numpy',
    'openpyxl',
    'openpyxl.cell._writer',
    # 图表
    'matplotlib',
    'matplotlib.backends.backend_agg',
    'matplotlib.figure',
    'matplotlib.pyplot',
    # Word 文档
    'docx',
    'docx.shared',
    'docx.enum.text',
    'docxtpl',
    # 数据库
    'aiosqlite',
    'sqlite3',
    # AI 客户端
    'openai',
    'dashscope',
    'httpx',
    # 工具库
    'pypinyin',
    'dotenv',
    # 编码
    'encodings',
    'encodings.utf_8',
    'encodings.gbk',
    'encodings.gb2312',
    # 应用模块
    'app',
    'app.main',
    'app.config',
    'app.api',
    'app.core',
    'app.models',
    'app.topics',
    'app.topics.attribute_map',
]

# 排除不需要的模块（减小体积）
excludes = [
    'tkinter',
    'tk',
    'tcl',
    'PyQt5',
    'PyQt6',
    'PySide2',
    'PySide6',
    'wx',
    'IPython',
    'jupyter',
    'notebook',
    'sphinx',
    'pytest',
    'mypy',
    'ruff',
]

a = Analysis(
    [str(ROOT_DIR / 'main.py')],
    pathex=[str(BACKEND_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='土壤普查报告系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 显示控制台窗口，方便调试
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以添加图标: icon='icon.ico'
)
