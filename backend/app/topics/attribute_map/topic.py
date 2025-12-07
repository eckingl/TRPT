"""属性图专题类

实现属性图专题的完整报告生成流程
"""

from pathlib import Path
from typing import ClassVar

import pandas as pd

from app.topics import register_topic
from app.topics.attribute_map.config import (
    detect_available_attributes,
    get_grade_order,
)
from app.topics.attribute_map.generate import (
    ReportConfig,
    generate_multi_attribute_report,
    generate_single_attribute_reports,
)
from app.topics.attribute_map.stats import AttributeStats, compute_attribute_stats
from app.topics.base import BaseTopic


@register_topic
class AttributeMapTopic(BaseTopic):
    """属性图专题

    用于生成土壤属性分析报告，支持单属性报告和综合报告
    """

    topic_id: ClassVar[str] = "attribute_map"
    topic_name: ClassVar[str] = "属性图"

    def __init__(self, data: pd.DataFrame, config: dict) -> None:
        """初始化属性图专题

        Args:
            data: 输入数据 DataFrame
            config: 专题配置，包含：
                - region_name: 地区名称
                - survey_year: 调查年份
                - use_ai: 是否使用 AI 生成分析
                - ai_provider: AI 提供商 (qwen/deepseek)
                - report_mode: 报告模式 (single/multi/both)
                - attributes: 要分析的属性列表（可选）
        """
        super().__init__(data, config)
        self.stats_list: list[AttributeStats] = []
        self.available_attrs: list[tuple[str, str]] = []

    def process_data(self) -> dict:
        """处理数据，计算各属性统计

        Returns:
            统计结果字典
        """
        # 检测可用属性
        self.available_attrs = detect_available_attributes(list(self.data.columns))

        if not self.available_attrs:
            return {"error": "未找到可用的土壤属性列"}

        # 如果配置中指定了属性，则过滤
        selected_attrs = self.config.get("attributes")
        if selected_attrs:
            self.available_attrs = [
                (orig, key)
                for orig, key in self.available_attrs
                if key in selected_attrs
            ]

        # 计算各属性统计
        self.stats_list = []
        for orig_col, attr_key in self.available_attrs:
            df_proc = self.data.copy()

            # 重命名列
            if orig_col != attr_key and orig_col in df_proc.columns:
                df_proc = df_proc.rename(columns={orig_col: attr_key})

            # 转换为数值
            df_proc[attr_key] = pd.to_numeric(df_proc[attr_key], errors="coerce")

            # 检查是否有有效数据
            if (df_proc[attr_key] > 0).sum() == 0:
                continue

            # 获取等级顺序
            grade_order = get_grade_order(attr_key)

            # 如果没有面积列，添加模拟面积
            if "面积" not in df_proc.columns:
                df_proc["面积"] = 1.0

            # 计算统计
            stats = compute_attribute_stats(df_proc, df_proc, attr_key, grade_order)
            self.stats_list.append(stats)

        return {
            "available_attrs": len(self.available_attrs),
            "processed_attrs": len(self.stats_list),
            "attr_names": [s.attr_name for s in self.stats_list],
        }

    def generate_charts(self, output_dir: Path) -> list[Path]:
        """生成图表

        图表在报告生成过程中内嵌生成，此方法返回空列表
        """
        return []

    def generate_report(self, template_path: Path, output_path: Path) -> Path:
        """生成报告

        Args:
            template_path: Word 模板路径（未使用，使用内置生成）
            output_path: 输出报告路径

        Returns:
            生成的报告文件路径
        """
        if not self.stats_list:
            raise ValueError("没有可用的统计数据，请先调用 process_data()")

        # 构建报告配置
        report_config = ReportConfig(
            region_name=self.config.get("region_name", "XX县"),
            survey_year=self.config.get("survey_year", 2024),
            theme=self.config.get("theme", "professional"),
            use_ai=self.config.get("use_ai", False),
            ai_provider=self.config.get("ai_provider"),
        )

        report_mode = self.config.get("report_mode", "multi")
        output_dir = output_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)

        if report_mode == "single":
            # 生成单属性报告
            results = generate_single_attribute_reports(
                self.stats_list, report_config, output_dir
            )
            # 返回第一个报告的路径
            if results:
                return output_dir / results[0][0]
            raise ValueError("未能生成任何报告")

        elif report_mode == "both":
            # 同时生成单属性和综合报告
            generate_single_attribute_reports(self.stats_list, report_config, output_dir)
            generate_multi_attribute_report(
                self.stats_list, report_config, output_path
            )
            return output_path

        else:  # multi (默认)
            # 生成综合报告
            generate_multi_attribute_report(
                self.stats_list, report_config, output_path
            )
            return output_path

    def run(self, output_dir: Path) -> Path:
        """执行完整的报告生成流程

        Args:
            output_dir: 输出目录

        Returns:
            生成的报告文件路径
        """
        self.context = self.process_data()

        if "error" in self.context:
            raise ValueError(self.context["error"])

        report_path = output_dir / f"{self.topic_id}_report.docx"
        return self.generate_report(Path(), report_path)
