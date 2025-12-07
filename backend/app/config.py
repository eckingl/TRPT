"""全局配置"""

import os
import sys
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


def get_base_dir() -> Path:
    """获取基础目录（支持打包后运行）"""
    # 优先使用环境变量（由 main.py 设置）
    env_base = os.environ.get("SOIL_REPORT_BASE_DIR")
    if env_base:
        return Path(env_base)

    # 打包模式
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent / "backend"

    # 开发模式
    return Path(__file__).parent.parent


class Settings(BaseSettings):
    """应用配置"""

    # 应用信息
    APP_NAME: str = "农业土壤普查报告生成系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False  # 打包后默认关闭调试模式

    # 服务器配置
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # 路径配置（动态获取）
    BASE_DIR: Path = get_base_dir()
    TEMPLATES_DIR: Path = BASE_DIR / "templates"
    OUTPUT_DIR: Path = BASE_DIR / "output"
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    DATA_DIR: Path = BASE_DIR / "data"

    # 文件配置
    MAX_UPLOAD_SIZE: int = 1024 * 1024 * 1024  # 1GB (支持大文件上传)
    ALLOWED_EXTENSIONS: set[str] = {".csv", ".xlsx", ".xls"}

    # 项目配置文件路径
    PROJECT_CONFIG_PATH: Path | None = None

    model_config = {
        "env_prefix": "SOIL_REPORT_",
        "env_file": ".env",
        "extra": "ignore",
    }

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        # 重新计算路径（确保使用正确的 BASE_DIR）
        self.BASE_DIR = get_base_dir()
        self.TEMPLATES_DIR = self.BASE_DIR / "templates"
        self.OUTPUT_DIR = self.BASE_DIR / "output"
        self.UPLOAD_DIR = self.BASE_DIR / "uploads"
        self.DATA_DIR = self.BASE_DIR / "data"

        # 确保目录存在
        self.TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """获取全局配置（单例模式）"""
    return Settings()
