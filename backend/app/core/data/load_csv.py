"""CSV文件加载模块 - 支持自动编码检测"""

from pathlib import Path

import chardet
import pandas as pd


def detect_encoding(file_path: str | Path, sample_size: int = 10000) -> str:
    """检测文件编码

    Args:
        file_path: 文件路径
        sample_size: 用于检测的字节数

    Returns:
        检测到的编码名称
    """
    with open(file_path, "rb") as f:
        raw_data = f.read(sample_size)
        result = chardet.detect(raw_data)
        encoding = result.get("encoding")

    if encoding is None:
        return "utf-8"

    # 统一处理中文编码
    if encoding.lower() in ["gb2312", "gbk", "cp936", "gb18030"]:
        return "gbk"

    return encoding


def load_csv(file_path: str | Path) -> pd.DataFrame:
    """加载CSV文件，自动检测编码

    Args:
        file_path: CSV文件路径

    Returns:
        加载的DataFrame

    Raises:
        ValueError: 无法读取文件时抛出
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise ValueError(f"文件不存在: {file_path}")

    encoding = detect_encoding(file_path)

    try:
        return pd.read_csv(file_path, encoding=encoding)
    except UnicodeDecodeError:
        # 如果检测的编码失败，尝试常用编码
        for fallback_encoding in ["utf-8", "gbk", "gb18030", "latin-1"]:
            try:
                return pd.read_csv(file_path, encoding=fallback_encoding)
            except UnicodeDecodeError:
                continue
        raise ValueError(f"无法读取文件 {file_path}，尝试了多种编码均失败")


def load_multiple_csv(file_paths: list[str | Path]) -> pd.DataFrame:
    """加载多个CSV文件并合并

    Args:
        file_paths: CSV文件路径列表

    Returns:
        合并后的DataFrame

    Raises:
        ValueError: 无有效文件时抛出
    """
    if not file_paths:
        raise ValueError("未提供任何文件")

    dataframes = []
    for path in file_paths:
        df = load_csv(path)
        dataframes.append(df)

    if not dataframes:
        raise ValueError("未能成功读取任何文件")

    return pd.concat(dataframes, ignore_index=True)
