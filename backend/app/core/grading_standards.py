"""土壤属性分级标准管理模块

支持多套分级标准（如江苏、河南等），方便后续扩展。
"""

from typing import TypedDict


class AttrGradeConfig(TypedDict, total=False):
    """属性分级配置类型"""

    name: str  # 属性中文名
    unit: str  # 单位
    reverse_display: bool  # 是否反向显示（1级在底部）
    levels: list[tuple[float, str, str]]  # [(阈值, 级别, 描述), ...]
    land_filter: str  # 土地利用过滤规则


class GradingStandard(TypedDict):
    """分级标准类型"""

    name: str  # 标准名称
    description: str  # 标准描述
    attributes: dict[str, AttrGradeConfig]  # 属性配置


# ============================================================================
# 江苏分级标准
# ============================================================================
JIANGSU_STANDARD: GradingStandard = {
    "name": "江苏分级",
    "description": "江苏省土壤普查分级标准",
    "attributes": {
        # ========== 盐碱相关 ==========
        "SRXYZL": {
            "name": "水溶性盐总量",
            "unit": "g/kg",
            "reverse_display": False,
            "land_filter": "cultivated_garden",
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
            "land_filter": "cultivated_garden",
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
            "land_filter": "cultivated_garden",
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
            "land_filter": "cultivated_only",
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
            "land_filter": "cultivated_garden",
            "levels": [
                (10, "1级", "低"),
                (20, "2级", "较低"),
                (30, "3级", "中"),
                (40, "4级", "较高"),
                (float("inf"), "5级", "高"),
            ],
        },
        # ========== 主要养分指标 ==========
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
            "land_filter": "cultivated_garden",
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
            "land_filter": "cultivated_garden",
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
            "land_filter": "cultivated_garden",
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
            "land_filter": "cultivated_garden",
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
            "land_filter": "cultivated_garden",
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
            "land_filter": "paddy_only",
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
            "land_filter": "cultivated_garden",
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
            "land_filter": "cultivated_garden",
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
            "land_filter": "cultivated_garden",
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
            "land_filter": "cultivated_garden",
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
            "land_filter": "cultivated_garden",
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
            "land_filter": "cultivated_garden",
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
    },
}

# ============================================================================
# 分级标准注册表
# ============================================================================
GRADING_STANDARDS: dict[str, GradingStandard] = {
    "jiangsu": JIANGSU_STANDARD,
    # 后续可在此添加更多标准，如：
    # "henan": HENAN_STANDARD,
}

# 默认使用的分级标准
DEFAULT_STANDARD = "jiangsu"

# 当前激活的分级标准（可在运行时修改）
_current_standard: str = DEFAULT_STANDARD


def get_standard(name: str | None = None) -> GradingStandard:
    """获取分级标准

    Args:
        name: 标准名称，为None时返回当前激活的标准

    Returns:
        分级标准配置
    """
    if name is None:
        name = _current_standard
    return GRADING_STANDARDS.get(name, JIANGSU_STANDARD)


def get_attr_config(name: str | None = None) -> dict[str, AttrGradeConfig]:
    """获取属性配置

    Args:
        name: 标准名称，为None时返回当前激活的标准

    Returns:
        属性配置字典
    """
    return get_standard(name)["attributes"]


def set_current_standard(name: str) -> bool:
    """设置当前激活的分级标准

    Args:
        name: 标准名称

    Returns:
        是否设置成功
    """
    global _current_standard
    if name in GRADING_STANDARDS:
        _current_standard = name
        return True
    return False


def get_current_standard() -> str:
    """获取当前激活的分级标准名称"""
    return _current_standard


def list_standards() -> list[dict[str, str]]:
    """列出所有可用的分级标准

    Returns:
        [{"id": "jiangsu", "name": "江苏分级", "description": "..."}, ...]
    """
    return [
        {
            "id": std_id,
            "name": std["name"],
            "description": std["description"],
        }
        for std_id, std in GRADING_STANDARDS.items()
    ]


def register_standard(std_id: str, standard: GradingStandard) -> None:
    """注册新的分级标准

    Args:
        std_id: 标准ID
        standard: 分级标准配置
    """
    GRADING_STANDARDS[std_id] = standard
