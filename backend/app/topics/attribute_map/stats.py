"""统计计算函数"""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from app.core.data import get_pinyin_sort_key
from app.topics.attribute_map.config import (
    SOIL_ATTR_CONFIG,
    classify_series,
)


@dataclass
class AttributeStats:
    """属性统计结果缓存"""

    attr_key: str
    attr_name: str
    unit: str

    # 全局统计
    sample_total: int
    sample_mean: float
    sample_median: float
    sample_min: float
    sample_max: float
    area_total: float
    area_mean: float
    area_median: float
    area_min: float
    area_max: float

    # 按等级统计
    grade_sample_counts: dict[str, int]
    grade_area_sums: dict[str, float]

    # 按乡镇统计
    town_stats: pd.DataFrame

    # 按土壤类型统计
    soil_type_stats: pd.DataFrame

    # 原始过滤后的数据（用于土地利用类型统计）
    df_sample_clean: pd.DataFrame
    df_area_clean: pd.DataFrame


def compute_attribute_stats(
    df_sample: pd.DataFrame,
    df_area: pd.DataFrame,
    attr_key: str,
    grade_order: list[str],
) -> AttributeStats:
    """预计算单个属性的所有统计结果

    使用 groupby 聚合一次性计算所有分组统计，避免重复过滤和迭代
    """
    config = SOIL_ATTR_CONFIG[attr_key]
    attr_name = config["name"]
    unit = config["unit"]

    # 过滤有效数据（只做一次）
    sample_valid = df_sample[attr_key] > 0
    area_valid = df_area[attr_key] > 0

    df_s = df_sample.loc[sample_valid].copy()
    df_a = df_area.loc[area_valid].copy()

    # 添加等级分类（向量化）
    if len(df_s) > 0:
        df_s["等级"] = classify_series(df_s[attr_key], attr_key)
    else:
        df_s["等级"] = pd.Series(dtype=str)

    if len(df_a) > 0:
        df_a["等级"] = classify_series(df_a[attr_key], attr_key)
    else:
        df_a["等级"] = pd.Series(dtype=str)

    # 全局统计
    sample_vals = df_s[attr_key]
    area_vals = df_a[attr_key]

    sample_total = len(sample_vals)
    sample_mean = sample_vals.mean() if sample_total > 0 else 0
    sample_median = sample_vals.median() if sample_total > 0 else 0
    sample_min = sample_vals.min() if sample_total > 0 else 0
    sample_max = sample_vals.max() if sample_total > 0 else 0

    area_total = df_a["面积"].sum() if "面积" in df_a.columns and len(df_a) > 0 else 0
    area_mean = area_vals.mean() if len(area_vals) > 0 else 0
    area_median = area_vals.median() if len(area_vals) > 0 else 0
    area_min = area_vals.min() if len(area_vals) > 0 else 0
    area_max = area_vals.max() if len(area_vals) > 0 else 0

    # 按等级统计
    grade_sample_counts = dict.fromkeys(grade_order, 0)
    if len(df_s) > 0:
        counts = df_s["等级"].value_counts()
        for g in grade_order:
            grade_sample_counts[g] = int(counts.get(g, 0))

    grade_area_sums = dict.fromkeys(grade_order, 0.0)
    if len(df_a) > 0 and "面积" in df_a.columns:
        area_by_grade = df_a.groupby("等级", observed=True)["面积"].sum()
        for g in grade_order:
            grade_area_sums[g] = float(area_by_grade.get(g, 0))

    # 按乡镇统计
    town_stats = _compute_town_stats(df_s, df_a, attr_key, grade_order)

    # 按土壤类型统计
    soil_type_stats = _compute_soil_type_stats(df_s, df_a, attr_key)

    return AttributeStats(
        attr_key=attr_key,
        attr_name=attr_name,
        unit=unit,
        sample_total=sample_total,
        sample_mean=sample_mean,
        sample_median=sample_median,
        sample_min=sample_min,
        sample_max=sample_max,
        area_total=area_total,
        area_mean=area_mean,
        area_median=area_median,
        area_min=area_min,
        area_max=area_max,
        grade_sample_counts=grade_sample_counts,
        grade_area_sums=grade_area_sums,
        town_stats=town_stats,
        soil_type_stats=soil_type_stats,
        df_sample_clean=df_s,
        df_area_clean=df_a,
    )


def _compute_town_stats(
    df_s: pd.DataFrame, df_a: pd.DataFrame, attr_key: str, grade_order: list[str]
) -> pd.DataFrame:
    """计算乡镇统计（使用 groupby 聚合）"""
    # 收集所有乡镇
    towns = set()
    if "行政区名称" in df_s.columns:
        towns.update(df_s["行政区名称"].dropna().unique())
    if "行政区名称" in df_a.columns:
        towns.update(df_a["行政区名称"].dropna().unique())
    towns = sorted(towns, key=get_pinyin_sort_key) if towns else []

    if not towns:
        return pd.DataFrame()

    # 样点统计：按乡镇分组
    sample_stats = {}
    if "行政区名称" in df_s.columns and len(df_s) > 0:
        grouped_s = df_s.groupby("行政区名称", observed=True)
        sample_stats = {
            "count": grouped_s.size(),
            "mean": grouped_s[attr_key].mean(),
        }

    # 面积统计：按乡镇和等级分组
    area_stats = {}
    grade_area_by_town = {}
    if "行政区名称" in df_a.columns and "面积" in df_a.columns and len(df_a) > 0:
        grouped_a = df_a.groupby("行政区名称", observed=True)
        area_stats = {"area": grouped_a["面积"].sum()}

        if "等级" in df_a.columns:
            # 按乡镇和等级双重分组
            grade_grouped = df_a.groupby(["行政区名称", "等级"], observed=True)[
                "面积"
            ].sum()
            grade_area_by_town = grade_grouped.unstack(fill_value=0)

    results = []
    for town in towns:
        row = {"乡镇": town}
        row["样点数"] = (
            int(sample_stats["count"].get(town, 0)) if "count" in sample_stats else 0
        )
        row["均值"] = (
            sample_stats["mean"].get(town, np.nan) if "mean" in sample_stats else np.nan
        )
        row["面积"] = area_stats["area"].get(town, 0) if "area" in area_stats else 0

        # 各等级占比
        total_area = row["面积"]
        for g in grade_order:
            if (
                isinstance(grade_area_by_town, pd.DataFrame)
                and town in grade_area_by_town.index
                and g in grade_area_by_town.columns
            ):
                grade_area = grade_area_by_town.loc[town, g]
                row[f"{g}_pct"] = grade_area / total_area * 100 if total_area > 0 else 0
            else:
                row[f"{g}_pct"] = 0

        results.append(row)

    return pd.DataFrame(results)


def _compute_soil_type_stats(
    df_s: pd.DataFrame, df_a: pd.DataFrame, attr_key: str
) -> pd.DataFrame:
    """计算土壤类型统计（使用 groupby 聚合）"""
    # 检查必要列
    has_yl_ts_s = "YL" in df_s.columns and "TS" in df_s.columns
    has_yl_ts_a = "YL" in df_a.columns and "TS" in df_a.columns

    if not has_yl_ts_s and not has_yl_ts_a:
        return pd.DataFrame()

    # 样点统计：按 YL, TS 分组聚合
    sample_agg = pd.DataFrame()
    if has_yl_ts_s and len(df_s) > 0:
        df_s_valid = df_s.dropna(subset=["YL", "TS"])
        if len(df_s_valid) > 0:
            grouped = df_s_valid.groupby(["YL", "TS"], observed=True)[attr_key]
            sample_agg = grouped.agg(
                ["mean", "median", "min", "max", "count"]
            ).reset_index()
            sample_agg.columns = [
                "YL",
                "TS",
                "sample_mean",
                "sample_median",
                "sample_min",
                "sample_max",
                "sample_count",
            ]

    # 面积统计：按 YL, TS 分组聚合
    area_agg = pd.DataFrame()
    if has_yl_ts_a and "面积" in df_a.columns and len(df_a) > 0:
        df_a_valid = df_a.dropna(subset=["YL", "TS"])
        if len(df_a_valid) > 0:
            grouped = df_a_valid.groupby(["YL", "TS"], observed=True)
            area_agg = grouped.agg({attr_key: ["mean", "min", "max"], "面积": "sum"})
            area_agg.columns = ["area_mean", "area_min", "area_max", "area_sum"]
            area_agg = area_agg.reset_index()

    # 合并样点和面积统计
    if len(sample_agg) > 0 and len(area_agg) > 0:
        result = pd.merge(sample_agg, area_agg, on=["YL", "TS"], how="outer")
    elif len(sample_agg) > 0:
        result = sample_agg
    elif len(area_agg) > 0:
        result = area_agg
    else:
        return pd.DataFrame()

    return result
