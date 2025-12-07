@echo off
chcp 65001 >nul
title 系统诊断 - 农业土壤普查报告生成系统

echo ================================================
echo   系统诊断工具
echo   System Diagnostic Tool
echo ================================================
echo.

REM 1. Python 环境检查
echo [1/7] 检查 Python 环境
echo ----------------------------------------
python --version 2>nul
if %errorlevel% neq 0 (
    echo ❌ Python 未安装
    set PYTHON_OK=0
) else (
    echo ✓ Python 已安装
    set PYTHON_OK=1
)
echo.

REM 2. Node.js 环境检查
echo [2/7] 检查 Node.js 环境
echo ----------------------------------------
node --version 2>nul
if %errorlevel% neq 0 (
    echo ❌ Node.js 未安装
    set NODE_OK=0
) else (
    echo ✓ Node.js 已安装
    npm --version 2>nul
    set NODE_OK=1
)
echo.

REM 3. 后端依赖检查
echo [3/7] 检查后端依赖
echo ----------------------------------------
cd /d "%~dp0backend"
if not exist "requirements.txt" (
    echo ❌ requirements.txt 不存在
) else (
    echo ✓ requirements.txt 存在
    if %PYTHON_OK% equ 1 (
        python -c "import fastapi" 2>nul
        if %errorlevel% neq 0 (
            echo ❌ FastAPI 未安装
        ) else (
            echo ✓ FastAPI 已安装
        )

        python -c "import uvicorn" 2>nul
        if %errorlevel% neq 0 (
            echo ❌ Uvicorn 未安装
        ) else (
            echo ✓ Uvicorn 已安装
        )

        python -c "import pandas" 2>nul
        if %errorlevel% neq 0 (
            echo ❌ Pandas 未安装
        ) else (
            echo ✓ Pandas 已安装
        )
    )
)
echo.

REM 4. 前端依赖检查
echo [4/7] 检查前端依赖
echo ----------------------------------------
cd /d "%~dp0frontend"
if not exist "package.json" (
    echo ❌ package.json 不存在
) else (
    echo ✓ package.json 存在
    if exist "node_modules\" (
        echo ✓ node_modules 存在
    ) else (
        echo ❌ node_modules 不存在（需要运行 npm install）
    )
)
echo.

REM 5. 端口占用检查
echo [5/7] 检查端口占用
echo ----------------------------------------
netstat -ano | findstr ":8000" >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠ 端口 8000 已被占用
) else (
    echo ✓ 端口 8000 可用
)

netstat -ano | findstr ":5173" >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠ 端口 5173 已被占用
) else (
    echo ✓ 端口 5173 可用
)
echo.

REM 6. 数据库检查
echo [6/7] 检查数据库
echo ----------------------------------------
cd /d "%~dp0backend"
if exist "data\projects.db" (
    echo ✓ 数据库文件存在
) else (
    echo ⚠ 数据库文件不存在（首次运行时会自动创建）
)
echo.

REM 7. 目录结构检查
echo [7/7] 检查目录结构
echo ----------------------------------------
cd /d "%~dp0"
if exist "backend\" (
    echo ✓ backend 目录存在
) else (
    echo ❌ backend 目录不存在
)

if exist "frontend\" (
    echo ✓ frontend 目录存在
) else (
    echo ❌ frontend 目录不存在
)

if exist "main.py" (
    echo ✓ main.py 存在
) else (
    echo ❌ main.py 不存在
)
echo.

REM 总结
echo ================================================
echo   诊断完成
echo ================================================
echo.
echo 如果发现问题，请根据提示安装相应的依赖：
echo.
echo   - Python: https://www.python.org/downloads/
echo   - Node.js: https://nodejs.org/
echo   - 后端依赖: cd backend ^&^& pip install -r requirements.txt
echo   - 前端依赖: cd frontend ^&^& npm install
echo.
pause
