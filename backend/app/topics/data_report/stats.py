"""统计计算模块

提供各维度统计计算功能：
- 全域统计
- 分乡镇统计
- 土地利用类型统计
- 土壤类型统计
- 样点统计
"""

from dataclasses import dataclass, field

import pandas as pd
from pypinyin import lazy_pinyin

from app.topics.data_report.classifiers import (
    calculate_weighted_average_grade,
    classify_series,
    classify_value,
)
from app.topics.data_report.config import (
    SOIL_ATTR_CONFIG,
    get_grade_order,
)
from app.topics.data_report.land_use import add_land_use_columns, get_land_use_structure
from app.topics.data_report.soil_type import (
    add_soil_type_columns,
    get_soil_type_sort_key,
)


@dataclass
class GradeStats:
    """等级统计数据"""

    grade: str
    area: float = 0.0
    count: int = 0
    percentage: float = 0.0


@dataclass
class TownStats:
    """乡镇统计数据"""

    town: str
    grade_stats: dict[str, GradeStats] = field(default_factory=dict)
    total_area: float = 0.0
    avg_grade: float | None = None
    # 样点统计
    sample_count: int = 0
    sample_mean: float = 0.0
    sample_min: float = 0.0
    sample_max: float = 0.0
    sample_percentage: float = 0.0


@dataclass
class LandUseStats:
    """土地利用类型统计数据"""

    primary: str
    secondary: str
    grade_stats: dict[str, GradeStats] = field(default_factory=dict)
    total_area: float = 0.0
    avg_grade: float | None = None
    # 样点统计
    sample_count: int = 0
    sample_mean: float = 0.0
    sample_min: float = 0.0
    sample_max: float = 0.0
    sample_percentage: float = 0.0


@dataclass
class SoilTypeStats:
    """土壤类型统计数据"""

    major: str  # 土类
    sub: str  # 亚类
    genus: str  # 土属
    grade_stats: dict[str, GradeStats] = field(default_factory=dict)
    total_area: float = 0.0
    avg_grade: float | None = None
    # 样点统计
    sample_count: int = 0
    sample_mean: float = 0.0
    sample_min: float = 0.0
    sample_max: float = 0.0
    sample_percentage: float = 0.0


@dataclass
class AttributeStatsSummary:
    """属性统计汇总"""

    attr_key: str
    attr_name: str
    unit: str

    # 全域统计
    total_area: float = 0.0
    total_samples: int = 0
    global_mean: float = 0.0
    global_median: float = 0.0
    global_min: float = 0.0
    global_max: float = 0.0
    global_std: float = 0.0
    global_cv: float = 0.0  # 变异系数
    global_avg_grade: float | None = None

    # 全域等级统计
    grade_stats: dict[str, GradeStats] = field(default_factory=dict)

    # 分乡镇统计
    town_stats: list[TownStats] = field(default_factory=list)

    # 土地利用类型统计
    land_use_stats: list[LandUseStats] = field(default_factory=list)

    # 土壤类型统计
    soil_type_stats: list[SoilTypeStats] = field(default_factory=list)

    # 百分位数
    percentiles: dict[str, float] = field(default_factory=dict)


def get_pinyin_sort_key(text: str) -> str:
    """获取拼音排序键"""
    if pd.isna(text):
        return ""
    return "".join(lazy_pinyin(str(text))).lower()


def compute_attribute_stats(
    df_mapping: pd.DataFrame | None,
    df_sample: pd.DataFrame | None,
    attr_key: str,
) -> AttributeStatsSummary:
    """计算单个属性的完整统计

    Args:
        df_mapping: 制图数据（用于面积统计）
        df_sample: 样点数据（用于样点统计）
        attr_key: 属性键名

    Returns:
        属性统计汇总
    """
    config = SOIL_ATTR_CONFIG[attr_key]
    attr_name = config["name"]
    unit = config["unit"]
    grade_order = get_grade_order(attr_key)

    summary = AttributeStatsSummary(
        attr_key=attr_key,
        attr_name=attr_name,
        unit=unit,
    )

    # 初始化等级统计
    for grade in grade_order:
        summary.grade_stats[grade] = GradeStats(grade=grade)

    # 处理制图数据
    if df_mapping is not None and attr_key in df_mapping.columns:
        df_m = _prepare_mapping_data(df_mapping, attr_key)
        _compute_mapping_stats(summary, df_m, attr_key, grade_order)

    # 处理样点数据
    if df_sample is not None and attr_key in df_sample.columns:
        df_s = _prepare_sample_data(df_sample, attr_key)
        _compute_sample_stats(summary, df_s, attr_key, grade_order)

    return summary


def _prepare_mapping_data(df: pd.DataFrame, attr_key: str) -> pd.DataFrame:
    """准备制图数据"""
    df = df.copy()
    df[attr_key] = pd.to_numeric(df[attr_key], errors="coerce")
    df = df[df[attr_key] > 0].copy()

    if df.empty:
        return df

    # 添加等级列
    df["等级"] = classify_series(df[attr_key], attr_key)

    # 添加土地利用分类
    df = add_land_use_columns(df)

    # 添加土壤类型
    df = add_soil_type_columns(df)

    return df


def _prepare_sample_data(df: pd.DataFrame, attr_key: str) -> pd.DataFrame:
    """准备样点数据"""
    df = df.copy()
    df[attr_key] = pd.to_numeric(df[attr_key], errors="coerce")
    df = df[df[attr_key] > 0].copy()

    if df.empty:
        return df

    # 添加等级列
    df["等级"] = classify_series(df[attr_key], attr_key)

    # 添加土地利用分类
    df = add_land_use_columns(df)

    # 添加土壤类型
    df = add_soil_type_columns(df)

    return df


def _compute_mapping_stats(
    summary: AttributeStatsSummary,
    df: pd.DataFrame,
    attr_key: str,
    grade_order: list[str],
) -> None:
    """计算制图数据统计"""
    if df.empty:
        return

    # 检查面积列
    if "面积" not in df.columns:
        return

    # 全域面积统计
    summary.total_area = df["面积"].sum()
    summary.global_avg_grade = calculate_weighted_average_grade(df, attr_key)

    # 全域等级统计
    grade_areas = df.groupby("等级")["面积"].sum()
    for grade in grade_order:
        area = grade_areas.get(grade, 0)
        pct = (area / summary.total_area * 100) if summary.total_area > 0 else 0
        summary.grade_stats[grade].area = area
        summary.grade_stats[grade].percentage = pct

    # 分乡镇统计
    _compute_town_mapping_stats(summary, df, attr_key, grade_order)

    # 土地利用类型统计
    _compute_land_use_mapping_stats(summary, df, attr_key, grade_order)

    # 土壤类型统计
    _compute_soil_type_mapping_stats(summary, df, attr_key, grade_order)


def _compute_sample_stats(
    summary: AttributeStatsSummary,
    df: pd.DataFrame,
    attr_key: str,
    grade_order: list[str],
) -> None:
    """计算样点数据统计"""
    if df.empty:
        return

    values = df[attr_key]
    summary.total_samples = len(df)
    summary.global_mean = values.mean()
    summary.global_median = values.median()
    summary.global_min = values.min()
    summary.global_max = values.max()
    summary.global_std = values.std()
    summary.global_cv = (
        summary.global_std / summary.global_mean if summary.global_mean != 0 else 0
    )

    # 全域等级样点统计
    grade_counts = df["等级"].value_counts()
    for grade in grade_order:
        count = grade_counts.get(grade, 0)
        pct = (count / summary.total_samples * 100) if summary.total_samples > 0 else 0
        summary.grade_stats[grade].count = int(count)
        if summary.grade_stats[grade].percentage == 0:
            summary.grade_stats[grade].percentage = pct

    # 百分位数
    percentile_list = [0.02, 0.05, 0.10, 0.20, 0.80, 0.90, 0.95, 0.98]
    for p in percentile_list:
        label = f"{int(p * 100)}%"
        summary.percentiles[label] = values.quantile(p)

    # 分乡镇样点统计
    _compute_town_sample_stats(summary, df, attr_key)

    # 土地利用类型样点统计
    _compute_land_use_sample_stats(summary, df, attr_key)

    # 土壤类型样点统计
    _compute_soil_type_sample_stats(summary, df, attr_key)


def _compute_town_mapping_stats(
    summary: AttributeStatsSummary,
    df: pd.DataFrame,
    attr_key: str,
    grade_order: list[str],
) -> None:
    """计算分乡镇制图统计"""
    town_col = _find_town_column(df)
    if town_col is None:
        return

    towns = sorted(
        [t for t in df[town_col].dropna().unique() if t and str(t).strip()],
        key=get_pinyin_sort_key,
    )

    for town in towns:
        town_df = df[df[town_col] == town]
        stats = TownStats(town=town)

        for grade in grade_order:
            stats.grade_stats[grade] = GradeStats(grade=grade)

        stats.total_area = town_df["面积"].sum()

        grade_areas = town_df.groupby("等级")["面积"].sum()
        for grade in grade_order:
            area = grade_areas.get(grade, 0)
            pct = (area / stats.total_area * 100) if stats.total_area > 0 else 0
            stats.grade_stats[grade].area = area
            stats.grade_stats[grade].percentage = pct

        stats.avg_grade = calculate_weighted_average_grade(town_df, attr_key)
        summary.town_stats.append(stats)


def _compute_town_sample_stats(
    summary: AttributeStatsSummary,
    df: pd.DataFrame,
    attr_key: str,
) -> None:
    """计算分乡镇样点统计"""
    town_col = _find_town_column(df)
    if town_col is None:
        return

    towns = sorted(
        [t for t in df[town_col].dropna().unique() if t and str(t).strip()],
        key=get_pinyin_sort_key,
    )

    # 查找或创建town_stats
    town_stats_map = {ts.town: ts for ts in summary.town_stats}

    for town in towns:
        town_df = df[df[town_col] == town]
        values = town_df[attr_key]

        if town in town_stats_map:
            stats = town_stats_map[town]
        else:
            stats = TownStats(town=town)
            summary.town_stats.append(stats)

        stats.sample_count = len(town_df)
        stats.sample_mean = values.mean() if len(values) > 0 else 0
        stats.sample_min = values.min() if len(values) > 0 else 0
        stats.sample_max = values.max() if len(values) > 0 else 0
        stats.sample_percentage = (
            (stats.sample_count / summary.total_samples * 100)
            if summary.total_samples > 0
            else 0
        )


def _compute_land_use_mapping_stats(
    summary: AttributeStatsSummary,
    df: pd.DataFrame,
    attr_key: str,
    grade_order: list[str],
) -> None:
    """计算土地利用类型制图统计"""
    land_structure = get_land_use_structure()

    for primary_type, secondaries in land_structure:
        primary_df = df[df["一级地类"] == primary_type]

        if secondaries:
            # 一级地类汇总
            primary_stats = LandUseStats(primary=primary_type, secondary="")
            for grade in grade_order:
                primary_stats.grade_stats[grade] = GradeStats(grade=grade)
            primary_stats.total_area = primary_df["面积"].sum()

            if primary_stats.total_area > 0:
                grade_areas = primary_df.groupby("等级")["面积"].sum()
                for grade in grade_order:
                    area = grade_areas.get(grade, 0)
                    pct = area / primary_stats.total_area * 100
                    primary_stats.grade_stats[grade].area = area
                    primary_stats.grade_stats[grade].percentage = pct
                primary_stats.avg_grade = calculate_weighted_average_grade(
                    primary_df, attr_key
                )

            summary.land_use_stats.append(primary_stats)

            # 二级地类
            for secondary_type in secondaries:
                secondary_df = primary_df[primary_df["二级地类"] == secondary_type]
                stats = LandUseStats(primary=primary_type, secondary=secondary_type)

                for grade in grade_order:
                    stats.grade_stats[grade] = GradeStats(grade=grade)

                stats.total_area = secondary_df["面积"].sum()

                if stats.total_area > 0:
                    grade_areas = secondary_df.groupby("等级")["面积"].sum()
                    for grade in grade_order:
                        area = grade_areas.get(grade, 0)
                        pct = area / stats.total_area * 100
                        stats.grade_stats[grade].area = area
                        stats.grade_stats[grade].percentage = pct
                    stats.avg_grade = calculate_weighted_average_grade(
                        secondary_df, attr_key
                    )

                summary.land_use_stats.append(stats)
        else:
            # 无二级地类
            stats = LandUseStats(primary=primary_type, secondary="")
            for grade in grade_order:
                stats.grade_stats[grade] = GradeStats(grade=grade)

            stats.total_area = primary_df["面积"].sum()

            if stats.total_area > 0:
                grade_areas = primary_df.groupby("等级")["面积"].sum()
                for grade in grade_order:
                    area = grade_areas.get(grade, 0)
                    pct = area / stats.total_area * 100
                    stats.grade_stats[grade].area = area
                    stats.grade_stats[grade].percentage = pct
                stats.avg_grade = calculate_weighted_average_grade(primary_df, attr_key)

            summary.land_use_stats.append(stats)


def _compute_land_use_sample_stats(
    summary: AttributeStatsSummary,
    df: pd.DataFrame,
    attr_key: str,
) -> None:
    """计算土地利用类型样点统计"""
    land_structure = get_land_use_structure()

    # 查找或创建land_use_stats
    land_stats_map = {
        (ls.primary, ls.secondary): ls for ls in summary.land_use_stats
    }

    for primary_type, secondaries in land_structure:
        primary_df = df[df["一级地类"] == primary_type]

        if secondaries:
            # 一级地类汇总
            key = (primary_type, "")
            if key in land_stats_map:
                stats = land_stats_map[key]
            else:
                stats = LandUseStats(primary=primary_type, secondary="")
                summary.land_use_stats.append(stats)

            values = primary_df[attr_key]
            stats.sample_count = len(primary_df)
            stats.sample_mean = values.mean() if len(values) > 0 else 0
            stats.sample_min = values.min() if len(values) > 0 else 0
            stats.sample_max = values.max() if len(values) > 0 else 0
            stats.sample_percentage = (
                (stats.sample_count / summary.total_samples * 100)
                if summary.total_samples > 0
                else 0
            )

            # 二级地类
            for secondary_type in secondaries:
                secondary_df = primary_df[primary_df["二级地类"] == secondary_type]
                key = (primary_type, secondary_type)

                if key in land_stats_map:
                    stats = land_stats_map[key]
                else:
                    stats = LandUseStats(primary=primary_type, secondary=secondary_type)
                    summary.land_use_stats.append(stats)

                values = secondary_df[attr_key]
                stats.sample_count = len(secondary_df)
                stats.sample_mean = values.mean() if len(values) > 0 else 0
                stats.sample_min = values.min() if len(values) > 0 else 0
                stats.sample_max = values.max() if len(values) > 0 else 0
                stats.sample_percentage = (
                    (stats.sample_count / summary.total_samples * 100)
                    if summary.total_samples > 0
                    else 0
                )
        else:
            # 无二级地类
            key = (primary_type, "")
            if key in land_stats_map:
                stats = land_stats_map[key]
            else:
                stats = LandUseStats(primary=primary_type, secondary="")
                summary.land_use_stats.append(stats)

            values = primary_df[attr_key]
            stats.sample_count = len(primary_df)
            stats.sample_mean = values.mean() if len(values) > 0 else 0
            stats.sample_min = values.min() if len(values) > 0 else 0
            stats.sample_max = values.max() if len(values) > 0 else 0
            stats.sample_percentage = (
                (stats.sample_count / summary.total_samples * 100)
                if summary.total_samples > 0
                else 0
            )


def _compute_soil_type_mapping_stats(
    summary: AttributeStatsSummary,
    df: pd.DataFrame,
    attr_key: str,
    grade_order: list[str],
) -> None:
    """计算土壤类型制图统计"""
    # 过滤有效土壤类型
    valid_df = df[
        df["亚类"].notna()
        & (df["亚类"] != "")
        & df["土属"].notna()
        & (df["土属"] != "")
    ]

    if valid_df.empty:
        return

    # 按土壤类型分组
    grouped = valid_df.groupby(["土类", "亚类", "土属"])

    soil_stats_list: list[SoilTypeStats] = []

    for (major, sub, genus), group_df in grouped:
        major = str(major) if pd.notna(major) and major != "" else "未分类"
        sub = str(sub)
        genus = str(genus)

        stats = SoilTypeStats(major=major, sub=sub, genus=genus)

        for grade in grade_order:
            stats.grade_stats[grade] = GradeStats(grade=grade)

        stats.total_area = group_df["面积"].sum()

        if stats.total_area > 0:
            grade_areas = group_df.groupby("等级")["面积"].sum()
            for grade in grade_order:
                area = grade_areas.get(grade, 0)
                pct = area / stats.total_area * 100
                stats.grade_stats[grade].area = area
                stats.grade_stats[grade].percentage = pct
            stats.avg_grade = calculate_weighted_average_grade(group_df, attr_key)

        soil_stats_list.append(stats)

    # 按土壤类型顺序排序
    soil_stats_list.sort(key=lambda s: get_soil_type_sort_key(s.major, s.sub, s.genus))
    summary.soil_type_stats = soil_stats_list


def _compute_soil_type_sample_stats(
    summary: AttributeStatsSummary,
    df: pd.DataFrame,
    attr_key: str,
) -> None:
    """计算土壤类型样点统计"""
    # 过滤有效土壤类型
    valid_df = df[
        df["亚类"].notna()
        & (df["亚类"] != "")
        & df["土属"].notna()
        & (df["土属"] != "")
    ]

    if valid_df.empty:
        return

    # 按土壤类型分组
    grouped = valid_df.groupby(["土类", "亚类", "土属"])

    # 查找或创建soil_type_stats
    soil_stats_map = {
        (ss.major, ss.sub, ss.genus): ss for ss in summary.soil_type_stats
    }

    new_stats_list: list[SoilTypeStats] = []

    for (major, sub, genus), group_df in grouped:
        major = str(major) if pd.notna(major) and major != "" else "未分类"
        sub = str(sub)
        genus = str(genus)

        key = (major, sub, genus)
        if key in soil_stats_map:
            stats = soil_stats_map[key]
        else:
            stats = SoilTypeStats(major=major, sub=sub, genus=genus)
            new_stats_list.append(stats)

        values = group_df[attr_key]
        stats.sample_count = len(group_df)
        stats.sample_mean = values.mean() if len(values) > 0 else 0
        stats.sample_min = values.min() if len(values) > 0 else 0
        stats.sample_max = values.max() if len(values) > 0 else 0
        stats.sample_percentage = (
            (stats.sample_count / summary.total_samples * 100)
            if summary.total_samples > 0
            else 0
        )

    # 合并并排序
    if new_stats_list:
        summary.soil_type_stats.extend(new_stats_list)
        summary.soil_type_stats.sort(
            key=lambda s: get_soil_type_sort_key(s.major, s.sub, s.genus)
        )


def _find_town_column(df: pd.DataFrame) -> str | None:
    """查找乡镇列"""
    for col in ["行政区名称", "乡镇", "镇/街道", "街道", "行政区"]:
        if col in df.columns:
            return col
    return None
