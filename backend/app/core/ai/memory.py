"""Memori 记忆引擎集成模块

为 AI 调用提供持久化记忆能力，支持跨会话上下文记忆
"""

import os
from pathlib import Path
from typing import TYPE_CHECKING

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

if TYPE_CHECKING:
    from memori import Memori
    from memori.core.providers import ProviderConfig

# 全局 Memori 实例
_memori_instance: "Memori | None" = None
_memori_enabled: bool = False


def get_memori_db_path() -> str:
    """获取 Memori 数据库路径"""
    # 使用项目 output 目录存储记忆数据库
    output_dir = Path(__file__).parent.parent.parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    db_path = output_dir / "memori.db"
    return f"sqlite:///{db_path}"


def init_memori(
    namespace: str = "trpc_soil_survey",
    conscious_ingest: bool = True,
    auto_ingest: bool = True,
    verbose: bool = False,
) -> "Memori | None":
    """初始化 Memori 记忆引擎

    Args:
        namespace: 记忆命名空间，用于隔离不同项目的记忆
        conscious_ingest: 是否启用智能上下文注入
        auto_ingest: 是否启用自动记忆摄取
        verbose: 是否启用详细日志

    Returns:
        Memori 实例，如果初始化失败则返回 None
    """
    global _memori_instance, _memori_enabled

    if _memori_instance is not None:
        return _memori_instance

    try:
        from memori import Memori
        from memori.core.providers import ProviderConfig
    except ImportError:
        print("[Memori] memorisdk 未安装，记忆功能不可用")
        return None

    # 根据当前 AI 提供商配置 Memori
    ai_provider = os.getenv("AI_PROVIDER", "deepseek")

    try:
        if ai_provider == "deepseek":
            # DeepSeek 使用 OpenAI 兼容接口
            deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "")
            if not deepseek_api_key:
                print("[Memori] DEEPSEEK_API_KEY 未设置，记忆功能不可用")
                return None

            provider_config = ProviderConfig.from_custom(
                base_url="https://api.deepseek.com",
                api_key=deepseek_api_key,
                model="deepseek-chat",
            )
        elif ai_provider == "qwen":
            # 通义千问需要配置 OpenAI 兼容模式
            # 注意: 通义千问可能需要额外配置
            dashscope_api_key = os.getenv("DASHSCOPE_API_KEY", "")
            if not dashscope_api_key:
                print("[Memori] DASHSCOPE_API_KEY 未设置，记忆功能不可用")
                return None

            # 通义千问 OpenAI 兼容接口
            provider_config = ProviderConfig.from_custom(
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                api_key=dashscope_api_key,
                model="qwen-plus",
            )
        else:
            # 默认使用 OpenAI
            openai_api_key = os.getenv("OPENAI_API_KEY", "")
            if not openai_api_key:
                print("[Memori] OPENAI_API_KEY 未设置，记忆功能不可用")
                return None

            provider_config = ProviderConfig.from_openai(
                api_key=openai_api_key,
            )

        # 初始化 Memori
        _memori_instance = Memori(
            database_connect=get_memori_db_path(),
            provider_config=provider_config,
            conscious_ingest=conscious_ingest,
            auto_ingest=auto_ingest,
            verbose=verbose,
            namespace=namespace,
        )

        print(f"[Memori] 记忆引擎初始化成功，使用 {ai_provider} 提供商")
        return _memori_instance

    except Exception as e:
        print(f"[Memori] 初始化失败: {e}")
        return None


def enable_memori() -> bool:
    """启用 Memori 记忆功能

    Returns:
        是否成功启用
    """
    global _memori_enabled

    memori = init_memori()
    if memori is None:
        return False

    try:
        memori.enable()
        _memori_enabled = True
        print("[Memori] 记忆功能已启用")
        return True
    except Exception as e:
        print(f"[Memori] 启用失败: {e}")
        return False


def disable_memori() -> None:
    """禁用 Memori 记忆功能"""
    global _memori_instance, _memori_enabled

    if _memori_instance is not None:
        try:
            _memori_instance.disable()
        except Exception:
            pass

    _memori_enabled = False
    print("[Memori] 记忆功能已禁用")


def is_memori_enabled() -> bool:
    """检查 Memori 是否已启用"""
    return _memori_enabled


def get_memori() -> "Memori | None":
    """获取 Memori 实例"""
    return _memori_instance


def inject_memory_context(prompt: str, user_id: str | None = None) -> str:
    """手动注入记忆上下文到提示词

    当 conscious_ingest 启用时，Memori 会自动处理上下文注入
    此函数用于需要手动控制的场景

    Args:
        prompt: 原始提示词
        user_id: 用户 ID，用于检索特定用户的记忆

    Returns:
        注入记忆上下文后的提示词
    """
    if not _memori_enabled or _memori_instance is None:
        return prompt

    try:
        # 使用 Memori 的上下文注入功能
        # 注意: 具体 API 可能需要根据 memorisdk 版本调整
        context = _memori_instance.get_context(prompt, user_id=user_id)
        if context:
            return f"{context}\n\n{prompt}"
    except Exception as e:
        print(f"[Memori] 上下文注入失败: {e}")

    return prompt


def record_interaction(
    user_message: str,
    assistant_response: str,
    metadata: dict | None = None,
) -> None:
    """手动记录交互到记忆

    当 auto_ingest 启用时，Memori 会自动记录交互
    此函数用于需要手动控制的场景

    Args:
        user_message: 用户消息
        assistant_response: AI 响应
        metadata: 额外元数据
    """
    if not _memori_enabled or _memori_instance is None:
        return

    try:
        _memori_instance.add_memory(
            content=f"用户: {user_message}\n助手: {assistant_response}",
            metadata=metadata or {},
        )
    except Exception as e:
        print(f"[Memori] 记录交互失败: {e}")
