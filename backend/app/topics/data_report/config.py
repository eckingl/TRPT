"""土壤属性分级配置

从分级标准模块加载配置，支持多套标准切换。
"""

from typing import TypedDict

import pandas as pd

from app.core.grading_standards import AttrGradeConfig, get_attr_config


class LevelConfig(TypedDict):
    """级别配置类型"""

    threshold: float
    level: str
    description: str


# 为了向后兼容，保留 AttrConfig 类型别名
AttrConfig = AttrGradeConfig

# 罗马数字映射
ROMAN_MAP: dict[str, str] = {
    "1级": "Ⅰ级",
    "2级": "Ⅱ级",
    "3级": "Ⅲ级",
    "4级": "Ⅳ级",
    "5级": "Ⅴ级",
    "6级": "Ⅵ级",
    "7级": "Ⅶ级",
}

# 所有罗马数字级别（按顺序）
ALL_ROMAN_GRADES: list[str] = ["Ⅰ级", "Ⅱ级", "Ⅲ级", "Ⅳ级", "Ⅴ级", "Ⅵ级", "Ⅶ级"]


def get_soil_attr_config() -> dict[str, AttrConfig]:
    """获取当前分级标准的土壤属性配置"""
    return get_attr_config()


# 土壤属性分级配置（从分级标准模块获取）
SOIL_ATTR_CONFIG: dict[str, AttrConfig] = get_attr_config()

# 土地利用类型配置
LAND_USE_CONFIG: dict[str, list[str]] = {
    "耕地": ["水田", "水浇地", "旱地"],
    "园地": ["果园", "茶园", "其他园地"],
    "林地": ["林地"],
    "草地": ["草地"],
    "其他": ["其他"],
}

# 土地利用类型结构（用于表格输出）
LAND_USE_STRUCTURE: list[tuple[str, list[str]]] = [
    ("耕地", ["水田", "水浇地", "旱地"]),
    ("园地", ["果园", "茶园", "其他园地"]),
    ("林地", []),
    ("草地", []),
    ("其他", []),
]

# 列名别名映射
COLUMN_ALIAS_MAP: dict[str, str] = {
    "pH": "ph",
    "PH": "ph",
    "酸碱度": "ph",
    "有机质含量": "OM",
    "有机质(g/kg)": "OM",
    "全氮含量": "TN",
    "有效磷(P)": "AP",
    "速效钾(K)": "AK",
    "阳离子交换量(CEC)": "CEC",
}


def normalize_attr_column_name(col_name: str) -> str:
    """将原始列名映射为标准键

    Args:
        col_name: 原始列名

    Returns:
        标准化后的键名
    """
    if pd.isna(col_name):
        return ""
    col_str = str(col_name).strip()

    # 先查别名
    if col_str in COLUMN_ALIAS_MAP:
        return COLUMN_ALIAS_MAP[col_str]

    # 再直接匹配（不区分大小写）
    for key in SOIL_ATTR_CONFIG:
        if col_str.lower() == key.lower():
            return key

    return col_str


def get_grade_order(attr_key: str) -> list[str]:
    """获取属性级别的排序列表

    Args:
        attr_key: 属性键名

    Returns:
        罗马数字级别列表
    """
    config = SOIL_ATTR_CONFIG.get(attr_key)
    if not config:
        return ALL_ROMAN_GRADES[:5]

    levels = config.get("levels", [])
    grade_set = set()
    for _, level, _ in levels:
        roman_level = ROMAN_MAP.get(level, level)
        grade_set.add(roman_level)

    return [g for g in ALL_ROMAN_GRADES if g in grade_set]


def get_grade_ranges(attr_key: str) -> dict[str, str]:
    """获取属性各级别的数值范围

    Args:
        attr_key: 属性键名

    Returns:
        {罗马数字级别: 范围字符串} 字典
    """
    config = SOIL_ATTR_CONFIG.get(attr_key)
    if not config:
        return {}

    levels = config["levels"]
    ranges: dict[str, str] = {}

    for i, (threshold, level, _) in enumerate(levels):
        roman_level = ROMAN_MAP.get(level, level)

        if i == 0:
            ranges[roman_level] = f"≤{threshold}"
        elif threshold == float("inf"):
            prev_threshold = levels[i - 1][0]
            ranges[roman_level] = f">{prev_threshold}"
        else:
            prev_threshold = levels[i - 1][0]
            ranges[roman_level] = f"{prev_threshold}～{threshold}"

    return ranges


def detect_available_attributes(columns: list[str]) -> list[tuple[str, str]]:
    """检测DataFrame列中可用的土壤属性

    Args:
        columns: 列名列表

    Returns:
        [(原始列名, 标准键), ...] 列表
    """
    available: list[tuple[str, str]] = []
    config_keys = set(SOIL_ATTR_CONFIG.keys())

    for col in columns:
        norm_key = normalize_attr_column_name(col)
        if norm_key in config_keys:
            available.append((col, norm_key))

    return available
