"""柱状图生成模块

用于生成土壤属性统计的柱状图，支持单系列和多系列
"""

from io import BytesIO
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from app.core.chart.setup_chinese import ensure_chinese_font
from app.core.chart.themes import ChartTheme, get_theme


def make_bar_chart(
    data: dict[str, float],
    title: str,
    *,
    xlabel: str = "",
    ylabel: str = "",
    theme: ChartTheme | None = None,
    figsize: tuple[float, float] = (10, 6),
    horizontal: bool = False,
    show_value: bool = True,
    value_format: str = ".1f",
    output_path: Path | None = None,
) -> bytes:
    """生成单系列柱状图

    Args:
        data: 数据字典，格式为 {标签: 值}
        title: 图表标题
        xlabel: X轴标签
        ylabel: Y轴标签
        theme: 主题配置
        figsize: 图表尺寸
        horizontal: 是否为水平柱状图
        show_value: 是否在柱子上显示数值
        value_format: 数值格式化字符串
        output_path: 输出路径

    Returns:
        bytes: PNG 图片数据
    """
    ensure_chinese_font()
    if theme is None:
        theme = get_theme()

    labels = list(data.keys())
    values = list(data.values())

    if not labels:
        return _create_empty_chart(title, theme, figsize, output_path)

    fig, ax = plt.subplots(figsize=figsize, facecolor=theme.background)
    ax.set_facecolor(theme.background)

    x = np.arange(len(labels))
    colors = [theme.colors[i % len(theme.colors)] for i in range(len(labels))]

    if horizontal:
        bars = ax.barh(x, values, color=colors)
        ax.set_yticks(x)
        ax.set_yticklabels(labels)
        ax.set_xlabel(ylabel, fontsize=theme.label_size, color=theme.text_color)
        ax.set_ylabel(xlabel, fontsize=theme.label_size, color=theme.text_color)

        if show_value:
            for bar, value in zip(bars, values, strict=True):
                width = bar.get_width()
                ax.annotate(
                    f"{value:{value_format}}",
                    xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(3, 0),
                    textcoords="offset points",
                    ha="left",
                    va="center",
                    fontsize=theme.label_size - 1,
                    color=theme.text_color,
                )
    else:
        bars = ax.bar(x, values, color=colors)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha="right")
        ax.set_xlabel(xlabel, fontsize=theme.label_size, color=theme.text_color)
        ax.set_ylabel(ylabel, fontsize=theme.label_size, color=theme.text_color)

        if show_value:
            for bar, value in zip(bars, values, strict=True):
                height = bar.get_height()
                ax.annotate(
                    f"{value:{value_format}}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontsize=theme.label_size - 1,
                    color=theme.text_color,
                )

    ax.set_title(title, fontsize=theme.title_size, color=theme.text_color, pad=15)
    ax.tick_params(colors=theme.text_color)
    ax.grid(axis="y" if not horizontal else "x", alpha=0.3, color=theme.grid_color)

    plt.tight_layout()

    return _save_figure(fig, theme.dpi, output_path)


def make_grouped_bar_chart(
    data: pd.DataFrame,
    title: str,
    *,
    x_col: str,
    value_cols: list[str],
    xlabel: str = "",
    ylabel: str = "",
    theme: ChartTheme | None = None,
    figsize: tuple[float, float] = (12, 6),
    show_value: bool = False,
    value_format: str = ".1f",
    output_path: Path | None = None,
) -> bytes:
    """生成分组柱状图

    Args:
        data: DataFrame 数据
        title: 图表标题
        x_col: X轴分类列名
        value_cols: 数值列名列表
        xlabel: X轴标签
        ylabel: Y轴标签
        theme: 主题配置
        figsize: 图表尺寸
        show_value: 是否显示数值
        value_format: 数值格式化字符串
        output_path: 输出路径

    Returns:
        bytes: PNG 图片数据
    """
    ensure_chinese_font()
    if theme is None:
        theme = get_theme()

    if data.empty or not value_cols:
        return _create_empty_chart(title, theme, figsize, output_path)

    labels = data[x_col].tolist()
    n_groups = len(labels)
    n_bars = len(value_cols)

    fig, ax = plt.subplots(figsize=figsize, facecolor=theme.background)
    ax.set_facecolor(theme.background)

    x = np.arange(n_groups)
    width = 0.8 / n_bars

    for i, col in enumerate(value_cols):
        values = data[col].tolist()
        offset = (i - n_bars / 2 + 0.5) * width
        bars = ax.bar(
            x + offset,
            values,
            width,
            label=col,
            color=theme.colors[i % len(theme.colors)],
        )

        if show_value:
            for bar, value in zip(bars, values, strict=True):
                height = bar.get_height()
                if height > 0:
                    ax.annotate(
                        f"{value:{value_format}}",
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 2),
                        textcoords="offset points",
                        ha="center",
                        va="bottom",
                        fontsize=max(6, theme.label_size - 2),
                        color=theme.text_color,
                    )

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_xlabel(xlabel, fontsize=theme.label_size, color=theme.text_color)
    ax.set_ylabel(ylabel, fontsize=theme.label_size, color=theme.text_color)
    ax.set_title(title, fontsize=theme.title_size, color=theme.text_color, pad=15)
    ax.tick_params(colors=theme.text_color)
    ax.grid(axis="y", alpha=0.3, color=theme.grid_color)
    ax.legend(fontsize=theme.legend_size)

    plt.tight_layout()

    return _save_figure(fig, theme.dpi, output_path)


def make_town_comparison_chart(
    town_stats: pd.DataFrame,
    attr_name: str,
    *,
    theme: ChartTheme | None = None,
    figsize: tuple[float, float] = (12, 6),
    output_path: Path | None = None,
) -> bytes:
    """生成乡镇对比柱状图

    专门针对 AttributeStats.town_stats 数据格式设计

    Args:
        town_stats: 乡镇统计 DataFrame，需包含 '乡镇', '均值' 列
        attr_name: 属性名称（用于标题）
        theme: 主题配置
        figsize: 图表尺寸
        output_path: 输出路径

    Returns:
        bytes: PNG 图片数据
    """
    ensure_chinese_font()
    if theme is None:
        theme = get_theme()

    if town_stats.empty or "乡镇" not in town_stats.columns:
        return _create_empty_chart(f"{attr_name}乡镇对比", theme, figsize, output_path)

    # 按均值排序
    df = town_stats.copy()
    if "均值" in df.columns:
        df = df.sort_values("均值", ascending=True)

    towns = df["乡镇"].tolist()
    values = df["均值"].tolist() if "均值" in df.columns else [0] * len(towns)

    fig, ax = plt.subplots(figsize=figsize, facecolor=theme.background)
    ax.set_facecolor(theme.background)

    y = np.arange(len(towns))
    bars = ax.barh(y, values, color=theme.colors[0])

    # 显示数值
    for bar, value in zip(bars, values, strict=True):
        width = bar.get_width()
        ax.annotate(
            f"{value:.2f}",
            xy=(width, bar.get_y() + bar.get_height() / 2),
            xytext=(3, 0),
            textcoords="offset points",
            ha="left",
            va="center",
            fontsize=theme.label_size - 1,
            color=theme.text_color,
        )

    ax.set_yticks(y)
    ax.set_yticklabels(towns)
    ax.set_xlabel(f"{attr_name}均值", fontsize=theme.label_size, color=theme.text_color)
    ax.set_title(
        f"各乡镇{attr_name}对比",
        fontsize=theme.title_size,
        color=theme.text_color,
        pad=15,
    )
    ax.tick_params(colors=theme.text_color)
    ax.grid(axis="x", alpha=0.3, color=theme.grid_color)

    plt.tight_layout()

    return _save_figure(fig, theme.dpi, output_path)


def make_grade_bar_chart(
    grade_data: dict[str, float],
    title: str,
    *,
    ylabel: str = "面积(亩)",
    theme: ChartTheme | None = None,
    figsize: tuple[float, float] = (10, 6),
    show_value: bool = True,
    output_path: Path | None = None,
) -> bytes:
    """生成等级分布柱状图（使用等级专用配色）

    Args:
        grade_data: 等级数据，格式为 {等级名: 值}
        title: 图表标题
        ylabel: Y轴标签
        theme: 主题配置
        figsize: 图表尺寸
        show_value: 是否显示数值
        output_path: 输出路径

    Returns:
        bytes: PNG 图片数据
    """
    ensure_chinese_font()
    if theme is None:
        theme = get_theme()

    labels = list(grade_data.keys())
    values = list(grade_data.values())

    if not labels:
        return _create_empty_chart(title, theme, figsize, output_path)

    fig, ax = plt.subplots(figsize=figsize, facecolor=theme.background)
    ax.set_facecolor(theme.background)

    x = np.arange(len(labels))
    grade_colors = theme.grade_colors if theme.grade_colors else theme.colors
    colors = [grade_colors[i % len(grade_colors)] for i in range(len(labels))]

    bars = ax.bar(x, values, color=colors)

    if show_value:
        for bar, value in zip(bars, values, strict=True):
            height = bar.get_height()
            if height > 0:
                # 格式化大数字
                if value >= 10000:
                    text = f"{value / 10000:.1f}万"
                else:
                    text = f"{value:.0f}"

                ax.annotate(
                    text,
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontsize=theme.label_size - 1,
                    color=theme.text_color,
                )

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel(ylabel, fontsize=theme.label_size, color=theme.text_color)
    ax.set_title(title, fontsize=theme.title_size, color=theme.text_color, pad=15)
    ax.tick_params(colors=theme.text_color)
    ax.grid(axis="y", alpha=0.3, color=theme.grid_color)

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
