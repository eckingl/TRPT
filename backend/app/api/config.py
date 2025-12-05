"""配置管理 API"""

from fastapi import APIRouter

from app.models import GradingStandard, ProjectConfig

router = APIRouter()


@router.get("/config", response_model=ProjectConfig)
async def get_config() -> ProjectConfig:
    """获取项目配置

    Returns:
        当前项目配置
    """
    # 返回默认配置
    return ProjectConfig()


@router.post("/config", response_model=ProjectConfig)
async def save_config(config: ProjectConfig) -> ProjectConfig:
    """保存项目配置

    Args:
        config: 项目配置

    Returns:
        保存后的配置
    """
    # TODO: P2 阶段实现配置持久化
    return config


@router.get("/config/grading/{indicator}", response_model=GradingStandard)
async def get_grading_standard(indicator: str) -> GradingStandard:
    """获取指定指标的分级标准

    Args:
        indicator: 指标名称

    Returns:
        分级标准
    """
    # 返回空的分级标准
    return GradingStandard(indicator=indicator, levels=[])


@router.post("/config/grading", response_model=GradingStandard)
async def save_grading_standard(standard: GradingStandard) -> GradingStandard:
    """保存分级标准

    Args:
        standard: 分级标准

    Returns:
        保存后的分级标准
    """
    # TODO: P2 阶段实现
    return standard
