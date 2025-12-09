"""土壤类型处理模块

处理土壤类型（土类、亚类、土属）的标准化和统计。
"""

import pandas as pd

# 土壤类型排序顺序（按土类-亚类-土属层级）
SOIL_TYPE_ORDER: list[tuple[str, str, str]] = [
    # 红壤相关
    ("红壤", "棕红壤", "红泥质棕红壤"),
    ("红壤", "红壤性土", "砂泥质红壤性土"),
    ("红壤", "红壤性土", "麻砂质红壤性土"),
    # 黄棕壤相关
    ("黄棕壤", "典型黄棕壤", "暗泥质黄棕壤"),
    ("黄棕壤", "典型黄棕壤", "麻砂质黄棕壤"),
    ("黄棕壤", "典型黄棕壤", "红砂质黄棕壤"),
    ("黄棕壤", "典型黄棕壤", "黄土质黄棕壤"),
    ("黄棕壤", "典型黄棕壤", "砂泥质黄棕壤"),
    ("黄棕壤", "黄棕壤性土", "砂泥质黄棕壤性土"),
    # 棕壤相关
    ("棕壤", "典型棕壤", "麻砂质典型棕壤"),
    ("棕壤", "白浆化棕壤", "麻砂质白浆化棕壤"),
    ("棕壤", "白浆化棕壤", "泥砂质白浆化棕壤"),
    ("棕壤", "潮棕壤", "泥砂质潮棕壤"),
    # 褐土相关
    ("褐土", "淋溶褐土", "黄土质淋溶褐土"),
    ("褐土", "淋溶褐土", "灰泥质淋溶褐土"),
    ("褐土", "淋溶褐土", "暗泥质淋溶褐土"),
    ("褐土", "潮褐土", "泥砂质潮褐土"),
    # 其他土壤类型
    ("红黏土", "红黏土", "红黏土"),
    # 石灰岩土相关
    ("石灰岩土", "黑色石灰土", "黑色石灰土"),
    ("石灰岩土", "棕色石灰土", "棕色石灰土"),
    # 火山灰土相关
    ("火山灰土", "暗火山灰土", "暗火山灰土"),
    # 紫色土相关
    ("紫色土", "酸性紫色土", "壤质酸性紫色土"),
    ("紫色土", "酸性紫色土", "黏质酸性紫色土"),
    ("紫色土", "中性紫色土", "砂质中性紫色土"),
    ("紫色土", "中性紫色土", "壤质中性紫色土"),
    ("紫色土", "中性紫色土", "黏质中性紫色土"),
    ("紫色土", "石灰性紫色土", "壤质石灰性紫色土"),
    # 粗骨土相关
    ("粗骨土", "酸性粗骨土", "麻砂质酸性粗骨土"),
    ("粗骨土", "酸性粗骨土", "硅质酸性粗骨土"),
    ("粗骨土", "中性粗骨土", "麻砂质中性粗骨土"),
    ("粗骨土", "钙质粗骨土", "灰泥质钙质粗骨土"),
    # 潮土相关
    ("潮土", "典型潮土", "砂质潮土"),
    ("潮土", "典型潮土", "壤质潮土"),
    ("潮土", "典型潮土", "黏质潮土"),
    ("潮土", "灰潮土", "灰潮土"),
    ("潮土", "灰潮土", "石灰性灰潮土"),
    ("潮土", "盐化潮土（含碱化潮土）", "氯化物盐化潮土"),
    ("潮土", "盐化潮土（含碱化潮土）", "硫酸盐盐化潮土"),
    ("潮土", "盐化潮土（含碱化潮土）", "苏打盐化潮土"),
    # 砂姜黑土相关
    ("砂姜黑土", "典型砂姜黑土", "黑腐砂姜黑土（黑姜土）"),
    ("砂姜黑土", "典型砂姜黑土", "覆泥砂姜黑土（覆泥黑姜土）"),
    ("砂姜黑土", "盐化砂姜黑土", "氯化物盐化砂姜黑土"),
    # 沼泽土相关
    ("沼泽土", "腐泥沼泽土", "腐泥沼泽土"),
    ("沼泽土", "草甸沼泽土", "草甸沼泽土"),
    ("沼泽土", "草甸沼泽土", "石灰性草甸沼泽土"),
    # 滨海盐土相关
    ("滨海盐土", "典型滨海盐土", "氯化物滨海盐土"),
    ("滨海盐土", "滨海沼泽盐土", "氯化物沼泽滨海盐土"),
    ("滨海盐土", "滨海潮滩盐土", "氯化物潮滩滨海盐土"),
    # 水稻土相关
    ("水稻土", "淹育水稻土", "浅马肝泥田"),
    ("水稻土", "渗育水稻土", "渗灰泥田"),
    ("水稻土", "渗育水稻土", "渗潮泥砂田"),
    ("水稻土", "渗育水稻土", "渗潮泥田"),
    ("水稻土", "渗育水稻土", "渗湖泥田"),
    ("水稻土", "渗育水稻土", "渗涂泥田"),
    ("水稻土", "渗育水稻土", "渗淡涂泥田"),
    ("水稻土", "渗育水稻土", "渗麻砂泥田"),
    ("水稻土", "渗育水稻土", "渗潮白土田"),
    ("水稻土", "渗育水稻土", "渗马肝泥田"),
    ("水稻土", "潴育水稻土", "潮泥田"),
    ("水稻土", "潴育水稻土", "湖泥田"),
    ("水稻土", "潴育水稻土", "马肝泥田"),
    ("水稻土", "潜育水稻土", "青湖泥田"),
    ("水稻土", "潜育水稻土", "青马肝泥田"),
    ("水稻土", "脱潜水稻土", "黄斑黏田"),
    ("水稻土", "脱潜水稻土", "黄斑泥田"),
    ("水稻土", "漂洗水稻土", "漂潮白土田"),
    ("水稻土", "漂洗水稻土", "漂马肝泥田"),
    ("水稻土", "盐渍水稻土", "氯化物潮泥田"),
    ("水稻土", "盐渍水稻土", "氯化物涂泥田"),
    ("水稻土", "盐渍水稻土", "氯化物湖泥田"),
    ("水稻土", "盐渍水稻土", "硫酸盐潮泥田"),
    ("水稻土", "盐渍水稻土", "硫酸盐涂泥田"),
    ("水稻土", "盐渍水稻土", "苏打潮泥田"),
    ("水稻土", "盐渍水稻土", "苏打涂泥田"),
    ("水稻土", "盐渍水稻土", "苏打湖泥田"),
    # 人工土相关
    ("人工土", "填充土", "工矿填充土"),
    ("人工土", "填充土", "城镇填充土"),
    ("人工土", "扰动土", "运移扰动土"),
]

# 构建层级结构
SOIL_TYPE_HIERARCHY: dict[str, dict[str, list[str]]] = {}
for _major, _sub, _genus in SOIL_TYPE_ORDER:
    if _major not in SOIL_TYPE_HIERARCHY:
        SOIL_TYPE_HIERARCHY[_major] = {}
    if _sub not in SOIL_TYPE_HIERARCHY[_major]:
        SOIL_TYPE_HIERARCHY[_major][_sub] = []
    if _genus not in SOIL_TYPE_HIERARCHY[_major][_sub]:
        SOIL_TYPE_HIERARCHY[_major][_sub].append(_genus)

# 排序索引
_SORT_INDEX: dict[tuple[str, str, str], int] = {
    item: idx for idx, item in enumerate(SOIL_TYPE_ORDER)
}


def normalize_soil_type_columns(df: pd.DataFrame) -> pd.DataFrame:
    """标准化土壤类型列名

    将TL/土类、YL/亚类、TS/土属统一为中文名称。

    Args:
        df: 输入数据框

    Returns:
        标准化后的数据框
    """
    df = df.copy()

    # 列名映射
    column_mapping: dict[str, str] = {}
    if "TL" in df.columns:
        column_mapping["TL"] = "土类"
    if "YL" in df.columns:
        column_mapping["YL"] = "亚类"
    if "TS" in df.columns:
        column_mapping["TS"] = "土属"

    if column_mapping:
        df = df.rename(columns=column_mapping)

    # 确保列存在
    for col in ["土类", "亚类", "土属"]:
        if col not in df.columns:
            df[col] = ""

    return df


def get_soil_type_sort_key(
    major: str, sub: str, genus: str
) -> tuple[int, str, str, str]:
    """获取土壤类型排序键

    Args:
        major: 土类
        sub: 亚类
        genus: 土属

    Returns:
        排序元组
    """
    key = (major, sub, genus)
    if key in _SORT_INDEX:
        return (_SORT_INDEX[key], major, sub, genus)
    # 未知类型排在最后
    return (len(SOIL_TYPE_ORDER), major, sub, genus)


def add_soil_type_columns(df: pd.DataFrame) -> pd.DataFrame:
    """为数据框添加标准化的土壤类型列

    Args:
        df: 输入数据框

    Returns:
        添加了土类、亚类、土属列的数据框
    """
    df = normalize_soil_type_columns(df)

    # 清理空白字符
    for col in ["土类", "亚类", "土属"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace(["nan", "None", ""], pd.NA)

    # 对于土类列，如果为空则设为"未分类"
    if "土类" in df.columns:
        df["土类"] = df["土类"].fillna("未分类")

    return df


def filter_valid_soil_types(df: pd.DataFrame) -> pd.DataFrame:
    """过滤出有效的土壤类型记录

    只保留亚类和土属都有值的记录。

    Args:
        df: 输入数据框

    Returns:
        过滤后的数据框
    """
    df = add_soil_type_columns(df)

    valid_mask = (
        df["亚类"].notna()
        & (df["亚类"] != "")
        & df["土属"].notna()
        & (df["土属"] != "")
    )

    return df[valid_mask].copy()


def group_by_soil_type(df: pd.DataFrame) -> dict[tuple[str, str, str], pd.DataFrame]:
    """按土壤类型分组

    Args:
        df: 输入数据框

    Returns:
        {(土类, 亚类, 土属): 子数据框} 字典
    """
    df = add_soil_type_columns(df)
    df = filter_valid_soil_types(df)

    groups: dict[tuple[str, str, str], pd.DataFrame] = {}

    for (major, sub, genus), group_df in df.groupby(
        ["土类", "亚类", "土属"], dropna=False
    ):
        # 处理NA值
        major = str(major) if pd.notna(major) and major != "" else "未分类"
        sub = str(sub) if pd.notna(sub) else ""
        genus = str(genus) if pd.notna(genus) else ""

        if sub and genus:
            groups[(major, sub, genus)] = group_df

    return groups
