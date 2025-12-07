"""图表生成模块

提供土壤属性分析图表的生成功能，支持：
- 饼图：分级分布展示
- 柱状图：对比分析、乡镇统计
- 堆叠图：多维度分布展示

使用示例：
    from app.core.chart import make_pie_chart, make_bar_chart, set_theme

    # 设置主题
    set_theme("professional")

    # 生成饼图
    data = {"1级": 100, "2级": 200, "3级": 150}
    png_bytes = make_pie_chart(data, "有机质等级分布")

    # 生成柱状图
    png_bytes = make_bar_chart(data, "有机质等级面积", ylabel="面积(亩)")
"""

from app.core.chart.make_bar_chart import (
    make_bar_chart,
    make_grade_bar_chart,
    make_grouped_bar_chart,
    make_town_comparison_chart,
)
from app.core.chart.make_pie_chart import (
    make_grade_pie_chart,
    make_pie_chart,
)
from app.core.chart.make_stack_chart import (
    make_land_use_stack_chart,
    make_stacked_bar_chart,
    make_town_grade_stack_chart,
)
from app.core.chart.setup_chinese import (
    ensure_chinese_font,
    setup_chinese_font,
)
from app.core.chart.themes import (
    ChartTheme,
    ThemeName,
    get_color,
    get_grade_color,
    get_theme,
    list_themes,
    register_theme,
    set_theme,
)

__all__ = [
    # 字体配置
    "ensure_chinese_font",
    "setup_chinese_font",
    # 主题
    "ChartTheme",
    "ThemeName",
    "get_theme",
    "set_theme",
    "list_themes",
    "register_theme",
    "get_color",
    "get_grade_color",
    # 饼图
    "make_pie_chart",
    "make_grade_pie_chart",
    # 柱状图
    "make_bar_chart",
    "make_grade_bar_chart",
    "make_grouped_bar_chart",
    "make_town_comparison_chart",
    # 堆叠图
    "make_stacked_bar_chart",
    "make_town_grade_stack_chart",
    "make_land_use_stack_chart",
]
