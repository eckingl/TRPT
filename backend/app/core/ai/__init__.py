"""AI 辅助生成模块

支持通义千问和 DeepSeek 生成报告文字内容
集成 Memori 记忆引擎提供跨会话上下文记忆
"""

from app.core.ai.memory import (
    disable_memori,
    enable_memori,
    get_memori,
    inject_memory_context,
    is_memori_enabled,
    record_interaction,
)
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
    # AI 提供商
    "AIProvider",
    "get_ai_config",
    "call_ai",
    # 报告生成
    "generate_analysis",
    "generate_conclusion",
    "generate_suggestion",
    "generate_comprehensive_summary",
    "generate_traceability_analysis",
    "generate_land_use_analysis",
    "generate_soil_type_analysis",
    "generate_town_analysis",
    # Memori 记忆功能
    "enable_memori",
    "disable_memori",
    "is_memori_enabled",
    "get_memori",
    "inject_memory_context",
    "record_interaction",
]
