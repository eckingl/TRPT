"""Word 报告生成模块测试"""

from pathlib import Path

import pandas as pd

from app.core.word import create_document_with_charts
from app.topics.attribute_map.generate import (
    ReportConfig,
    generate_attribute_report,
    generate_multi_attribute_report,
)
from app.topics.attribute_map.stats import AttributeStats

# ============ 辅助函数 ============


def create_mock_stats(
    attr_key: str = "OM",
    attr_name: str = "有机质",
    unit: str = "g/kg",
) -> AttributeStats:
    """创建模拟的 AttributeStats 数据"""
    # 模拟乡镇统计数据
    town_stats = pd.DataFrame(
        {
            "乡镇": ["甲镇", "乙镇", "丙镇"],
            "样点数": [50, 80, 65],
            "均值": [25.5, 30.2, 28.8],
            "面积": [10000, 15000, 12000],
            "1级_pct": [10.0, 8.0, 12.0],
            "2级_pct": [25.0, 30.0, 28.0],
            "3级_pct": [35.0, 38.0, 32.0],
            "4级_pct": [20.0, 15.0, 18.0],
            "5级_pct": [10.0, 9.0, 10.0],
        }
    )

    # 模拟土壤类型统计
    soil_type_stats = pd.DataFrame(
        {
            "YL": ["红壤", "黄壤"],
            "TS": ["红壤", "黄壤"],
            "sample_mean": [28.0, 32.0],
            "sample_count": [100, 80],
        }
    )

    # 模拟清洗后的数据
    df_sample_clean = pd.DataFrame(
        {
            attr_key: [25.0, 30.0, 28.0, 35.0, 22.0] * 20,
            "等级": ["3级", "2级", "3级", "2级", "4级"] * 20,
            "一级": ["耕地"] * 50 + ["园地"] * 30 + ["林地"] * 20,
            "行政区名称": ["甲镇"] * 40 + ["乙镇"] * 35 + ["丙镇"] * 25,
        }
    )

    df_area_clean = pd.DataFrame(
        {
            attr_key: [25.0, 30.0, 28.0] * 30,
            "等级": ["3级", "2级", "3级"] * 30,
            "面积": [100.0, 150.0, 120.0] * 30,
            "行政区名称": ["甲镇"] * 30 + ["乙镇"] * 30 + ["丙镇"] * 30,
        }
    )

    return AttributeStats(
        attr_key=attr_key,
        attr_name=attr_name,
        unit=unit,
        sample_total=100,
        sample_mean=28.5,
        sample_median=27.0,
        sample_min=15.0,
        sample_max=45.0,
        area_total=37000.0,
        area_mean=27.8,
        area_median=26.5,
        area_min=12.0,
        area_max=42.0,
        grade_sample_counts={
            "1级": 10,
            "2级": 25,
            "3级": 35,
            "4级": 20,
            "5级": 10,
        },
        grade_area_sums={
            "1级": 3700.0,
            "2级": 9250.0,
            "3级": 12950.0,
            "4级": 7400.0,
            "5级": 3700.0,
        },
        town_stats=town_stats,
        soil_type_stats=soil_type_stats,
        df_sample_clean=df_sample_clean,
        df_area_clean=df_area_clean,
    )


# ============ Word 核心功能测试 ============


class TestCreateDocumentWithCharts:
    """测试带图表的文档创建"""

    def test_create_empty_document(self) -> None:
        """测试创建空文档"""
        result = create_document_with_charts([], "空报告")

        assert isinstance(result, bytes)
        assert len(result) > 0
        # DOCX 文件是 ZIP 格式，以 PK 开头
        assert result[:2] == b"PK"

    def test_create_document_with_chart(self) -> None:
        """测试创建带图表的文档"""
        # 生成一个简单的图表
        from app.core.chart import make_pie_chart

        chart_data = make_pie_chart({"A": 30, "B": 50, "C": 20}, "测试图表")

        result = create_document_with_charts(
            [(chart_data, "测试饼图")],
            "测试报告",
        )

        assert isinstance(result, bytes)
        assert result[:2] == b"PK"

    def test_save_document_to_file(self, tmp_path: Path) -> None:
        """测试保存文档到文件"""
        output = tmp_path / "test.docx"

        result = create_document_with_charts(
            [],
            "保存测试",
            output_path=output,
        )

        assert output.exists()
        assert output.read_bytes() == result


# ============ 属性报告生成测试 ============


class TestGenerateAttributeReport:
    """测试单属性报告生成"""

    def test_generate_basic_report(self) -> None:
        """测试生成基本报告"""
        stats = create_mock_stats()
        result = generate_attribute_report(stats)

        assert isinstance(result, bytes)
        assert len(result) > 0
        assert result[:2] == b"PK"

    def test_generate_report_with_config(self) -> None:
        """测试使用配置生成报告"""
        stats = create_mock_stats()
        config = ReportConfig(
            region_name="测试县",
            survey_year=2024,
            theme="professional",
        )

        result = generate_attribute_report(stats, config)

        assert isinstance(result, bytes)

    def test_generate_report_without_charts(self) -> None:
        """测试生成不含图表的报告"""
        stats = create_mock_stats()
        config = ReportConfig(
            include_pie_chart=False,
            include_bar_chart=False,
            include_town_chart=False,
            include_stack_chart=False,
        )

        result = generate_attribute_report(stats, config)

        assert isinstance(result, bytes)

    def test_save_report_to_file(self, tmp_path: Path) -> None:
        """测试保存报告到文件"""
        stats = create_mock_stats()
        output = tmp_path / "report.docx"

        result = generate_attribute_report(stats, output_path=output)

        assert output.exists()
        assert output.read_bytes() == result


# ============ 多属性报告生成测试 ============


class TestGenerateMultiAttributeReport:
    """测试多属性综合报告生成"""

    def test_generate_multi_report(self) -> None:
        """测试生成多属性报告"""
        stats_list = [
            create_mock_stats("OM", "有机质", "g/kg"),
            create_mock_stats("TN", "全氮", "g/kg"),
            create_mock_stats("AP", "有效磷", "mg/kg"),
        ]

        result = generate_multi_attribute_report(stats_list)

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_generate_single_attr_multi_report(self) -> None:
        """测试只有一个属性的多属性报告"""
        stats_list = [create_mock_stats()]

        result = generate_multi_attribute_report(stats_list)

        assert isinstance(result, bytes)

    def test_generate_multi_report_with_config(self) -> None:
        """测试使用配置生成多属性报告"""
        stats_list = [
            create_mock_stats("OM", "有机质", "g/kg"),
            create_mock_stats("pH", "酸碱度", ""),
        ]
        config = ReportConfig(
            region_name="示例县",
            survey_year=2023,
            theme="earth",
        )

        result = generate_multi_attribute_report(stats_list, config)

        assert isinstance(result, bytes)


# ============ 报告配置测试 ============


class TestReportConfig:
    """测试报告配置"""

    def test_default_config(self) -> None:
        """测试默认配置"""
        config = ReportConfig()

        assert config.region_name == "XX县"
        assert config.survey_year == 2024
        assert config.theme == "professional"
        assert config.include_pie_chart is True
        assert config.include_bar_chart is True

    def test_custom_config(self) -> None:
        """测试自定义配置"""
        config = ReportConfig(
            region_name="自定义县",
            survey_year=2025,
            theme="earth",
            include_stack_chart=False,
        )

        assert config.region_name == "自定义县"
        assert config.survey_year == 2025
        assert config.theme == "earth"
        assert config.include_stack_chart is False


# ============ 集成测试 ============


class TestWordIntegration:
    """Word 报告集成测试"""

    def test_full_report_generation(self, tmp_path: Path) -> None:
        """测试完整报告生成流程"""
        # 创建模拟数据
        stats = create_mock_stats()

        # 配置报告
        config = ReportConfig(
            region_name="集成测试县",
            survey_year=2024,
            theme="professional",
        )

        # 生成报告
        output = tmp_path / "integration_test.docx"
        result = generate_attribute_report(stats, config, output_path=output)

        # 验证
        assert output.exists()
        assert output.stat().st_size > 0
        assert result == output.read_bytes()

    def test_all_themes_generate_report(self) -> None:
        """测试所有主题都能生成报告"""
        stats = create_mock_stats()
        themes = ["default", "professional", "earth", "vibrant"]

        for theme in themes:
            config = ReportConfig(theme=theme)
            result = generate_attribute_report(stats, config)
            assert isinstance(result, bytes)
            assert len(result) > 0
