"""数据分级与分类工具

提供土壤属性分级、数值格式化等工具函数。
"""

import math

import numpy as np
import pandas as pd

from app.topics.data_report.config import ROMAN_MAP, SOIL_ATTR_CONFIG


def classify_value(value: float, attr_key: str) -> str | None:
    """根据配置对属性值进行分级

    分级规则：
    - 第一级：value ≤ threshold1
    - 中间级：prev_threshold < value ≤ threshold
    - 最后一级：value > last_threshold

    Args:
        value: 属性值
        attr_key: 属性键名

    Returns:
        罗马数字级别，无效值返回None
    """
    if pd.isna(value) or value <= 0:
        return None

    config = SOIL_ATTR_CONFIG.get(attr_key)
    if not config:
        return None

    levels = config["levels"]

    for i, (threshold, level, _) in enumerate(levels):
        if i == 0:
            if value <= threshold:
                return ROMAN_MAP.get(level, level)
        else:
            prev_threshold = levels[i - 1][0]
            if prev_threshold < value <= threshold:
                return ROMAN_MAP.get(level, level)

    return None


def classify_series(values: pd.Series, attr_key: str) -> pd.Series:
    """向量化的属性分级

    使用numpy进行向量化操作，提高大数据集处理效率。

    Args:
        values: 属性值Series
        attr_key: 属性键名

    Returns:
        分级结果Series
    """
    config = SOIL_ATTR_CONFIG.get(attr_key)
    if not config:
        return pd.Series([None] * len(values), index=values.index, dtype=object)

    numeric = pd.to_numeric(values, errors="coerce")
    valid_mask = numeric.notna() & (numeric > 0)

    result = pd.Series([None] * len(values), index=values.index, dtype=object)
    if not valid_mask.any():
        return result

    thresholds = np.array([float(th[0]) for th in config["levels"]], dtype=float)
    levels = [lvl for _, lvl, _ in config["levels"]]

    valid_values = numeric[valid_mask].values.astype(float)
    idx = np.searchsorted(thresholds, valid_values, side="right")
    idx = np.clip(idx, 0, len(levels) - 1)

    level_arr = [ROMAN_MAP.get(levels[i], levels[i]) for i in idx]
    result.loc[valid_mask] = level_arr

    return result


def format_small_value(value: float) -> float:
    """格式化小数值

    - 大于等于 0.001: 显示3位小数
    - 小于 0.001: 显示到第一位非零数字

    Args:
        value: 数值

    Returns:
        格式化后的数值
    """
    if pd.isna(value) or value == 0:
        return round(value, 3) if not pd.isna(value) else value

    abs_val = abs(value)

    if abs_val >= 0.001:
        return round(value, 3)

    # 计算需要保留的小数位数
    decimal_places = -int(math.floor(math.log10(abs_val)))
    return round(value, decimal_places)


def format_percentage(value: float) -> float:
    """格式化百分比数值

    - 超过100显示100
    - 否则按format_small_value逻辑处理

    Args:
        value: 数值

    Returns:
        格式化后的数值
    """
    if pd.isna(value):
        return value

    if value > 100:
        return 100

    return format_small_value(value)


def calculate_weighted_average_grade(
    df: pd.DataFrame,
    attr_key: str,
    area_col: str = "面积",
) -> float | None:
    """计算加权平均等级

    根据面积加权计算平均等级。

    Args:
        df: 数据框
        attr_key: 属性键名
        area_col: 面积列名

    Returns:
        加权平均等级，无有效数据返回None
    """
    grade_map = {
        "Ⅰ级": 1,
        "Ⅱ级": 2,
        "Ⅲ级": 3,
        "Ⅳ级": 4,
        "Ⅴ级": 5,
        "Ⅵ级": 6,
        "Ⅶ级": 7,
    }

    df = df.copy()
    df[attr_key] = pd.to_numeric(df[attr_key], errors="coerce")

    valid_df = df[(df[attr_key] > 0) & (df[area_col].notna()) & (df[area_col] > 0)]

    if valid_df.empty:
        return None

    # 分级
    valid_df = valid_df.copy()
    valid_df["等级"] = valid_df[attr_key].apply(lambda x: classify_value(x, attr_key))
    valid_df["等级数值"] = valid_df["等级"].map(grade_map)

    valid_df = valid_df[valid_df["等级数值"].notna()]
    if valid_df.empty:
        return None

    total_area = valid_df[area_col].sum()
    weighted_sum = (valid_df["等级数值"] * valid_df[area_col]).sum()

    return round(weighted_sum / total_area, 2)
