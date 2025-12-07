@echo off
chcp 65001 >nul
title 农业土壤普查报告生成系统 - 开发模式

echo ================================================
echo   农业土壤普查报告生成系统 - 开发模式
echo   Development Mode (Frontend + Backend)
echo ================================================
echo.

REM 检查 Python
echo [检查] 正在检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python！
    pause
    exit /b 1
)
python --version

REM 检查 Node.js
echo [检查] 正在检查 Node.js 环境...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Node.js！
    echo 开发模式需要 Node.js，请先安装: https://nodejs.org/
    pause
    exit /b 1
)
node --version
echo.

REM 检查并安装后端依赖
echo [检查] 正在检查后端依赖...
cd /d "%~dp0backend"
python -c "import fastapi, uvicorn" >nul 2>&1
if %errorlevel% neq 0 (
    echo [安装] 正在安装后端依赖...
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [错误] 后端依赖安装失败！
        pause
        exit /b 1
    )
    echo [完成] 后端依赖安装完成
)
echo.

REM 检查并安装前端依赖
echo [检查] 正在检查前端依赖...
cd /d "%~dp0frontend"
if not exist "node_modules\" (
    echo [安装] 正在安装前端依赖（首次运行需要较长时间）...
    call npm install
    if %errorlevel% neq 0 (
        echo [错误] 前端依赖安装失败！
        pause
        exit /b 1
    )
    echo [完成] 前端依赖安装完成
)
echo.

REM 返回根目录
cd /d "%~dp0"

echo ================================================
echo [启动] 开发模式启动中...
echo ================================================
echo.
echo 后端服务: http://127.0.0.1:8000
echo 后端文档: http://127.0.0.1:8000/docs
echo 前端服务: http://localhost:5173
echo.
echo 前端自动代理后端 API 请求到 http://127.0.0.1:8000
echo.
echo 按 Ctrl+C 停止所有服务
echo ================================================
echo.

REM 启动后端服务（新窗口，不最小化以便查看日志）
echo [启动] 正在启动后端服务...
start "后端服务 - FastAPI" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

REM 等待后端启动
echo [等待] 后端服务启动中...
timeout /t 5 /nobreak >nul

REM 检查后端是否启动成功
echo [检查] 验证后端服务...
curl -s http://127.0.0.1:8000/api/health >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 后端服务可能未完全启动，请稍等...
    timeout /t 3 /nobreak >nul
)

REM 启动前端服务（当前窗口）
echo [启动] 前端服务启动中...
echo.
cd /d "%~dp0frontend"
call npm run dev

REM 如果前端退出，提示用户
echo.
echo [提示] 前端服务已停止
echo.
pause
