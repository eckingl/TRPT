@echo off
chcp 65001 >nul
title 停止服务 - 农业土壤普查报告生成系统

echo ================================================
echo   停止服务
echo ================================================
echo.

echo [检查] 正在检查运行中的服务...
echo.

REM 检查端口 8000 (后端)
netstat -ano | findstr ":8000" >nul 2>&1
if %errorlevel% equ 0 (
    echo [发现] 后端服务正在运行（端口 8000）
    echo [操作] 正在停止后端服务...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000"') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    echo [完成] 后端服务已停止
    echo.
) else (
    echo [提示] 未检测到后端服务运行
    echo.
)

REM 检查端口 5173 (前端)
netstat -ano | findstr ":5173" >nul 2>&1
if %errorlevel% equ 0 (
    echo [发现] 前端服务正在运行（端口 5173）
    echo [操作] 正在停止前端服务...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173"') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    echo [完成] 前端服务已停止
    echo.
) else (
    echo [提示] 未检测到前端服务运行
    echo.
)

REM 额外检查 Python 和 Node 进程（可选）
echo [检查] 正在检查相关进程...
tasklist | findstr /i "python.exe uvicorn" >nul 2>&1
if %errorlevel% equ 0 (
    echo [警告] 检测到其他 Python 进程，可能包含系统服务
)

tasklist | findstr /i "node.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo [警告] 检测到其他 Node.js 进程，可能包含前端服务
)

echo.
echo ================================================
echo [完成] 服务已全部停止
echo ================================================
echo.
pause
