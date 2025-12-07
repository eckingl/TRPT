"""堆叠图生成模块

用于生成土壤属性的堆叠柱状图，展示多维度分布
"""

from io import BytesIO
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from app.core.chart.setup_chinese import ensure_chinese_font
from app.core.chart.themes import ChartTheme, get_theme


def make_stacked_bar_chart(
    data: pd.DataFrame,
    title: str,
    *,
    x_col: str,
    stack_cols: list[str],
    xlabel: str = "",
    ylabel: str = "",
    theme: ChartTheme | None = None,
    figsize: tuple[float, float] = (12, 6),
    show_percent: bool = False,
    horizontal: bool = False,
    output_path: Path | None = None,
) -> bytes:
    """生成堆叠柱状图

    Args:
        data: DataFrame 数据
        title: 图表标题
        x_col: X轴分类列名
        stack_cols: 堆叠数值列名列表
        xlabel: X轴标签
        ylabel: Y轴标签
        theme: 主题配置
        figsize: 图表尺寸
        show_percent: 是否显示为百分比堆叠（100%堆叠）
        horizontal: 是否为水平堆叠图
        output_path: 输出路径

    Returns:
        bytes: PNG 图片数据
    """
    ensure_chinese_font()
    if theme is None:
        theme = get_theme()

    if data.empty or not stack_cols:
        return _create_empty_chart(title, theme, figsize, output_path)

    df = data.copy()
    labels = df[x_col].tolist()

    # 如果是百分比堆叠，先转换数据
    if show_percent:
        row_sums = df[stack_cols].sum(axis=1)
        for col in stack_cols:
            df[col] = df[col] / row_sums * 100

    fig, ax = plt.subplots(figsize=figsize, facecolor=theme.background)
    ax.set_facecolor(theme.background)

    x = np.arange(len(labels))
    width = 0.6

    # 使用等级配色（适合分级数据）
    colors = theme.grade_colors if theme.grade_colors else theme.colors

    if horizontal:
        # 水平堆叠
        left = np.zeros(len(labels))
        for i, col in enumerate(stack_cols):
            values = df[col].tolist()
            color = colors[i % len(colors)]
            ax.barh(x, values, width, left=left, label=col, color=color)
            left += np.array(values)

        ax.set_yticks(x)
        ax.set_yticklabels(labels)
        ax.set_xlabel(
            ylabel if ylabel else ("占比(%)" if show_percent else ""),
            fontsize=theme.label_size,
            color=theme.text_color,
        )
        ax.set_ylabel(xlabel, fontsize=theme.label_size, color=theme.text_color)

        if show_percent:
            ax.set_xlim(0, 100)
    else:
        # 垂直堆叠
        bottom = np.zeros(len(labels))
        for i, col in enumerate(stack_cols):
            values = df[col].tolist()
            color = colors[i % len(colors)]
            ax.bar(x, values, width, bottom=bottom, label=col, color=color)
            bottom += np.array(values)

        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha="right")
        ax.set_xlabel(xlabel, fontsize=theme.label_size, color=theme.text_color)
        ax.set_ylabel(
            ylabel if ylabel else ("占比(%)" if show_percent else ""),
            fontsize=theme.label_size,
            color=theme.text_color,
        )

        if show_percent:
            ax.set_ylim(0, 100)

    ax.set_title(title, fontsize=theme.title_size, color=theme.text_color, pad=15)
    ax.tick_params(colors=theme.text_color)
    ax.legend(
        fontsize=theme.legend_size,
        loc="upper right",
        bbox_to_anchor=(1.15, 1),
    )

    plt.tight_layout()

    return _save_figure(fig, theme.dpi, output_path)


def make_town_grade_stack_chart(
    town_stats: pd.DataFrame,
    grade_order: list[str],
    attr_name: str,
    *,
    theme: ChartTheme | None = None,
    figsize: tuple[float, float] = (14, 6),
    show_percent: bool = True,
    output_path: Path | None = None,
) -> bytes:
    """生成乡镇等级分布堆叠图

    专门针对 AttributeStats.town_stats 数据格式设计

    Args:
        town_stats: 乡镇统计 DataFrame，需包含 '乡镇' 和各等级占比列（如 '1级_pct'）
        grade_order: 等级顺序列表，如 ['1级', '2级', ...]
        attr_name: 属性名称（用于标题）
        theme: 主题配置
        figsize: 图表尺寸
        show_percent: 是否为百分比堆叠
        output_path: 输出路径

    Returns:
        bytes: PNG 图片数据
    """
    ensure_chinese_font()
    if theme is None:
        theme = get_theme()

    if town_stats.empty or "乡镇" not in town_stats.columns:
        return _create_empty_chart(f"{attr_name}乡镇分布", theme, figsize, output_path)

    # 构建等级占比列名
    pct_cols = [f"{g}_pct" for g in grade_order if f"{g}_pct" in town_stats.columns]

    if not pct_cols:
        return _create_empty_chart(f"{attr_name}乡镇分布", theme, figsize, output_path)

    # 准备数据
    df = town_stats[["乡镇"] + pct_cols].copy()

    # 重命名列为等级名（去掉 _pct 后缀）
    rename_map = {col: col.replace("_pct", "") for col in pct_cols}
    df = df.rename(columns=rename_map)

    stack_cols = list(rename_map.values())

    return make_stacked_bar_chart(
        df,
        f"各乡镇{attr_name}等级分布",
        x_col="乡镇",
        stack_cols=stack_cols,
        ylabel="占比(%)" if show_percent else "面积",
        theme=theme,
        figsize=figsize,
        show_percent=False,  # 数据已经是百分比
        output_path=output_path,
    )


def make_land_use_stack_chart(
    df_clean: pd.DataFrame,
    attr_key: str,
    attr_name: str,
    grade_order: list[str],
    *,
    classify_func: callable,
    theme: ChartTheme | None = None,
    figsize: tuple[float, float] = (12, 6),
    output_path: Path | None = None,
) -> bytes:
    """生成土地利用类型等级分布堆叠图

    Args:
        df_clean: 清洗后的样点数据 DataFrame
        attr_key: 属性代码
        attr_name: 属性名称
        grade_order: 等级顺序列表
        classify_func: 分级函数，签名为 (pd.Series, str) -> pd.Series
        theme: 主题配置
        figsize: 图表尺寸
        output_path: 输出路径

    Returns:
        bytes: PNG 图片数据
    """
    ensure_chinese_font()
    if theme is None:
        theme = get_theme()

    if df_clean.empty or "一级" not in df_clean.columns:
        return _create_empty_chart(
            f"{attr_name}土地利用分布", theme, figsize, output_path
        )

    df = df_clean.copy()

    # 添加等级列（如果不存在）
    if "等级" not in df.columns:
        df["等级"] = classify_func(df[attr_key], attr_key)

    # 按一级土地利用类型和等级统计
    grouped = df.groupby(["一级", "等级"], observed=True).size().unstack(fill_value=0)

    # 确保等级顺序
    existing_grades = [g for g in grade_order if g in grouped.columns]
    if not existing_grades:
        return _create_empty_chart(
            f"{attr_name}土地利用分布", theme, figsize, output_path
        )

    grouped = grouped[existing_grades]

    # 转换为百分比
    row_sums = grouped.sum(axis=1)
    grouped_pct = grouped.div(row_sums, axis=0) * 100

    # 准备数据
    result_df = grouped_pct.reset_index()
    result_df.columns = ["土地类型"] + existing_grades

    return make_stacked_bar_chart(
        result_df,
        f"不同土地利用类型{attr_name}等级分布",
        x_col="土地类型",
        stack_cols=existing_grades,
        ylabel="占比(%)",
        theme=theme,
        figsize=figsize,
        show_percent=False,  # 数据已经是百分比
        output_path=output_path,
    )


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
