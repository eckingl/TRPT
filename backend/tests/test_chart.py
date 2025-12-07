"""图表生成模块测试"""

from pathlib import Path

import pandas as pd
import pytest

from app.core.chart import (
    ChartTheme,
    ensure_chinese_font,
    get_theme,
    list_themes,
    make_bar_chart,
    make_grade_bar_chart,
    make_grade_pie_chart,
    make_grouped_bar_chart,
    make_land_use_stack_chart,
    make_pie_chart,
    make_stacked_bar_chart,
    make_town_comparison_chart,
    make_town_grade_stack_chart,
    set_theme,
)

# ============ 字体和主题测试 ============


class TestChineseFont:
    """中文字体配置测试"""

    def test_ensure_chinese_font(self) -> None:
        """测试中文字体配置"""
        font_name = ensure_chinese_font()
        assert isinstance(font_name, str)
        assert len(font_name) > 0

    def test_ensure_chinese_font_idempotent(self) -> None:
        """测试字体配置幂等性"""
        font1 = ensure_chinese_font()
        font2 = ensure_chinese_font()
        assert font1 == font2


class TestThemes:
    """主题系统测试"""

    def test_list_themes(self) -> None:
        """测试列出所有主题"""
        themes = list_themes()
        assert isinstance(themes, list)
        assert "default" in themes
        assert "professional" in themes
        assert "earth" in themes
        assert "vibrant" in themes

    def test_get_theme_default(self) -> None:
        """测试获取默认主题"""
        theme = get_theme()
        assert isinstance(theme, ChartTheme)
        assert theme.name == "default"

    def test_get_theme_by_name(self) -> None:
        """测试按名称获取主题"""
        theme = get_theme("professional")
        assert theme.name == "professional"

    def test_set_theme(self) -> None:
        """测试设置当前主题"""
        original = get_theme()
        set_theme("earth")
        current = get_theme()
        assert current.name == "earth"
        # 恢复默认
        set_theme(original.name)

    def test_theme_has_colors(self) -> None:
        """测试主题包含配色"""
        theme = get_theme("default")
        assert len(theme.colors) > 0
        assert len(theme.grade_colors) > 0

    def test_get_nonexistent_theme_raises(self) -> None:
        """测试获取不存在的主题抛出异常"""
        with pytest.raises(KeyError):
            get_theme("nonexistent")


# ============ 饼图测试 ============


class TestPieChart:
    """饼图生成测试"""

    def test_make_pie_chart_basic(self) -> None:
        """测试基本饼图生成"""
        data = {"A": 30, "B": 50, "C": 20}
        result = make_pie_chart(data, "测试饼图")

        assert isinstance(result, bytes)
        assert len(result) > 0
        # PNG 文件头
        assert result[:8] == b"\x89PNG\r\n\x1a\n"

    def test_make_pie_chart_empty_data(self) -> None:
        """测试空数据饼图"""
        data: dict[str, float] = {}
        result = make_pie_chart(data, "空数据")

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_make_pie_chart_with_zero_values(self) -> None:
        """测试包含零值的饼图"""
        data = {"A": 30, "B": 0, "C": 20}
        result = make_pie_chart(data, "含零值")

        assert isinstance(result, bytes)

    def test_make_pie_chart_save_to_file(self, tmp_path: Path) -> None:
        """测试保存饼图到文件"""
        data = {"一级": 100, "二级": 200, "三级": 150}
        output = tmp_path / "pie.png"

        result = make_pie_chart(data, "保存测试", output_path=output)

        assert output.exists()
        assert output.read_bytes() == result

    def test_make_grade_pie_chart(self) -> None:
        """测试等级饼图"""
        grade_data = {
            "1级": 50,
            "2级": 80,
            "3级": 120,
            "4级": 60,
            "5级": 30,
        }
        result = make_grade_pie_chart(grade_data, "有机质等级分布")

        assert isinstance(result, bytes)
        assert result[:8] == b"\x89PNG\r\n\x1a\n"

    def test_make_pie_chart_with_theme(self) -> None:
        """测试使用指定主题"""
        data = {"A": 30, "B": 50}
        theme = get_theme("professional")
        result = make_pie_chart(data, "专业主题", theme=theme)

        assert isinstance(result, bytes)


# ============ 柱状图测试 ============


class TestBarChart:
    """柱状图生成测试"""

    def test_make_bar_chart_basic(self) -> None:
        """测试基本柱状图"""
        data = {"甲镇": 25.5, "乙镇": 30.2, "丙镇": 28.8}
        result = make_bar_chart(data, "乡镇对比", ylabel="有机质(g/kg)")

        assert isinstance(result, bytes)
        assert result[:8] == b"\x89PNG\r\n\x1a\n"

    def test_make_bar_chart_horizontal(self) -> None:
        """测试水平柱状图"""
        data = {"A": 100, "B": 200, "C": 150}
        result = make_bar_chart(data, "水平柱状图", horizontal=True)

        assert isinstance(result, bytes)

    def test_make_bar_chart_empty_data(self) -> None:
        """测试空数据柱状图"""
        data: dict[str, float] = {}
        result = make_bar_chart(data, "空数据")

        assert isinstance(result, bytes)

    def test_make_grade_bar_chart(self) -> None:
        """测试等级柱状图"""
        grade_data = {
            "1级": 5000,
            "2级": 12000,
            "3级": 8000,
            "4级": 3000,
            "5级": 1500,
        }
        result = make_grade_bar_chart(grade_data, "有机质分级面积")

        assert isinstance(result, bytes)

    def test_make_grouped_bar_chart(self) -> None:
        """测试分组柱状图"""
        data = pd.DataFrame(
            {
                "乡镇": ["甲镇", "乙镇", "丙镇"],
                "有机质": [25.5, 30.2, 28.8],
                "全氮": [1.2, 1.5, 1.3],
                "有效磷": [15.0, 18.5, 16.2],
            }
        )
        result = make_grouped_bar_chart(
            data,
            "多属性对比",
            x_col="乡镇",
            value_cols=["有机质", "全氮", "有效磷"],
        )

        assert isinstance(result, bytes)

    def test_make_town_comparison_chart(self) -> None:
        """测试乡镇对比图"""
        town_stats = pd.DataFrame(
            {
                "乡镇": ["甲镇", "乙镇", "丙镇", "丁镇"],
                "样点数": [50, 80, 65, 45],
                "均值": [25.5, 30.2, 28.8, 22.1],
                "面积": [10000, 15000, 12000, 8000],
            }
        )
        result = make_town_comparison_chart(town_stats, "有机质")

        assert isinstance(result, bytes)

    def test_make_town_comparison_chart_empty(self) -> None:
        """测试空乡镇数据"""
        empty_df = pd.DataFrame()
        result = make_town_comparison_chart(empty_df, "有机质")

        assert isinstance(result, bytes)


# ============ 堆叠图测试 ============


class TestStackChart:
    """堆叠图生成测试"""

    def test_make_stacked_bar_chart_basic(self) -> None:
        """测试基本堆叠图"""
        data = pd.DataFrame(
            {
                "乡镇": ["甲镇", "乙镇", "丙镇"],
                "1级": [20, 15, 25],
                "2级": [30, 35, 28],
                "3级": [25, 30, 27],
                "4级": [15, 12, 12],
                "5级": [10, 8, 8],
            }
        )
        result = make_stacked_bar_chart(
            data,
            "等级分布",
            x_col="乡镇",
            stack_cols=["1级", "2级", "3级", "4级", "5级"],
        )

        assert isinstance(result, bytes)
        assert result[:8] == b"\x89PNG\r\n\x1a\n"

    def test_make_stacked_bar_chart_percent(self) -> None:
        """测试百分比堆叠图"""
        data = pd.DataFrame(
            {
                "类型": ["耕地", "园地", "林地"],
                "A": [100, 50, 30],
                "B": [200, 80, 50],
                "C": [150, 70, 40],
            }
        )
        result = make_stacked_bar_chart(
            data,
            "百分比堆叠",
            x_col="类型",
            stack_cols=["A", "B", "C"],
            show_percent=True,
        )

        assert isinstance(result, bytes)

    def test_make_stacked_bar_chart_horizontal(self) -> None:
        """测试水平堆叠图"""
        data = pd.DataFrame(
            {
                "项目": ["X", "Y", "Z"],
                "部分1": [30, 40, 35],
                "部分2": [50, 45, 55],
                "部分3": [20, 15, 10],
            }
        )
        result = make_stacked_bar_chart(
            data,
            "水平堆叠",
            x_col="项目",
            stack_cols=["部分1", "部分2", "部分3"],
            horizontal=True,
        )

        assert isinstance(result, bytes)

    def test_make_town_grade_stack_chart(self) -> None:
        """测试乡镇等级分布堆叠图"""
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
        grade_order = ["1级", "2级", "3级", "4级", "5级"]

        result = make_town_grade_stack_chart(town_stats, grade_order, "有机质")

        assert isinstance(result, bytes)

    def test_make_land_use_stack_chart(self) -> None:
        """测试土地利用分布堆叠图"""
        df_clean = pd.DataFrame(
            {
                "一级": ["耕地"] * 50 + ["园地"] * 30 + ["林地"] * 20,
                "OM": [25.0] * 20
                + [30.0] * 15
                + [35.0] * 15
                + [28.0] * 15
                + [32.0] * 15
                + [20.0] * 20,
            }
        )
        grade_order = ["1级", "2级", "3级", "4级", "5级"]

        # 简单的分级函数
        def mock_classify(series: pd.Series, attr_key: str) -> pd.Series:
            def classify_value(v: float) -> str:
                if v >= 40:
                    return "1级"
                elif v >= 30:
                    return "2级"
                elif v >= 20:
                    return "3级"
                elif v >= 10:
                    return "4级"
                else:
                    return "5级"

            return series.apply(classify_value)

        result = make_land_use_stack_chart(
            df_clean,
            "OM",
            "有机质",
            grade_order,
            classify_func=mock_classify,
        )

        assert isinstance(result, bytes)


# ============ 集成测试 ============


class TestChartIntegration:
    """图表集成测试"""

    def test_all_themes_work(self) -> None:
        """测试所有主题都能正常工作"""
        data = {"A": 30, "B": 50, "C": 20}

        for theme_name in list_themes():
            theme = get_theme(theme_name)
            result = make_pie_chart(data, f"{theme_name}主题测试", theme=theme)
            assert isinstance(result, bytes)
            assert len(result) > 0

    def test_large_data_pie_chart(self) -> None:
        """测试大数据量饼图"""
        data = {f"类别{i}": i * 10 for i in range(1, 21)}
        result = make_pie_chart(data, "大数据量测试", min_percent=3.0)

        assert isinstance(result, bytes)

    def test_chinese_labels(self) -> None:
        """测试中文标签显示"""
        data = {
            "强酸性": 50,
            "酸性": 120,
            "微酸性": 200,
            "中性": 150,
            "微碱性": 80,
            "碱性": 30,
        }
        result = make_pie_chart(data, "土壤酸碱度分布（pH值）")

        assert isinstance(result, bytes)

    def test_save_multiple_charts(self, tmp_path: Path) -> None:
        """测试保存多个图表"""
        grade_data = {"1级": 100, "2级": 200, "3级": 150}

        # 保存饼图
        pie_path = tmp_path / "pie.png"
        make_grade_pie_chart(grade_data, "饼图", output_path=pie_path)

        # 保存柱状图
        bar_path = tmp_path / "bar.png"
        make_grade_bar_chart(grade_data, "柱状图", output_path=bar_path)

        assert pie_path.exists()
        assert bar_path.exists()
        assert pie_path.stat().st_size > 0
        assert bar_path.stat().st_size > 0
