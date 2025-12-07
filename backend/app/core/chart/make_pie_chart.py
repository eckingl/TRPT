"""饼图生成模块

用于生成土壤属性分级分布的饼图
"""

from io import BytesIO
from pathlib import Path

import matplotlib.pyplot as plt

from app.core.chart.setup_chinese import ensure_chinese_font
from app.core.chart.themes import ChartTheme, get_theme


def make_pie_chart(
    data: dict[str, float],
    title: str,
    *,
    theme: ChartTheme | None = None,
    figsize: tuple[float, float] = (8, 6),
    show_percent: bool = True,
    show_value: bool = False,
    min_percent: float = 1.0,
    output_path: Path | None = None,
) -> bytes:
    """生成饼图

    Args:
        data: 数据字典，格式为 {标签: 值}
        title: 图表标题
        theme: 主题配置，为 None 时使用当前主题
        figsize: 图表尺寸 (宽, 高)，单位为英寸
        show_percent: 是否显示百分比
        show_value: 是否显示具体数值
        min_percent: 最小显示百分比，小于此值的合并为"其他"
        output_path: 输出路径，为 None 时返回 bytes

    Returns:
        bytes: PNG 图片数据
    """
    ensure_chinese_font()
    if theme is None:
        theme = get_theme()

    # 过滤零值和负值
    filtered_data = {k: v for k, v in data.items() if v > 0}

    if not filtered_data:
        return _create_empty_chart(title, theme, figsize, output_path)

    # 计算总和和百分比
    total = sum(filtered_data.values())
    percentages = {k: v / total * 100 for k, v in filtered_data.items()}

    # 合并小于阈值的项
    main_data: dict[str, float] = {}
    other_value = 0.0

    for label, value in filtered_data.items():
        if percentages[label] >= min_percent:
            main_data[label] = value
        else:
            other_value += value

    if other_value > 0:
        main_data["其他"] = other_value

    # 准备绑数据
    labels = list(main_data.keys())
    values = list(main_data.values())
    colors = [theme.colors[i % len(theme.colors)] for i in range(len(labels))]

    # 创建图表
    fig, ax = plt.subplots(figsize=figsize, facecolor=theme.background)
    ax.set_facecolor(theme.background)

    # 构建标签格式
    def make_autopct(show_pct: bool, show_val: bool, total_val: float) -> str | None:
        if not show_pct and not show_val:
            return None

        def autopct(pct: float) -> str:
            parts = []
            if show_pct:
                parts.append(f"{pct:.1f}%")
            if show_val:
                val = pct / 100 * total_val
                if val >= 10000:
                    parts.append(f"({val / 10000:.1f}万)")
                elif val >= 1:
                    parts.append(f"({val:.0f})")
                else:
                    parts.append(f"({val:.2f})")
            return "\n".join(parts)

        return autopct

    autopct_func = make_autopct(show_percent, show_value, total)

    # 绘制饼图
    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        colors=colors,
        autopct=autopct_func if autopct_func else "",
        startangle=90,
        textprops={"fontsize": theme.label_size, "color": theme.text_color},
    )

    # 设置自动标签样式
    for autotext in autotexts:
        autotext.set_fontsize(theme.label_size - 1)
        autotext.set_color("#FFFFFF")
        autotext.set_weight("bold")

    # 设置标题
    ax.set_title(title, fontsize=theme.title_size, color=theme.text_color, pad=20)

    plt.tight_layout()

    # 输出
    return _save_figure(fig, theme.dpi, output_path)


def make_grade_pie_chart(
    grade_data: dict[str, float],
    title: str,
    *,
    theme: ChartTheme | None = None,
    figsize: tuple[float, float] = (8, 6),
    show_percent: bool = True,
    output_path: Path | None = None,
) -> bytes:
    """生成等级分布饼图（使用等级专用配色）

    Args:
        grade_data: 等级数据，格式为 {等级名: 值}
        title: 图表标题
        theme: 主题配置
        figsize: 图表尺寸
        show_percent: 是否显示百分比
        output_path: 输出路径

    Returns:
        bytes: PNG 图片数据
    """
    ensure_chinese_font()
    if theme is None:
        theme = get_theme()

    # 过滤零值
    filtered_data = {k: v for k, v in grade_data.items() if v > 0}

    if not filtered_data:
        return _create_empty_chart(title, theme, figsize, output_path)

    labels = list(filtered_data.keys())
    values = list(filtered_data.values())

    # 使用等级配色
    grade_colors = theme.grade_colors if theme.grade_colors else theme.colors
    colors = [grade_colors[i % len(grade_colors)] for i in range(len(labels))]

    # 创建图表
    fig, ax = plt.subplots(figsize=figsize, facecolor=theme.background)
    ax.set_facecolor(theme.background)

    def autopct(pct: float) -> str:
        if show_percent:
            return f"{pct:.1f}%"
        return ""

    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        colors=colors,
        autopct=autopct,
        startangle=90,
        textprops={"fontsize": theme.label_size, "color": theme.text_color},
    )

    for autotext in autotexts:
        autotext.set_fontsize(theme.label_size - 1)
        autotext.set_color("#FFFFFF")
        autotext.set_weight("bold")

    ax.set_title(title, fontsize=theme.title_size, color=theme.text_color, pad=20)

    plt.tight_layout()

    return _save_figure(fig, theme.dpi, output_path)


def _create_empty_chart(
    title: str,
    theme: ChartTheme,
    figsize: tuple[float, float],
    output_path: Path | None,
) -> bytes:
    """创建空数据提示图表"""
    fig, ax = plt.subplots(figsize=figsize, facecolor=theme.background)
    ax.set_facecolor(theme.background)
    ax.text(
        0.5,
        0.5,
        "暂无数据",
        ha="center",
        va="center",
        fontsize=theme.title_size,
        color=theme.text_color,
    )
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title(title, fontsize=theme.title_size, color=theme.text_color)

    return _save_figure(fig, theme.dpi, output_path)


def _save_figure(fig: plt.Figure, dpi: int, output_path: Path | None) -> bytes:
    """保存图表并返回字节数据"""
    buf = BytesIO()
    fig.savefig(
        buf, format="png", dpi=dpi, bbox_inches="tight", facecolor=fig.get_facecolor()
    )
    plt.close(fig)

    buf.seek(0)
    data = buf.read()

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(data)

    return data
