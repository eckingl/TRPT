"""土壤属性分级配置"""

import numpy as np
import pandas as pd

# 罗马数字映射
ROMAN_NUMERALS = ["Ⅰ", "Ⅱ", "Ⅲ", "Ⅳ", "Ⅴ", "Ⅵ", "Ⅶ"]

# 土壤属性分级配置
SOIL_ATTR_CONFIG: dict = {
    # ========== 盐碱相关 ==========
    "SRXYZL": {
        "name": "水溶性盐总量",
        "unit": "g/kg",
        "reverse_display": False,
        "levels": [
            (1, "1级", "无盐化"),
            (2, "2级", "轻度盐化"),
            (4, "3级", "中度盐化"),
            (6, "4级", "重度盐化"),
            (float("inf"), "5级", "盐土"),
        ],
    },
    "DDL": {
        "name": "电导率",
        "unit": "mS/cm",
        "reverse_display": False,
        "levels": [
            (0.4, "1级", "低"),
            (0.8, "2级", "较低"),
            (1.6, "3级", "中"),
            (2.4, "4级", "较高"),
            (float("inf"), "5级", "高"),
        ],
    },
    "ENA": {
        "name": "交换性钠",
        "unit": "cmol(+)/kg",
        "reverse_display": False,
        "levels": [
            (0.2, "1级", "低"),
            (0.5, "2级", "较低"),
            (0.8, "3级", "中"),
            (1.2, "4级", "较高"),
            (float("inf"), "5级", "高"),
        ],
    },
    # ========== 物理性质 ==========
    "TRRZPJZ": {
        "name": "土壤容重",
        "unit": "g/cm³",
        "reverse_display": False,
        "levels": [
            (0.9, "1级", "不适宜"),
            (1.1, "2级", "较适宜"),
            (1.35, "3级", "适宜"),
            (1.55, "4级", "较适宜"),
            (float("inf"), "5级", "不适宜"),
        ],
    },
    "GZCHD": {
        "name": "耕作层厚度",
        "unit": "cm",
        "reverse_display": True,
        "levels": [
            (10, "5级", "薄"),
            (15, "4级", "较薄"),
            (20, "3级", "中"),
            (25, "2级", "较厚"),
            (float("inf"), "1级", "厚"),
        ],
    },
    "SWXDTJT7": {
        "name": "水稳性大团聚体",
        "unit": "mg/kg",
        "reverse_display": False,
        "levels": [
            (10, "1级", "低"),
            (20, "2级", "较低"),
            (30, "3级", "中"),
            (40, "4级", "较高"),
            (float("inf"), "5级", "高"),
        ],
    },
    # ========== 养分指标 ==========
    "OM": {
        "name": "有机质",
        "unit": "g/kg",
        "reverse_display": True,
        "levels": [
            (10, "5级", "低"),
            (20, "4级", "较低"),
            (30, "3级", "中"),
            (40, "2级", "较高"),
            (float("inf"), "1级", "高"),
        ],
    },
    "TN": {
        "name": "全氮",
        "unit": "g/kg",
        "reverse_display": True,
        "levels": [
            (0.5, "5级", "极缺"),
            (1.0, "4级", "缺乏"),
            (1.5, "3级", "中等"),
            (2.0, "2级", "较丰富"),
            (float("inf"), "1级", "丰富"),
        ],
    },
    "TP": {
        "name": "全磷",
        "unit": "g/kg",
        "reverse_display": True,
        "levels": [
            (0.4, "5级", "极缺"),
            (0.6, "4级", "缺乏"),
            (0.8, "3级", "中等"),
            (1.0, "2级", "较丰富"),
            (float("inf"), "1级", "丰富"),
        ],
    },
    "TK": {
        "name": "全钾",
        "unit": "g/kg",
        "reverse_display": True,
        "levels": [
            (10, "5级", "极缺"),
            (15, "4级", "缺乏"),
            (20, "3级", "中等"),
            (25, "2级", "较丰富"),
            (float("inf"), "1级", "丰富"),
        ],
    },
    "AP": {
        "name": "有效磷",
        "unit": "mg/kg",
        "reverse_display": True,
        "levels": [
            (5, "5级", "极缺"),
            (10, "4级", "缺乏"),
            (20, "3级", "中等"),
            (40, "2级", "较丰富"),
            (float("inf"), "1级", "丰富"),
        ],
    },
    "AK": {
        "name": "速效钾",
        "unit": "mg/kg",
        "reverse_display": True,
        "levels": [
            (50, "5级", "极缺"),
            (100, "4级", "缺乏"),
            (150, "3级", "中等"),
            (200, "2级", "较丰富"),
            (float("inf"), "1级", "丰富"),
        ],
    },
    "SK": {
        "name": "缓效钾",
        "unit": "mg/kg",
        "reverse_display": True,
        "levels": [
            (100, "5级", "极缺"),
            (300, "4级", "缺乏"),
            (500, "3级", "中等"),
            (700, "2级", "较丰富"),
            (float("inf"), "1级", "丰富"),
        ],
    },
    # ========== 交换性阳离子 ==========
    "CEC": {
        "name": "阳离子交换量",
        "unit": "cmol(+)/kg",
        "reverse_display": True,
        "levels": [
            (5, "5级", "低"),
            (10, "4级", "较低"),
            (15, "3级", "中"),
            (20, "2级", "较高"),
            (float("inf"), "1级", "高"),
        ],
    },
    "ECA": {
        "name": "交换性钙",
        "unit": "cmol(1/2Ca²⁺)/kg",
        "reverse_display": True,
        "levels": [
            (1.0, "5级", "极缺"),
            (4.0, "4级", "缺乏"),
            (10.0, "3级", "中等"),
            (15.0, "2级", "丰富"),
            (float("inf"), "1级", "偏高"),
        ],
    },
    "EMG": {
        "name": "交换性镁",
        "unit": "cmol(1/2Mg²⁺)/kg",
        "reverse_display": True,
        "levels": [
            (0.5, "5级", "极缺"),
            (1.0, "4级", "缺乏"),
            (1.5, "3级", "中等"),
            (2.0, "2级", "丰富"),
            (float("inf"), "1级", "偏高"),
        ],
    },
    "EK": {
        "name": "交换性钾",
        "unit": "cmol(+)/kg",
        "reverse_display": False,
        "levels": [
            (0.1, "1级", "无效钾"),
            (0.2, "2级", "低效钾"),
            (0.4, "3级", "中效钾"),
            (float("inf"), "4级", "高效钾"),
        ],
    },
    "JHXYJZL": {
        "name": "交换性盐基总量",
        "unit": "cmol(+)/kg",
        "reverse_display": False,
        "levels": [
            (5, "1级", "低"),
            (10, "2级", "较低"),
            (15, "3级", "中"),
            (20, "4级", "较高"),
            (float("inf"), "5级", "高"),
        ],
    },
    # ========== 中微量元素 ==========
    "AS1": {
        "name": "有效硫",
        "unit": "mg/kg",
        "reverse_display": True,
        "levels": [
            (10.0, "5级", "极缺"),
            (20.0, "4级", "缺乏"),
            (30.0, "3级", "中等"),
            (40.0, "2级", "丰富"),
            (float("inf"), "1级", "偏高"),
        ],
    },
    "ASI": {
        "name": "有效硅",
        "unit": "mg/kg",
        "reverse_display": True,
        "levels": [
            (50, "5级", "极缺"),
            (100, "4级", "缺乏"),
            (150, "3级", "中等"),
            (250, "2级", "丰富"),
            (float("inf"), "1级", "偏高"),
        ],
    },
    "AFE": {
        "name": "有效铁",
        "unit": "mg/kg",
        "reverse_display": True,
        "levels": [
            (2.5, "5级", "极缺"),
            (4.5, "4级", "缺乏"),
            (10.0, "3级", "中等"),
            (20.0, "2级", "丰富"),
            (float("inf"), "1级", "偏高"),
        ],
    },
    "AMN": {
        "name": "有效锰",
        "unit": "mg/kg",
        "reverse_display": True,
        "levels": [
            (1.0, "5级", "极缺"),
            (5.0, "4级", "缺乏"),
            (15.0, "3级", "中等"),
            (30.0, "2级", "丰富"),
            (float("inf"), "1级", "偏高"),
        ],
    },
    "ACU": {
        "name": "有效铜",
        "unit": "mg/kg",
        "reverse_display": True,
        "levels": [
            (0.2, "5级", "极缺"),
            (0.5, "4级", "缺乏"),
            (1.0, "3级", "中等"),
            (2.0, "2级", "丰富"),
            (float("inf"), "1级", "偏高"),
        ],
    },
    "AZN": {
        "name": "有效锌",
        "unit": "mg/kg",
        "reverse_display": True,
        "levels": [
            (0.5, "5级", "极缺"),
            (1.0, "4级", "缺乏"),
            (2.0, "3级", "中等"),
            (3.0, "2级", "丰富"),
            (float("inf"), "1级", "偏高"),
        ],
    },
    "AB": {
        "name": "有效硼",
        "unit": "mg/kg",
        "reverse_display": True,
        "levels": [
            (0.2, "5级", "极缺"),
            (0.5, "4级", "缺乏"),
            (1.0, "3级", "中等"),
            (2.0, "2级", "丰富"),
            (float("inf"), "1级", "偏高"),
        ],
    },
    "AMO": {
        "name": "有效钼",
        "unit": "mg/kg",
        "reverse_display": True,
        "levels": [
            (0.10, "5级", "极缺"),
            (0.15, "4级", "缺乏"),
            (0.20, "3级", "中等"),
            (0.30, "2级", "丰富"),
            (float("inf"), "1级", "偏高"),
        ],
    },
    # ========== pH值 ==========
    "ph": {
        "name": "pH",
        "unit": "",
        "reverse_display": True,
        "levels": [
            (4.5, "1级", "强酸性"),
            (5.5, "2级", "酸性"),
            (6.5, "3级", "弱酸性"),
            (7.5, "4级", "中性"),
            (8.5, "5级", "弱碱性"),
            (9.0, "6级", "碱性"),
            (14.0, "7级", "强碱性"),
        ],
    },
    # ========== 机械组成分级 ==========
    "sand": {
        "name": "机械组成-砂粒",
        "unit": "%",
        "reverse_display": True,
        "levels": [
            (15, "5级", "≤15"),
            (25, "4级", "15～25"),
            (45, "3级", "25～45"),
            (65, "2级", "45～65"),
            (float("inf"), "1级", "65～100"),
        ],
    },
    "silt": {
        "name": "机械组成-粉粒",
        "unit": "%",
        "reverse_display": True,
        "levels": [
            (15, "5级", "≤15"),
            (25, "4级", "15～25"),
            (45, "3级", "25～45"),
            (65, "2级", "45～65"),
            (float("inf"), "1级", "65～100"),
        ],
    },
    "clay": {
        "name": "机械组成-黏粒",
        "unit": "%",
        "reverse_display": True,
        "levels": [
            (15, "5级", "≤15"),
            (25, "4级", "15～25"),
            (45, "3级", "25～45"),
            (65, "2级", "45～65"),
            (float("inf"), "1级", "65～100"),
        ],
    },
}

# 土壤质地映射配置
SOIL_TEXTURE_MAPPING: dict[str, tuple[str, str, int]] = {
    "砂土及壤质砂土": ("砂土类", "砂土及壤质砂土", 1),
    "砂质壤土": ("砂壤类", "砂质壤土", 2),
    "粉(砂)质壤土": ("轻壤类", "粉(砂)质壤土", 3),
    "壤土": ("中壤类", "壤土", 4),
    "砂质黏壤土": ("黏壤类", "砂质黏壤土", 5),
    "黏壤土": ("黏壤类", "黏壤土", 5),
    "粉(砂)质黏壤土": ("黏壤类", "粉(砂)质黏壤土", 5),
    "砂质黏土": ("轻黏类", "砂质黏土", 6),
    "壤质黏土": ("轻黏类", "壤质黏土", 6),
    "粉(砂)质黏土": ("轻黏类", "粉(砂)质黏土", 6),
    "黏土": ("黏土类", "黏土", 7),
    "重黏土": ("黏土类", "重黏土", 7),
}

# 质地结构（用于表格展示）
TEXTURE_STRUCTURE: list[list[str]] = [
    ["砂土及壤质砂土", "砂质壤土", "粉(砂)质壤土", "壤土"],
    ["砂质黏壤土", "黏壤土", "粉(砂)质黏壤土"],
    ["砂质黏土", "壤质黏土", "粉(砂)质黏土"],
    ["黏土", "重黏土"],
]

# 所有质地类型列表
TEXTURE_COLS: list[str] = [item for sublist in TEXTURE_STRUCTURE for item in sublist]

# 土壤类型排序映射表
SOIL_TYPE_ORDER_MAP: dict[str, list[str]] = {
    "棕红壤": ["红泥质棕红壤"],
    "红壤性土": ["砂泥质红壤性土", "麻砂质红壤性土"],
    "典型黄棕壤": [
        "暗泥质黄棕壤",
        "麻砂质黄棕壤",
        "红砂质黄棕壤",
        "黄土质黄棕壤",
        "砂泥质黄棕壤",
    ],
    "黄棕壤性土": ["砂泥质黄棕壤性土"],
    "典型棕壤": ["麻砂质典型棕壤"],
    "白浆化棕壤": ["麻砂质白浆化棕壤", "泥砂质白浆化棕壤"],
    "潮棕壤": ["泥砂质潮棕壤"],
    "淋溶褐土": ["黄土质淋溶褐土", "灰泥质淋溶褐土", "暗泥质淋溶褐土"],
    "潮褐土": ["泥砂质潮褐土"],
    "红黏土": ["红黏土"],
    "黑色石灰土": ["黑色石灰土"],
    "棕色石灰土": ["棕色石灰土"],
    "暗火山灰土": ["暗火山灰土"],
    "酸性紫色土": ["壤质酸性紫色土", "黏质酸性紫色土"],
    "中性紫色土": ["砂质中性紫色土", "壤质中性紫色土", "黏质中性紫色土"],
    "石灰性紫色土": ["壤质石灰性紫色土"],
    "酸性粗骨土": ["麻砂质酸性粗骨土", "硅质酸性粗骨土"],
    "中性粗骨土": ["麻砂质中性粗骨土"],
    "钙质粗骨土": ["灰泥质钙质粗骨土"],
    "典型潮土": ["砂质潮土", "壤质潮土", "黏质潮土"],
    "灰潮土": ["灰潮土", "石灰性灰潮土"],
    "盐化潮土（含碱化潮土）": ["氯化物盐化潮土", "硫酸盐盐化潮土", "苏打盐化潮土"],
    "典型砂姜黑土": ["黑腐砂姜黑土（黑姜土）", "覆泥砂姜黑土（覆泥黑姜土）"],
    "盐化砂姜黑土": ["氯化物盐化砂姜黑土"],
    "腐泥沼泽土": ["腐泥沼泽土"],
    "草甸沼泽土": ["草甸沼泽土", "石灰性草甸沼泽土"],
    "典型滨海盐土": ["氯化物滨海盐土"],
    "滨海沼泽盐土": ["氯化物沼泽滨海盐土"],
    "滨海潮滩盐土": ["氯化物潮滩滨海盐土"],
    "淹育水稻土": ["浅马肝泥田"],
    "渗育水稻土": [
        "渗灰泥田",
        "渗潮泥砂田",
        "渗潮泥田",
        "渗湖泥田",
        "渗涂泥田",
        "渗淡涂泥田",
        "渗麻砂泥田",
        "渗潮白土田",
        "渗马肝泥田",
    ],
    "潴育水稻土": ["潮泥田", "湖泥田", "马肝泥田"],
    "潜育水稻土": ["青湖泥田", "青马肝泥田"],
    "脱潜水稻土": ["黄斑黏田", "黄斑泥田"],
    "漂洗水稻土": ["漂潮白土田", "漂马肝泥田"],
    "盐渍水稻土": [
        "氯化物潮泥田",
        "氯化物涂泥田",
        "氯化物湖泥田",
        "硫酸盐潮泥田",
        "硫酸盐涂泥田",
        "苏打潮泥田",
        "苏打涂泥田",
        "苏打湖泥田",
    ],
    "填充土": ["工矿填充土", "城镇填充土"],
    "扰动土": ["运移扰动土"],
}

# 土地利用类型配置
LAND_USE_CONFIG: dict[str, list[str]] = {
    "耕地": ["水田", "水浇地", "旱地"],
    "园地": ["果园", "茶园", "其他园地"],
    "林地": ["林地"],
    "草地": ["草地"],
    "其他": ["其他"],
}

# 特定属性的地类过滤规则
ATTR_LAND_USE_FILTERS: dict[str, list[str]] = {
    # 耕作层厚度只统计耕地
    "GZCHD": ["水田", "水浇地", "旱地"],
    # 有效硅只统计水田
    "ASI": ["水田"],
}

# 以下属性只统计耕园地
FARMLAND_GARDEN_ATTRS: list[str] = [
    "ECA",
    "EMG",
    "ENA",
    "EK",
    "SRXYZL",
    "DDL",
    "SK",
    "AS1",
    "AFE",
    "AMN",
    "ACU",
    "AZN",
    "AB",
    "AMO",
    "SWXDTJT7",
]


def normalize_attr_column_name(col_name: str) -> str:
    """将原始列名映射为 SOIL_ATTR_CONFIG 中的标准键"""
    if pd.isna(col_name):
        return ""
    col_str = str(col_name).strip()

    # 别名映射
    alias_map = {
        "pH": "ph",
        "PH": "ph",
        "酸碱度": "ph",
        "有机质含量": "OM",
        "有机质(g/kg)": "OM",
        "全氮含量": "TN",
        "有效磷(P)": "AP",
        "速效钾(K)": "AK",
        "阳离子交换量(CEC)": "CEC",
        "水溶性盐": "SRXYZL",
        "电导率(EC)": "DDL",
    }

    if col_str in alias_map:
        return alias_map[col_str]

    # 直接匹配（不区分大小写）
    for key in SOIL_ATTR_CONFIG:
        if col_str.lower() == key.lower():
            return key

    return col_str


def classify_value(value: float, attr_key: str) -> str | None:
    """根据配置对属性值进行分级

    Args:
        value: 属性值
        attr_key: 属性键名

    Returns:
        分级结果（罗马数字），无效值返回None
    """
    if pd.isna(value) or value <= 0:
        return None

    config = SOIL_ATTR_CONFIG.get(attr_key)
    if not config:
        return None

    roman_map = {
        "1级": "Ⅰ级",
        "2级": "Ⅱ级",
        "3级": "Ⅲ级",
        "4级": "Ⅳ级",
        "5级": "Ⅴ级",
        "6级": "Ⅵ级",
        "7级": "Ⅶ级",
    }

    for threshold, level, _ in config["levels"]:
        if value <= threshold:
            return roman_map.get(level, level)

    return None


def classify_series(values: pd.Series, attr_key: str) -> pd.Series:
    """向量化的属性分级

    Args:
        values: 属性值Series
        attr_key: 属性键名

    Returns:
        分级结果Series
    """
    config = SOIL_ATTR_CONFIG.get(attr_key)
    if not config:
        return pd.Series([None] * len(values), index=values.index)

    numeric = pd.to_numeric(values, errors="coerce")
    valid_mask = numeric.notna() & (numeric > 0)

    result = pd.Series([None] * len(values), index=values.index, dtype=object)
    if not valid_mask.any():
        return result

    thresholds = np.array([float(th[0]) for th in config["levels"]], dtype=float)
    levels = [lvl for _, lvl, _ in config["levels"]]

    roman_map = {
        "1级": "Ⅰ级",
        "2级": "Ⅱ级",
        "3级": "Ⅲ级",
        "4级": "Ⅳ级",
        "5级": "Ⅴ级",
        "6级": "Ⅵ级",
        "7级": "Ⅶ级",
    }

    valid_values = numeric[valid_mask].values.astype(float)
    idx = np.searchsorted(thresholds, valid_values, side="right")
    idx = np.clip(idx, 0, len(levels) - 1)

    level_arr = [roman_map.get(levels[i], levels[i]) for i in idx]
    result.loc[valid_mask] = level_arr

    return result


def get_grade_order(attr_key: str) -> list[str]:
    """获取属性级别的排序列表"""
    if attr_key == "ph":
        return ["Ⅰ级", "Ⅱ级", "Ⅲ级", "Ⅳ级", "Ⅴ级", "Ⅵ级", "Ⅶ级"]
    return ["Ⅰ级", "Ⅱ级", "Ⅲ级", "Ⅳ级", "Ⅴ级"]


def get_level_value_ranges(attr_key: str) -> list[str]:
    """获取属性各级别的数值范围字符串列表"""
    config = SOIL_ATTR_CONFIG.get(attr_key)
    if not config:
        return []

    levels = config["levels"]
    ranges = []

    for i, (threshold, _, _) in enumerate(levels):
        if i == 0:
            ranges.append(f"≤{threshold}")
        elif i == len(levels) - 1:
            ranges.append(f">{levels[i - 1][0]}")
        else:
            prev = levels[i - 1][0]
            ranges.append(f"{prev}～{threshold}")

    if config.get("reverse_display", False):
        return list(reversed(ranges))

    return ranges


def detect_available_attributes(columns: list[str]) -> list[tuple[str, str]]:
    """检测DataFrame列中可用的土壤属性

    Args:
        columns: 列名列表

    Returns:
        [(原始列名, 标准键), ...] 列表
    """
    available = []
    config_keys = set(SOIL_ATTR_CONFIG.keys())

    for col in columns:
        norm_key = normalize_attr_column_name(col)
        if norm_key in config_keys:
            available.append((col, norm_key))

    return available
