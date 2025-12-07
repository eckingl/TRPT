"""图表主题配置模块

提供可配置的图表配色方案和样式
"""

from dataclasses import dataclass, field
from enum import Enum


class ThemeName(Enum):
    """预设主题名称"""

    DEFAULT = "default"
    PROFESSIONAL = "professional"  # 专业报告风格（蓝绿色系）
    EARTH = "earth"  # 大地色系（适合土壤/农业报告）
    VIBRANT = "vibrant"  # 鲜艳色系


@dataclass(frozen=True)
class ChartTheme:
    """图表主题配置

    Attributes:
        name: 主题名称
        colors: 主色列表（用于饼图、柱状图等）
        background: 背景色
        text_color: 文字颜色
        grid_color: 网格线颜色
        title_size: 标题字号
        label_size: 标签字号
        legend_size: 图例字号
        dpi: 输出分辨率
    """

    name: str
    colors: tuple[str, ...]
    background: str = "#FFFFFF"
    text_color: str = "#333333"
    grid_color: str = "#E0E0E0"
    title_size: int = 14
    label_size: int = 10
    legend_size: int = 9
    dpi: int = 150

    # 分级配色（用于土壤属性等级）
    grade_colors: tuple[str, ...] = field(default_factory=tuple)


# 预设主题定义
THEME_DEFAULT = ChartTheme(
    name="default",
    colors=(
        "#5470C6",  # 蓝
        "#91CC75",  # 绿
        "#FAC858",  # 黄
        "#EE6666",  # 红
        "#73C0DE",  # 浅蓝
        "#3BA272",  # 深绿
        "#FC8452",  # 橙
        "#9A60B4",  # 紫
    ),
    grade_colors=(
        "#2E7D32",  # 1级 - 深绿（最优）
        "#66BB6A",  # 2级 - 绿
        "#AED581",  # 3级 - 浅绿
        "#FFF176",  # 4级 - 黄
        "#FFB74D",  # 5级 - 橙
        "#E57373",  # 6级 - 红
        "#B71C1C",  # 7级 - 深红（最差）
    ),
)

THEME_PROFESSIONAL = ChartTheme(
    name="professional",
    colors=(
        "#1565C0",  # 深蓝
        "#0097A7",  # 青
        "#00796B",  # 蓝绿
        "#43A047",  # 绿
        "#7CB342",  # 黄绿
        "#558B2F",  # 橄榄
        "#33691E",  # 深橄榄
        "#827717",  # 暗黄
    ),
    text_color="#212121",
    grid_color="#BDBDBD",
    grade_colors=(
        "#1B5E20",  # 1级
        "#2E7D32",  # 2级
        "#388E3C",  # 3级
        "#689F38",  # 4级
        "#AFB42B",  # 5级
        "#F57F17",  # 6级
        "#D84315",  # 7级
    ),
)

THEME_EARTH = ChartTheme(
    name="earth",
    colors=(
        "#8D6E63",  # 棕
        "#A1887F",  # 浅棕
        "#795548",  # 深棕
        "#6D4C41",  # 咖啡
        "#5D4037",  # 深咖啡
        "#4E342E",  # 暗棕
        "#BCAAA4",  # 米色
        "#D7CCC8",  # 浅米
    ),
    background="#FAFAFA",
    text_color="#3E2723",
    grid_color="#D7CCC8",
    grade_colors=(
        "#33691E",  # 1级 - 深绿
        "#558B2F",  # 2级 - 橄榄绿
        "#7CB342",  # 3级 - 黄绿
        "#C0CA33",  # 4级 - 柠檬
        "#FDD835",  # 5级 - 黄
        "#FF8F00",  # 6级 - 琥珀
        "#E65100",  # 7级 - 橙
    ),
)

THEME_VIBRANT = ChartTheme(
    name="vibrant",
    colors=(
        "#E91E63",  # 粉红
        "#9C27B0",  # 紫
        "#673AB7",  # 深紫
        "#3F51B5",  # 靛蓝
        "#2196F3",  # 蓝
        "#00BCD4",  # 青
        "#009688",  # 蓝绿
        "#4CAF50",  # 绿
    ),
    text_color="#1A1A1A",
    grade_colors=(
        "#00C853",  # 1级
        "#64DD17",  # 2级
        "#AEEA00",  # 3级
        "#FFEB3B",  # 4级
        "#FFC107",  # 5级
        "#FF9800",  # 6级
        "#FF5722",  # 7级
    ),
)

# 主题注册表
_THEMES: dict[str, ChartTheme] = {
    ThemeName.DEFAULT.value: THEME_DEFAULT,
    ThemeName.PROFESSIONAL.value: THEME_PROFESSIONAL,
    ThemeName.EARTH.value: THEME_EARTH,
    ThemeName.VIBRANT.value: THEME_VIBRANT,
}

# 当前活动主题
_current_theme: ChartTheme = THEME_DEFAULT


def get_theme(name: str | None = None) -> ChartTheme:
    """获取指定主题

    Args:
        name: 主题名称，为 None 时返回当前主题

    Returns:
        ChartTheme: 主题配置对象

    Raises:
        KeyError: 主题不存在
    """
    if name is None:
        return _current_theme
    return _THEMES[name]


def set_theme(name: str) -> ChartTheme:
    """设置当前主题

    Args:
        name: 主题名称

    Returns:
        ChartTheme: 设置后的主题对象

    Raises:
        KeyError: 主题不存在
    """
    global _current_theme
    _current_theme = _THEMES[name]
    return _current_theme


def register_theme(theme: ChartTheme) -> None:
    """注册自定义主题

    Args:
        theme: 主题配置对象
    """
    _THEMES[theme.name] = theme


def list_themes() -> list[str]:
    """列出所有可用主题名称"""
    return list(_THEMES.keys())


def get_grade_color(grade_index: int, theme: ChartTheme | None = None) -> str:
    """获取等级对应的颜色

    Args:
        grade_index: 等级索引（0-based）
        theme: 主题，为 None 时使用当前主题

    Returns:
        str: 颜色代码
    """
    if theme is None:
        theme = _current_theme

    colors = theme.grade_colors
    if not colors:
        colors = theme.colors

    return colors[grade_index % len(colors)]


def get_color(index: int, theme: ChartTheme | None = None) -> str:
    """获取索引对应的主题颜色

    Args:
        index: 颜色索引（0-based）
        theme: 主题，为 None 时使用当前主题

    Returns:
        str: 颜色代码
    """
    if theme is None:
        theme = _current_theme

    return theme.colors[index % len(theme.colors)]
