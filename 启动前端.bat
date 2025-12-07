@echo off
chcp 65001 >nul
title 前端服务 - Vite

echo ================================================
echo   农业土壤普查报告生成系统 - 前端服务
echo ================================================
echo.

cd /d "%~dp0frontend"

echo [启动] 前端服务启动中...
echo 访问地址: http://localhost:5173
echo.
echo 按 Ctrl+C 停止服务
echo ================================================
echo.

npm run dev

if %errorlevel% neq 0 (
    echo.
    echo [错误] 启动失败！请检查错误信息。
    pause
)
