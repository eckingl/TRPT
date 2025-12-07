@echo off
chcp 65001 >nul
title 打包土壤普查报告系统

echo ========================================
echo   土壤普查报告系统 - 打包脚本
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] 检查 Python 环境...
python --version
if errorlevel 1 (
    echo 错误: 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

echo.
echo [2/4] 构建前端...
cd frontend
if not exist "node_modules" (
    echo 安装前端依赖...
    call npm install
)
echo 构建前端...
call npm run build
if errorlevel 1 (
    echo 错误: 前端构建失败
    pause
    exit /b 1
)
cd ..

echo.
echo [3/4] 安装打包依赖...
pip install pyinstaller -q

echo.
echo [4/4] 开始打包...
pyinstaller build.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo 错误: 打包失败，请检查错误信息
    pause
    exit /b 1
)

echo.
echo ========================================
echo   打包完成!
echo   输出文件: dist\土壤普查报告系统.exe
echo ========================================
echo.

pause
