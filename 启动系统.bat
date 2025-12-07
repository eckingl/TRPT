@echo off
chcp 65001 >nul
title 农业土壤普查报告生成系统 - 启动器

echo ================================================
echo   农业土壤普查报告生成系统
echo   Soil Survey Report Generation System
echo ================================================
echo.

REM 检查 Python 是否安装
echo [检查] 正在检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python！
    echo.
    echo 请先安装 Python 3.11 或更高版本
    echo 下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

python --version
echo.

REM 检查 Node.js 是否安装（用于前端开发）
echo [检查] 正在检查 Node.js 环境...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 未检测到 Node.js（前端开发模式需要）
    echo 如需前端开发，请安装 Node.js: https://nodejs.org/
    echo.
) else (
    node --version
    echo.
)

REM 检查端口占用
echo [检查] 正在检查端口占用情况...
netstat -ano | findstr ":8000" >nul 2>&1
if %errorlevel% equ 0 (
    echo [警告] 端口 8000 已被占用！
    echo.
    echo 请选择操作:
    echo   1. 结束占用进程并继续启动
    echo   2. 退出
    echo.
    choice /c 12 /n /m "请输入选择 (1 或 2): "
    if errorlevel 2 exit /b 0
    if errorlevel 1 (
        echo [操作] 正在结束占用端口 8000 的进程...
        for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000"') do (
            taskkill /F /PID %%a >nul 2>&1
        )
        echo [完成] 进程已结束
        echo.
    )
)

REM 检查后端依赖
echo [检查] 正在检查后端依赖...
cd /d "%~dp0backend"
if not exist "requirements.txt" (
    echo [错误] 未找到 requirements.txt 文件！
    pause
    exit /b 1
)

python -c "import fastapi, uvicorn" >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 检测到缺少依赖，正在安装...
    echo.
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [错误] 依赖安装失败！
        pause
        exit /b 1
    )
    echo.
    echo [完成] 依赖安装完成
    echo.
)

REM 返回根目录
cd /d "%~dp0"

REM 启动系统
echo ================================================
echo [启动] 正在启动系统...
echo ================================================
echo.
echo 系统将在 1.5 秒后自动打开浏览器
echo 访问地址: http://127.0.0.1:8000
echo.
echo 按 Ctrl+C 停止服务器
echo ================================================
echo.

REM 使用 Python 启动
python main.py

REM 如果启动失败
if %errorlevel% neq 0 (
    echo.
    echo [错误] 系统启动失败！
    echo.
    pause
    exit /b 1
)
