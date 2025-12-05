"""全局配置"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 应用信息
    APP_NAME: str = "农业土壤普查报告生成系统"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # 服务器配置
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # 路径配置
    BASE_DIR: Path = Path(__file__).parent.parent
    TEMPLATES_DIR: Path = BASE_DIR / "templates"
    OUTPUT_DIR: Path = BASE_DIR / "output"
    UPLOAD_DIR: Path = BASE_DIR / "uploads"

    # 文件配置
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
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
        # 确保目录存在
        self.TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """获取全局配置（单例模式）"""
    return Settings()
