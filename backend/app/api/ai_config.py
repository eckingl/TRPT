"""AI 配置管理 API"""

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.config import get_settings

router = APIRouter(prefix="/ai-config")
settings = get_settings()

# 配置文件路径
CONFIG_FILE = settings.BASE_DIR / "data" / "ai_configs.json"


class AIConfigCreate(BaseModel):
    """创建 AI 配置"""

    name: str = Field(..., min_length=1, max_length=50, description="配置名称")
    provider: str = Field(..., description="提供商类型: qwen/deepseek/openai/custom")
    api_key: str = Field(..., min_length=1, description="API 密钥")
    base_url: str | None = Field(None, description="自定义 API 地址")
    model: str = Field(..., min_length=1, description="模型名称")
    is_default: bool = Field(False, description="是否为默认配置")


class AIConfigUpdate(BaseModel):
    """更新 AI 配置"""

    name: str | None = Field(None, min_length=1, max_length=50)
    provider: str | None = None
    api_key: str | None = Field(None, min_length=1)
    base_url: str | None = None
    model: str | None = Field(None, min_length=1)
    is_default: bool | None = None


class AIConfigResponse(BaseModel):
    """AI 配置响应"""

    id: str
    name: str
    provider: str
    api_key_masked: str  # 显示掩码后的 API Key
    base_url: str | None
    model: str
    is_default: bool


class AIConfigListResponse(BaseModel):
    """AI 配置列表响应"""

    configs: list[AIConfigResponse]
    total: int


def _ensure_config_dir() -> None:
    """确保配置目录存在"""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)


def _load_configs() -> dict[str, Any]:
    """加载配置文件"""
    _ensure_config_dir()
    if not CONFIG_FILE.exists():
        return {"configs": [], "next_id": 1}
    try:
        with open(CONFIG_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"configs": [], "next_id": 1}


def _save_configs(data: dict[str, Any]) -> None:
    """保存配置文件"""
    _ensure_config_dir()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _mask_api_key(api_key: str) -> str:
    """掩码 API Key，只显示前4位和后4位"""
    if len(api_key) <= 8:
        return "*" * len(api_key)
    return api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]


def _config_to_response(config: dict[str, Any]) -> AIConfigResponse:
    """将配置转换为响应格式"""
    return AIConfigResponse(
        id=config["id"],
        name=config["name"],
        provider=config["provider"],
        api_key_masked=_mask_api_key(config["api_key"]),
        base_url=config.get("base_url"),
        model=config["model"],
        is_default=config.get("is_default", False),
    )


@router.get("", response_model=AIConfigListResponse)
async def list_ai_configs() -> AIConfigListResponse:
    """获取所有 AI 配置"""
    data = _load_configs()
    configs = [_config_to_response(c) for c in data["configs"]]
    return AIConfigListResponse(configs=configs, total=len(configs))


@router.post("", response_model=AIConfigResponse)
async def create_ai_config(config: AIConfigCreate) -> AIConfigResponse:
    """创建新的 AI 配置"""
    data = _load_configs()

    # 检查名称是否重复
    for existing in data["configs"]:
        if existing["name"] == config.name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"配置名称已存在: {config.name}",
            )

    # 创建新配置
    new_id = str(data["next_id"])
    new_config = {
        "id": new_id,
        "name": config.name,
        "provider": config.provider,
        "api_key": config.api_key,
        "base_url": config.base_url,
        "model": config.model,
        "is_default": config.is_default,
    }

    # 如果设为默认，取消其他配置的默认状态
    if config.is_default:
        for c in data["configs"]:
            c["is_default"] = False

    data["configs"].append(new_config)
    data["next_id"] += 1
    _save_configs(data)

    return _config_to_response(new_config)


@router.get("/{config_id}", response_model=AIConfigResponse)
async def get_ai_config(config_id: str) -> AIConfigResponse:
    """获取单个 AI 配置"""
    data = _load_configs()

    for config in data["configs"]:
        if config["id"] == config_id:
            return _config_to_response(config)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"配置不存在: {config_id}",
    )


@router.put("/{config_id}", response_model=AIConfigResponse)
async def update_ai_config(config_id: str, update: AIConfigUpdate) -> AIConfigResponse:
    """更新 AI 配置"""
    data = _load_configs()

    for i, config in enumerate(data["configs"]):
        if config["id"] == config_id:
            # 检查名称是否与其他配置重复
            if update.name and update.name != config["name"]:
                for other in data["configs"]:
                    if other["id"] != config_id and other["name"] == update.name:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"配置名称已存在: {update.name}",
                        )

            # 更新字段
            if update.name is not None:
                config["name"] = update.name
            if update.provider is not None:
                config["provider"] = update.provider
            if update.api_key is not None:
                config["api_key"] = update.api_key
            if update.base_url is not None:
                config["base_url"] = update.base_url if update.base_url else None
            if update.model is not None:
                config["model"] = update.model
            if update.is_default is not None:
                if update.is_default:
                    # 取消其他配置的默认状态
                    for c in data["configs"]:
                        c["is_default"] = False
                config["is_default"] = update.is_default

            data["configs"][i] = config
            _save_configs(data)
            return _config_to_response(config)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"配置不存在: {config_id}",
    )


@router.delete("/{config_id}")
async def delete_ai_config(config_id: str) -> dict:
    """删除 AI 配置"""
    data = _load_configs()

    for i, config in enumerate(data["configs"]):
        if config["id"] == config_id:
            deleted = data["configs"].pop(i)
            _save_configs(data)
            return {"success": True, "message": f"已删除配置: {deleted['name']}"}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"配置不存在: {config_id}",
    )


@router.post("/{config_id}/set-default")
async def set_default_config(config_id: str) -> dict:
    """设置默认配置"""
    data = _load_configs()

    found = False
    for config in data["configs"]:
        if config["id"] == config_id:
            config["is_default"] = True
            found = True
        else:
            config["is_default"] = False

    if not found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"配置不存在: {config_id}",
        )

    _save_configs(data)
    return {"success": True, "message": "已设置为默认配置"}


@router.post("/{config_id}/test")
async def test_ai_config(config_id: str) -> dict:
    """测试 AI 配置是否可用"""
    data = _load_configs()

    config = None
    for c in data["configs"]:
        if c["id"] == config_id:
            config = c
            break

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"配置不存在: {config_id}",
        )

    try:
        # 根据提供商类型测试连接
        provider = config["provider"]
        api_key = config["api_key"]
        model = config["model"]
        base_url = config.get("base_url")

        if provider == "qwen":
            import dashscope
            from dashscope import Generation

            dashscope.api_key = api_key
            response = Generation.call(
                model=model,
                prompt="你好，这是一个测试消息，请回复'测试成功'。",
                result_format="message",
            )
            if response.status_code == 200:
                return {"success": True, "message": "连接测试成功"}
            else:
                return {
                    "success": False,
                    "message": f"调用失败: {response.code} - {response.message}",
                }

        elif provider in ("deepseek", "openai", "custom"):
            from openai import OpenAI

            # 设置 base_url
            if provider == "deepseek":
                url = base_url or "https://api.deepseek.com"
            elif provider == "openai":
                url = base_url or "https://api.openai.com/v1"
            else:
                url = base_url
                if not url:
                    return {"success": False, "message": "自定义提供商需要设置 API 地址"}

            client = OpenAI(api_key=api_key, base_url=url, timeout=30.0)
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "你好，请回复'测试成功'"}],
                max_tokens=50,
            )
            if response.choices:
                return {"success": True, "message": "连接测试成功"}
            else:
                return {"success": False, "message": "API 返回结果异常"}

        else:
            return {"success": False, "message": f"不支持的提供商类型: {provider}"}

    except Exception as e:
        return {"success": False, "message": f"测试失败: {str(e)}"}


@router.get("/default/current")
async def get_default_config() -> dict:
    """获取当前默认配置（用于 AI 调用）"""
    data = _load_configs()

    for config in data["configs"]:
        if config.get("is_default"):
            return {
                "has_default": True,
                "config": _config_to_response(config),
            }

    return {"has_default": False, "config": None}
