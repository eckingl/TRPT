"""
农业土壤普查报告生成系统 - 启动入口

使用方法:
    python main.py

启动后会自动打开浏览器访问 http://127.0.0.1:8000
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path


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
    requirements_path = Path(__file__).parent / "backend" / "requirements.txt"
    print("正在安装依赖...")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-r", str(requirements_path)]
    )


def start_server() -> None:
    """启动服务器"""
    import uvicorn

    # 添加 backend 目录到 Python 路径
    backend_path = Path(__file__).parent / "backend"
    sys.path.insert(0, str(backend_path))

    from app.config import get_settings

    settings = get_settings()

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
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )


def main() -> None:
    """主入口"""
    print("=" * 50)
    print("  农业数据处理系统")
    print("=" * 50)

    if not check_dependencies():
        print("\n[警告] 检测到缺少依赖，正在安装...")
        install_dependencies()
        print("[完成] 依赖安装完成")

    print("\n[启动] 正在启动服务器...")
    start_server()


if __name__ == "__main__":
    main()
