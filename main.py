"""
农业土壤普查报告生成系统 - 启动入口

使用方法:
    python main.py

启动后会自动打开浏览器访问 http://127.0.0.1:8000
"""

import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path


def get_base_path() -> Path:
    """获取基础路径（支持打包后运行）"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后的路径
        return Path(sys._MEIPASS)
    else:
        # 开发环境路径
        return Path(__file__).parent


def get_app_path() -> Path:
    """获取应用数据路径（用于存储上传文件、数据库等）"""
    if getattr(sys, 'frozen', False):
        # 打包后使用 exe 所在目录
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent


def check_dependencies() -> bool:
    """检查依赖是否安装"""
    try:
        import fastapi  # noqa: F401
        import uvicorn  # noqa: F401

        return True
    except ImportError:
        return False


def install_dependencies() -> None:
    """安装依赖"""
    requirements_path = get_base_path() / "backend" / "requirements.txt"
    if requirements_path.exists():
        print("正在安装依赖...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_path)]
        )


def setup_environment() -> None:
    """设置运行环境"""
    base_path = get_base_path()
    app_path = get_app_path()

    # 添加 backend 目录到 Python 路径
    backend_path = base_path / "backend"
    if backend_path.exists():
        sys.path.insert(0, str(backend_path))

    # 设置环境变量
    os.environ["SOIL_REPORT_BASE_DIR"] = str(app_path / "backend")

    # 确保必要目录存在
    for dir_name in ["uploads", "output", "data", "templates"]:
        (app_path / "backend" / dir_name).mkdir(parents=True, exist_ok=True)


def start_server() -> None:
    """启动服务器"""
    import uvicorn

    setup_environment()

    from app.config import get_settings

    settings = get_settings()

    # 打包模式下禁用热重载
    is_frozen = getattr(sys, 'frozen', False)
    reload_enabled = settings.DEBUG and not is_frozen

    # 延迟打开浏览器
    def open_browser() -> None:
        time.sleep(1.5)
        url = f"http://{settings.HOST}:{settings.PORT}"
        print(f"\n[浏览器] 正在打开: {url}")
        webbrowser.open(url)

    import threading

    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()

    # 启动服务器
    if is_frozen:
        # 打包模式：直接导入 app
        from app.main import app
        uvicorn.run(
            app,
            host=settings.HOST,
            port=settings.PORT,
            reload=False,
        )
    else:
        # 开发模式：使用模块字符串
        uvicorn.run(
            "app.main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=reload_enabled,
        )


def main() -> None:
    """主入口"""
    print("=" * 50)
    print("  农业土壤普查报告生成系统")
    print("=" * 50)

    is_frozen = getattr(sys, 'frozen', False)

    if not is_frozen and not check_dependencies():
        print("\n[警告] 检测到缺少依赖，正在安装...")
        install_dependencies()
        print("[完成] 依赖安装完成")

    print("\n[启动] 正在启动服务器...")
    start_server()


if __name__ == "__main__":
    main()
