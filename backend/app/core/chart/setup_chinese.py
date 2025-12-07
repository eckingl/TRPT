"""中文字体配置模块

为 matplotlib 配置中文字体支持，确保图表中文正常显示
"""

import platform
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt

# 中文字体优先级列表（按平台）
FONT_PRIORITY = {
    "Windows": [
        "Microsoft YaHei",
        "SimHei",
        "SimSun",
        "KaiTi",
        "FangSong",
    ],
    "Darwin": [  # macOS
        "PingFang SC",
        "Heiti SC",
        "STHeiti",
        "Songti SC",
    ],
    "Linux": [
        "WenQuanYi Micro Hei",
        "WenQuanYi Zen Hei",
        "Noto Sans CJK SC",
        "Droid Sans Fallback",
    ],
}


def _find_available_font() -> str | None:
    """查找系统可用的中文字体"""
    system = platform.system()
    font_list = FONT_PRIORITY.get(system, FONT_PRIORITY["Windows"])

    # 获取系统可用字体
    available_fonts = {f.name for f in matplotlib.font_manager.fontManager.ttflist}

    for font in font_list:
        if font in available_fonts:
            return font

    return None


def setup_chinese_font() -> str:
    """配置 matplotlib 中文字体

    Returns:
        str: 实际使用的字体名称

    Raises:
        RuntimeError: 当找不到可用中文字体时
    """
    font_name = _find_available_font()

    if font_name is None:
        # 尝试使用系统默认字体
        font_name = "sans-serif"

    # 配置 matplotlib
    plt.rcParams["font.sans-serif"] = [font_name, "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

    return font_name


def get_font_path(font_name: str) -> Path | None:
    """获取指定字体的文件路径

    Args:
        font_name: 字体名称

    Returns:
        字体文件路径，找不到返回 None
    """
    for font in matplotlib.font_manager.fontManager.ttflist:
        if font.name == font_name:
            return Path(font.fname)
    return None


# 模块加载时自动配置中文字体
_CONFIGURED_FONT: str | None = None


def ensure_chinese_font() -> str:
    """确保中文字体已配置（幂等操作）

    Returns:
        str: 当前使用的字体名称
    """
    global _CONFIGURED_FONT
    if _CONFIGURED_FONT is None:
        _CONFIGURED_FONT = setup_chinese_font()
    return _CONFIGURED_FONT
