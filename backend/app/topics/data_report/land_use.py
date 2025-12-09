"""土地利用类型处理模块

处理土地利用类型分类、过滤和统计。
"""

import pandas as pd

from app.topics.data_report.config import LAND_USE_STRUCTURE, SOIL_ATTR_CONFIG


def get_land_class(dlmc: str) -> tuple[str, str] | None:
    """将地类名称映射为(一级地类, 二级地类)

    Args:
        dlmc: 地类名称

    Returns:
        (一级地类, 二级地类) 元组，无效返回None
    """
    if pd.isna(dlmc):
        return None

    s = str(dlmc).strip()

    if s in ["水田", "水浇地", "旱地"]:
        return ("耕地", s)
    elif s in ["果园", "茶园"]:
        return ("园地", s)
    elif "园地" in s:
        return ("园地", "其他园地")
    elif "林地" in s:
        return ("林地", "林地")
    elif "草地" in s:
        return ("草地", "草地")
    else:
        return ("其他", "其他")


def ensure_land_class_column(df: pd.DataFrame) -> pd.DataFrame:
    """确保数据框包含二级地类列

    统一列名为'二级地类'，兼容多种常见列名。

    Args:
        df: 输入数据框

    Returns:
        处理后的数据框

    Raises:
        ValueError: 未找到地类列
    """
    if "二级地类" in df.columns:
        return df

    # 尝试常见列名
    possible_names = ["DLMC", "dlmc", "地类名称", "dlm", "DLM"]
    for col in df.columns:
        col_str = str(col).strip()
        if col_str in possible_names or col_str.upper() == "DLMC":
            return df.rename(columns={col: "二级地类"})

    raise ValueError("未找到地类列（期望：'二级地类'、'DLMC' 或 '地类名称'）")


def apply_land_filter(df: pd.DataFrame, attr_key: str) -> pd.DataFrame:
    """根据属性的用地限制过滤数据

    不同属性可能只统计特定地类：
    - cultivated_garden: 耕地和园地
    - paddy_only: 仅水田
    - cultivated_only: 仅耕地

    Args:
        df: 输入数据框
        attr_key: 属性键名

    Returns:
        过滤后的数据框
    """
    config = SOIL_ATTR_CONFIG.get(attr_key, {})
    land_filter = config.get("land_filter")

    if not land_filter:
        return df

    try:
        df = ensure_land_class_column(df)
        land_info = df["二级地类"].apply(get_land_class)
        df = df.copy()
        df[["一级地类", "二级地类名"]] = pd.DataFrame(
            land_info.tolist(), index=df.index
        )

        if land_filter == "cultivated_garden":
            df = df[df["一级地类"].isin(["耕地", "园地"])]
        elif land_filter == "paddy_only":
            df = df[(df["一级地类"] == "耕地") & (df["二级地类名"] == "水田")]
        elif land_filter == "cultivated_only":
            df = df[df["一级地类"] == "耕地"]

    except Exception:
        pass  # 过滤失败保持原数据

    return df


def add_land_use_columns(df: pd.DataFrame) -> pd.DataFrame:
    """为数据框添加土地利用分类列

    Args:
        df: 输入数据框

    Returns:
        添加了一级地类和二级地类列的数据框
    """
    df = df.copy()

    # 确定地类源列
    dlmc_col = None
    for col in ["二级地类", "DLMC", "dlmc", "地类名称"]:
        if col in df.columns:
            dlmc_col = col
            break

    if dlmc_col is None:
        df["一级地类"] = "其他"
        df["二级地类"] = "其他"
        return df

    # 应用分类映射
    land_info = df[dlmc_col].apply(get_land_class)
    result_df = pd.DataFrame(land_info.tolist(), index=df.index)
    result_df.columns = ["一级地类", "二级地类"]

    # 处理None值
    result_df = result_df.fillna("其他")

    df["一级地类"] = result_df["一级地类"]
    df["二级地类"] = result_df["二级地类"]

    return df


def get_land_use_structure() -> list[tuple[str, list[str]]]:
    """获取土地利用类型结构

    Returns:
        [(一级地类, [二级地类列表]), ...] 列表
    """
    return LAND_USE_STRUCTURE
