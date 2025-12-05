"""专题基类"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar

import pandas as pd


class BaseTopic(ABC):
    """专题基类，所有专题必须继承此类"""

    topic_id: ClassVar[str] = ""
    topic_name: ClassVar[str] = ""

    def __init__(self, data: pd.DataFrame, config: dict) -> None:
        """初始化专题

        Args:
            data: 输入数据 DataFrame
            config: 专题配置
        """
        self.data = data
        self.config = config
        self.charts: list[Path] = []
        self.context: dict = {}

    @abstractmethod
    def process_data(self) -> dict:
        """处理数据，返回统计结果

        Returns:
            统计结果字典
        """
        raise NotImplementedError

    @abstractmethod
    def generate_charts(self, output_dir: Path) -> list[Path]:
        """生成图表

        Args:
            output_dir: 图表输出目录

        Returns:
            生成的图表文件路径列表
        """
        raise NotImplementedError

    @abstractmethod
    def generate_report(self, template_path: Path, output_path: Path) -> Path:
        """生成报告

        Args:
            template_path: Word 模板路径
            output_path: 输出报告路径

        Returns:
            生成的报告文件路径
        """
        raise NotImplementedError

    def run(self, output_dir: Path) -> Path:
        """执行完整的报告生成流程

        Args:
            output_dir: 输出目录

        Returns:
            生成的报告文件路径
        """
        self.context = self.process_data()
        self.charts = self.generate_charts(output_dir / "charts")

        template_path = self.get_template_path()
        report_path = output_dir / f"{self.topic_id}_report.docx"

        return self.generate_report(template_path, report_path)

    @classmethod
    def get_template_path(cls) -> Path:
        """获取模板路径"""
        from app.config import get_settings

        settings = get_settings()
        return settings.TEMPLATES_DIR / f"{cls.topic_id}.docx"
