"""专题配置管理 API"""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.topic_config import (
    AttributeMapConfig,
    AttributeMapDataConfig,
    AttributeMapMappingConfig,
    AttributeMapStatsConfig,
    DataReportConfig,
    DataReportDataConfig,
    DataReportOutputConfig,
    DataReportStatsConfig,
    TopicRegionConfig,
    topic_config_manager,
)

router = APIRouter(prefix="/topic-config", tags=["topic-config"])


class TopicConfigSummary(BaseModel):
    """配置摘要"""

    region_id: int
    region_name: str
    updated_at: str


class CreateConfigRequest(BaseModel):
    """创建配置请求"""

    topic: str
    region_id: int
    region_name: str


class UpdateAttributeMapDataRequest(BaseModel):
    """更新属性图数据处理配置请求"""

    enabled_attributes: list[str] = Field(default_factory=list)
    area_column: str = "面积"
    town_column: str = "XZQMC"
    land_use_column: str = "TDLYLX"


class UpdateAttributeMapMappingRequest(BaseModel):
    """更新属性图上图配置请求"""

    color_scheme: str = "default"
    legend_position: str = "bottom_right"
    show_labels: bool = True


class UpdateAttributeMapStatsRequest(BaseModel):
    """更新属性图统计配置请求"""

    include_town_stats: bool = True
    include_land_use_stats: bool = True
    include_soil_type_stats: bool = True
    percentile_list: list[int] = Field(
        default_factory=lambda: [2, 5, 10, 20, 80, 90, 95, 98]
    )


class UpdateBaseConfigRequest(BaseModel):
    """更新基础配置请求"""

    survey_year: int = 2024
    historical_year: int | None = None


class UpdateGradingStandardRequest(BaseModel):
    """更新分级标准请求"""

    grading_standard: str


class UpdateDataReportDataRequest(BaseModel):
    """更新数据报告数据处理配置请求"""

    enabled_attributes: list[str] = Field(default_factory=list)
    area_column: str = "面积"
    town_column: str = "XZQMC"
    land_use_column: str = "TDLYLX"
    soil_type_column: str = "YL"
    soil_subtype_column: str = "TS"


class UpdateDataReportStatsRequest(BaseModel):
    """更新数据报告统计配置请求"""

    include_town_stats: bool = True
    include_land_use_stats: bool = True
    include_soil_type_stats: bool = True
    percentile_list: list[int] = Field(
        default_factory=lambda: [2, 5, 10, 20, 80, 90, 95, 98]
    )


class UpdateDataReportOutputRequest(BaseModel):
    """更新数据报告输出配置请求"""

    output_format: str = "xlsx"
    include_summary_sheet: bool = True
    include_detail_sheets: bool = True
    decimal_places: int = 2


@router.get("/{topic}", response_model=list[TopicConfigSummary])
async def list_topic_configs(topic: str) -> list[dict[str, Any]]:
    """获取专题下的所有配置列表"""
    configs = topic_config_manager.list_configs(topic)
    return configs


@router.get("/{topic}/{region_id}")
async def get_topic_config(topic: str, region_id: int) -> dict[str, Any]:
    """获取专题-地区配置"""
    config = topic_config_manager.get_config(topic, region_id)
    if config is None:
        raise HTTPException(
            status_code=404,
            detail=f"配置不存在: topic={topic}, region_id={region_id}",
        )
    return config.model_dump()


@router.post("/{topic}/{region_id}")
async def create_or_get_topic_config(
    topic: str, region_id: int, request: CreateConfigRequest
) -> dict[str, Any]:
    """创建或获取专题-地区配置"""
    config = topic_config_manager.get_or_create_config(
        topic, region_id, request.region_name
    )
    return config.model_dump()


@router.delete("/{topic}/{region_id}")
async def delete_topic_config(topic: str, region_id: int) -> dict[str, str]:
    """删除专题-地区配置"""
    if not topic_config_manager.delete_config(topic, region_id):
        raise HTTPException(
            status_code=500,
            detail="删除配置失败",
        )
    return {"message": "配置已删除"}


@router.put("/{topic}/{region_id}/base")
async def update_base_config(
    topic: str, region_id: int, request: UpdateBaseConfigRequest
) -> dict[str, Any]:
    """更新基础配置（年份等）"""
    config = topic_config_manager.get_config(topic, region_id)
    if config is None:
        raise HTTPException(
            status_code=404,
            detail=f"配置不存在: topic={topic}, region_id={region_id}",
        )

    config.survey_year = request.survey_year
    config.historical_year = request.historical_year

    if not topic_config_manager.save_config(config):
        raise HTTPException(status_code=500, detail="保存配置失败")

    return config.model_dump()


@router.put("/{topic}/{region_id}/grading-standard")
async def update_grading_standard(
    topic: str, region_id: int, request: UpdateGradingStandardRequest
) -> dict[str, Any]:
    """更新分级标准"""
    # 根据专题类型调用不同的更新方法
    if topic == "attribute_map":
        config = topic_config_manager.update_attribute_map_grading(
            topic, region_id, request.grading_standard
        )
    elif topic == "data_report":
        config = topic_config_manager.update_data_report_grading(
            topic, region_id, request.grading_standard
        )
    else:
        raise HTTPException(
            status_code=400,
            detail=f"专题 '{topic}' 不支持分级标准配置",
        )

    if config is None:
        raise HTTPException(
            status_code=404,
            detail="配置不存在或分级标准无效",
        )
    return config.model_dump()


@router.put("/{topic}/{region_id}/attribute-map/data")
async def update_attribute_map_data_config(
    topic: str, region_id: int, request: UpdateAttributeMapDataRequest
) -> dict[str, Any]:
    """更新属性图数据处理配置"""
    config = topic_config_manager.get_config(topic, region_id)
    if config is None:
        raise HTTPException(
            status_code=404,
            detail=f"配置不存在: topic={topic}, region_id={region_id}",
        )

    if config.attribute_map is None:
        config.attribute_map = AttributeMapConfig()

    config.attribute_map.data_process = AttributeMapDataConfig(
        enabled_attributes=request.enabled_attributes,
        area_column=request.area_column,
        town_column=request.town_column,
        land_use_column=request.land_use_column,
    )

    if not topic_config_manager.save_config(config):
        raise HTTPException(status_code=500, detail="保存配置失败")

    return config.model_dump()


@router.put("/{topic}/{region_id}/attribute-map/mapping")
async def update_attribute_map_mapping_config(
    topic: str, region_id: int, request: UpdateAttributeMapMappingRequest
) -> dict[str, Any]:
    """更新属性图上图配置"""
    config = topic_config_manager.get_config(topic, region_id)
    if config is None:
        raise HTTPException(
            status_code=404,
            detail=f"配置不存在: topic={topic}, region_id={region_id}",
        )

    if config.attribute_map is None:
        config.attribute_map = AttributeMapConfig()

    config.attribute_map.mapping = AttributeMapMappingConfig(
        color_scheme=request.color_scheme,
        legend_position=request.legend_position,
        show_labels=request.show_labels,
    )

    if not topic_config_manager.save_config(config):
        raise HTTPException(status_code=500, detail="保存配置失败")

    return config.model_dump()


@router.put("/{topic}/{region_id}/attribute-map/stats")
async def update_attribute_map_stats_config(
    topic: str, region_id: int, request: UpdateAttributeMapStatsRequest
) -> dict[str, Any]:
    """更新属性图统计配置"""
    config = topic_config_manager.get_config(topic, region_id)
    if config is None:
        raise HTTPException(
            status_code=404,
            detail=f"配置不存在: topic={topic}, region_id={region_id}",
        )

    if config.attribute_map is None:
        config.attribute_map = AttributeMapConfig()

    config.attribute_map.stats = AttributeMapStatsConfig(
        include_town_stats=request.include_town_stats,
        include_land_use_stats=request.include_land_use_stats,
        include_soil_type_stats=request.include_soil_type_stats,
        percentile_list=request.percentile_list,
    )

    if not topic_config_manager.save_config(config):
        raise HTTPException(status_code=500, detail="保存配置失败")

    return config.model_dump()


# ============ 数据报告专题配置 API ============


@router.put("/{topic}/{region_id}/data-report/data")
async def update_data_report_data_config(
    topic: str, region_id: int, request: UpdateDataReportDataRequest
) -> dict[str, Any]:
    """更新数据报告数据处理配置"""
    config = topic_config_manager.get_config(topic, region_id)
    if config is None:
        raise HTTPException(
            status_code=404,
            detail=f"配置不存在: topic={topic}, region_id={region_id}",
        )

    if config.data_report is None:
        config.data_report = DataReportConfig()

    config.data_report.data_process = DataReportDataConfig(
        enabled_attributes=request.enabled_attributes,
        area_column=request.area_column,
        town_column=request.town_column,
        land_use_column=request.land_use_column,
        soil_type_column=request.soil_type_column,
        soil_subtype_column=request.soil_subtype_column,
    )

    if not topic_config_manager.save_config(config):
        raise HTTPException(status_code=500, detail="保存配置失败")

    return config.model_dump()


@router.put("/{topic}/{region_id}/data-report/stats")
async def update_data_report_stats_config(
    topic: str, region_id: int, request: UpdateDataReportStatsRequest
) -> dict[str, Any]:
    """更新数据报告统计配置"""
    config = topic_config_manager.get_config(topic, region_id)
    if config is None:
        raise HTTPException(
            status_code=404,
            detail=f"配置不存在: topic={topic}, region_id={region_id}",
        )

    if config.data_report is None:
        config.data_report = DataReportConfig()

    config.data_report.stats = DataReportStatsConfig(
        include_town_stats=request.include_town_stats,
        include_land_use_stats=request.include_land_use_stats,
        include_soil_type_stats=request.include_soil_type_stats,
        percentile_list=request.percentile_list,
    )

    if not topic_config_manager.save_config(config):
        raise HTTPException(status_code=500, detail="保存配置失败")

    return config.model_dump()


@router.put("/{topic}/{region_id}/data-report/output")
async def update_data_report_output_config(
    topic: str, region_id: int, request: UpdateDataReportOutputRequest
) -> dict[str, Any]:
    """更新数据报告输出配置"""
    config = topic_config_manager.get_config(topic, region_id)
    if config is None:
        raise HTTPException(
            status_code=404,
            detail=f"配置不存在: topic={topic}, region_id={region_id}",
        )

    if config.data_report is None:
        config.data_report = DataReportConfig()

    config.data_report.output = DataReportOutputConfig(
        output_format=request.output_format,
        include_summary_sheet=request.include_summary_sheet,
        include_detail_sheets=request.include_detail_sheets,
        decimal_places=request.decimal_places,
    )

    if not topic_config_manager.save_config(config):
        raise HTTPException(status_code=500, detail="保存配置失败")

    return config.model_dump()
