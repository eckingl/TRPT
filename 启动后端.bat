@echo off
chcp 65001 >nul
title 后端服务 - FastAPI

echo ================================================
echo   农业土壤普查报告生成系统 - 后端服务
echo ================================================
echo.

cd /d "%~dp0backend"

echo [启动] 后端服务启动中...
echo 访问地址: http://127.0.0.1:8000
echo API 文档: http://127.0.0.1:8000/docs
echo.
echo 按 Ctrl+C 停止服务
echo ================================================
echo.

python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

if %errorlevel% neq 0 (
    echo.
    echo [错误] 启动失败！请检查错误信息。
    pause
)
