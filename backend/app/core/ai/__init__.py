"""AI 辅助生成模块

支持通义千问和 DeepSeek 生成报告文字内容
"""

from app.core.ai.qwen_client import (
    AIProvider,
    call_ai,
    generate_analysis,
    generate_comprehensive_summary,
    generate_conclusion,
    generate_land_use_analysis,
    generate_soil_type_analysis,
    generate_suggestion,
    generate_town_analysis,
    generate_traceability_analysis,
    get_ai_config,
)

__all__ = [
    "AIProvider",
    "get_ai_config",
    "call_ai",
    "generate_analysis",
    "generate_conclusion",
    "generate_suggestion",
    "generate_comprehensive_summary",
    "generate_traceability_analysis",
    "generate_land_use_analysis",
    "generate_soil_type_analysis",
    "generate_town_analysis",
]
