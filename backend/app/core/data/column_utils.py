"""列名处理工具模块"""

import pandas as pd
from pypinyin import lazy_pinyin


def find_column_case_insensitive(df: pd.DataFrame, target_col: str) -> str:
    """在数据框中查找指定列名（不区分大小写）

    Args:
        df: 数据框
        target_col: 目标列名

    Returns:
        找到的实际列名

    Raises:
        ValueError: 未找到列时抛出
    """
    for col in df.columns:
        if col.strip().lower() == target_col.lower():
            return col
    raise ValueError(f"未找到名为 '{target_col}' 的列（不区分大小写）")


def find_column_by_names(df: pd.DataFrame, possible_names: list[str]) -> str | None:
    """查找可能存在的列名

    Args:
        df: 数据框
        possible_names: 可能的列名列表

    Returns:
        找到的列名，未找到返回None
    """
    for name in possible_names:
        for col in df.columns:
            if col.strip().lower() == name.lower():
                return col
    return None


def normalize_dlmc_column(df: pd.DataFrame) -> pd.DataFrame:
    """将数据框中的地类列统一重命名为 'DLMC'

    支持: dlm, dlmc, 二级地类

    Args:
        df: 输入数据框

    Returns:
        处理后的数据框

    Raises:
        ValueError: 未找到地类列时抛出
    """
    dlmc_col = find_column_by_names(df, ["DLMC", "dlmc", "dlm", "DLM", "二级地类"])
    if dlmc_col is None:
        raise ValueError("未找到名为 'DLMC'、'dlm' 或 '二级地类' 的列")
    if dlmc_col != "DLMC":
        df = df.rename(columns={dlmc_col: "DLMC"})
    return df


def normalize_soil_type_columns(df: pd.DataFrame) -> pd.DataFrame:
    """将土壤类型列统一重命名为 'YL'（亚类）和 'TS'（土属）

    支持: YL/SSub_JZg, TS/SGen_JZg

    Args:
        df: 输入数据框

    Returns:
        处理后的数据框

    Raises:
        ValueError: 未找到必需列时抛出
    """
    # 处理亚类列
    yl_col = find_column_by_names(df, ["YL", "SSub_JZg"])
    if yl_col is None:
        raise ValueError("未找到 'YL' 或 'SSub_JZg' 列")
    if yl_col != "YL":
        df = df.rename(columns={yl_col: "YL"})

    # 处理土属列
    ts_col = find_column_by_names(df, ["TS", "SGen_JZg"])
    if ts_col is None:
        raise ValueError("未找到 'TS' 或 'SGen_JZg' 列")
    if ts_col != "TS":
        df = df.rename(columns={ts_col: "TS"})

    return df


def normalize_mechanical_columns(df: pd.DataFrame) -> pd.DataFrame:
    """将机械组成列统一重命名为 'sand', 'silt', 'clay'

    Args:
        df: 输入数据框

    Returns:
        处理后的数据框

    Raises:
        ValueError: 未找到必需列时抛出
    """
    # 查找并重命名砂粒列
    sand_col = find_column_by_names(df, ["sand", "SAND", "Sand"])
    if sand_col is None:
        raise ValueError("未找到 'sand' 列")
    if sand_col != "sand":
        df = df.rename(columns={sand_col: "sand"})

    # 查找并重命名粉粒列
    silt_col = find_column_by_names(df, ["silt", "SILT", "Silt"])
    if silt_col is None:
        raise ValueError("未找到 'silt' 列")
    if silt_col != "silt":
        df = df.rename(columns={silt_col: "silt"})

    # 查找并重命名黏粒列
    clay_col = find_column_by_names(df, ["clay", "CLAY", "Clay"])
    if clay_col is None:
        raise ValueError("未找到 'clay' 列")
    if clay_col != "clay":
        df = df.rename(columns={clay_col: "clay"})

    return df


def get_pinyin_sort_key(text: str) -> str:
    """获取文本的拼音排序键

    Args:
        text: 中文文本

    Returns:
        拼音字符串（用于排序）
    """
    if pd.isna(text):
        return ""
    pinyin_list = lazy_pinyin(str(text))
    return "".join(pinyin_list).lower()


def get_land_use_class(dlmc: str) -> tuple[str | None, str | None]:
    """根据地类名称获取土地利用分类

    Args:
        dlmc: 地类名称

    Returns:
        (一级分类, 二级分类) 元组
    """
    if pd.isna(dlmc):
        return None, None

    s = str(dlmc).strip()

    if s in ["水田", "水浇地", "旱地"]:
        return "耕地", s
    elif s in ["果园", "茶园"]:
        return "园地", s
    elif "园地" in s:
        return "园地", "其他园地"
    elif "林地" in s:
        return "林地", "林地"
    elif "草地" in s:
        return "草地", "草地"
    else:
        return "其他", "其他"
