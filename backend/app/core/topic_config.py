"""专题配置管理模块

按专题和地区管理配置文件，支持属性图的数据处理、上图、统计等配置。
配置文件存储在 data/configs/{topic}/{region_id}.json
"""

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from app.config import get_settings


class GradeLevelConfig(BaseModel):
    """分级配置"""

    threshold: float
    level: str
    description: str


class AttributeGradeConfig(BaseModel):
    """属性分级配置"""

    name: str
    unit: str = ""
    reverse_display: bool = False
    land_filter: str = ""
    levels: list[GradeLevelConfig] = []


class AttributeMapDataConfig(BaseModel):
    """属性图-数据处理配置"""

    enabled_attributes: list[str] = Field(default_factory=list)
    area_column: str = "面积"
    town_column: str = "XZQMC"
    land_use_column: str = "TDLYLX"


class AttributeMapMappingConfig(BaseModel):
    """属性图-上图配置"""

    color_scheme: str = "default"
    legend_position: str = "bottom_right"
    show_labels: bool = True


class AttributeMapStatsConfig(BaseModel):
    """属性图-统计配置"""

    include_town_stats: bool = True
    include_land_use_stats: bool = True
    include_soil_type_stats: bool = True
    percentile_list: list[int] = Field(default_factory=lambda: [2, 5, 10, 20, 80, 90, 95, 98])


class AttributeMapConfig(BaseModel):
    """属性图专题配置"""

    grading_standard: str = "jiangsu"
    attributes: dict[str, AttributeGradeConfig] = Field(default_factory=dict)
    data_process: AttributeMapDataConfig = Field(default_factory=AttributeMapDataConfig)
    mapping: AttributeMapMappingConfig = Field(default_factory=AttributeMapMappingConfig)
    stats: AttributeMapStatsConfig = Field(default_factory=AttributeMapStatsConfig)


class TypeMapConfig(BaseModel):
    """类型图专题配置"""

    # 后续扩展
    pass


class SuitabilityConfig(BaseModel):
    """适宜性评价专题配置"""

    # 后续扩展
    pass


class GradeEvalConfig(BaseModel):
    """等级评价专题配置"""

    # 后续扩展
    pass


class DataReportStatsConfig(BaseModel):
    """数据报告-统计配置"""

    include_town_stats: bool = True
    include_land_use_stats: bool = True
    include_soil_type_stats: bool = True
    percentile_list: list[int] = Field(
        default_factory=lambda: [2, 5, 10, 20, 80, 90, 95, 98]
    )


class DataReportDataConfig(BaseModel):
    """数据报告-数据处理配置"""

    enabled_attributes: list[str] = Field(default_factory=list)
    area_column: str = "面积"
    town_column: str = "XZQMC"
    land_use_column: str = "TDLYLX"
    soil_type_column: str = "YL"
    soil_subtype_column: str = "TS"


class DataReportOutputConfig(BaseModel):
    """数据报告-输出配置"""

    output_format: str = "xlsx"
    include_summary_sheet: bool = True
    include_detail_sheets: bool = True
    decimal_places: int = 2


class DataReportConfig(BaseModel):
    """数据报告专题配置"""

    grading_standard: str = "jiangsu"
    attributes: dict[str, AttributeGradeConfig] = Field(default_factory=dict)
    data_process: DataReportDataConfig = Field(default_factory=DataReportDataConfig)
    stats: DataReportStatsConfig = Field(default_factory=DataReportStatsConfig)
    output: DataReportOutputConfig = Field(default_factory=DataReportOutputConfig)


class TopicRegionConfig(BaseModel):
    """专题-地区配置"""

    topic: str
    region_id: int
    region_name: str
    survey_year: int = 2024
    historical_year: int | None = None
    updated_at: str = ""

    # 专题特定配置
    attribute_map: AttributeMapConfig | None = None
    type_map: TypeMapConfig | None = None
    suitability: SuitabilityConfig | None = None
    grade_eval: GradeEvalConfig | None = None
    data_report: DataReportConfig | None = None


class TopicConfigManager:
    """专题配置管理器"""

    def __init__(self) -> None:
        settings = get_settings()
        self.config_dir = settings.DATA_DIR / "configs"
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def _get_topic_dir(self, topic: str) -> Path:
        """获取专题配置目录"""
        topic_dir = self.config_dir / topic
        topic_dir.mkdir(parents=True, exist_ok=True)
        return topic_dir

    def _get_config_path(self, topic: str, region_id: int) -> Path:
        """获取配置文件路径"""
        return self._get_topic_dir(topic) / f"{region_id}.json"

    def get_config(self, topic: str, region_id: int) -> TopicRegionConfig | None:
        """获取专题-地区配置

        Args:
            topic: 专题ID
            region_id: 地区ID

        Returns:
            配置对象，不存在则返回None
        """
        config_path = self._get_config_path(topic, region_id)
        if not config_path.exists():
            return None

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return TopicRegionConfig(**data)
        except Exception as e:
            print(f"[警告] 读取配置失败: {config_path}, 错误: {e}")
            return None

    def save_config(self, config: TopicRegionConfig) -> bool:
        """保存专题-地区配置

        Args:
            config: 配置对象

        Returns:
            是否保存成功
        """
        from datetime import datetime

        config.updated_at = datetime.now().isoformat()
        config_path = self._get_config_path(config.topic, config.region_id)

        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config.model_dump(), f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"[错误] 保存配置失败: {config_path}, 错误: {e}")
            return False

    def delete_config(self, topic: str, region_id: int) -> bool:
        """删除专题-地区配置

        Args:
            topic: 专题ID
            region_id: 地区ID

        Returns:
            是否删除成功
        """
        config_path = self._get_config_path(topic, region_id)
        if config_path.exists():
            try:
                config_path.unlink()
                return True
            except Exception as e:
                print(f"[错误] 删除配置失败: {config_path}, 错误: {e}")
                return False
        return True

    def list_configs(self, topic: str) -> list[dict[str, Any]]:
        """列出专题下的所有配置

        Args:
            topic: 专题ID

        Returns:
            配置摘要列表
        """
        topic_dir = self._get_topic_dir(topic)
        configs = []

        for config_file in topic_dir.glob("*.json"):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                configs.append(
                    {
                        "region_id": data.get("region_id"),
                        "region_name": data.get("region_name", ""),
                        "updated_at": data.get("updated_at", ""),
                    }
                )
            except Exception:
                continue

        return configs

    def get_or_create_config(
        self, topic: str, region_id: int, region_name: str
    ) -> TopicRegionConfig:
        """获取或创建配置

        Args:
            topic: 专题ID
            region_id: 地区ID
            region_name: 地区名称

        Returns:
            配置对象
        """
        config = self.get_config(topic, region_id)
        if config is None:
            config = TopicRegionConfig(
                topic=topic,
                region_id=region_id,
                region_name=region_name,
            )
            # 根据专题初始化默认配置
            if topic == "attribute_map":
                config.attribute_map = self._create_default_attribute_map_config()
            elif topic == "type_map":
                config.type_map = TypeMapConfig()
            elif topic == "suitability":
                config.suitability = SuitabilityConfig()
            elif topic == "grade_eval":
                config.grade_eval = GradeEvalConfig()
            elif topic == "data_report":
                config.data_report = self._create_default_data_report_config()

            self.save_config(config)

        return config

    def _create_default_attribute_map_config(self) -> AttributeMapConfig:
        """创建默认的属性图配置"""
        from app.core.grading_standards import get_attr_config, get_current_standard

        config = AttributeMapConfig()
        config.grading_standard = get_current_standard()

        # 从分级标准加载属性配置
        attrs = get_attr_config()
        for key, attr_config in attrs.items():
            levels = []
            for threshold, level, desc in attr_config.get("levels", []):
                levels.append(
                    GradeLevelConfig(
                        threshold=threshold if threshold != float("inf") else 999999,
                        level=level,
                        description=desc,
                    )
                )
            config.attributes[key] = AttributeGradeConfig(
                name=attr_config.get("name", key),
                unit=attr_config.get("unit", ""),
                reverse_display=attr_config.get("reverse_display", False),
                land_filter=attr_config.get("land_filter", ""),
                levels=levels,
            )

        return config

    def update_attribute_map_grading(
        self, topic: str, region_id: int, grading_standard: str
    ) -> TopicRegionConfig | None:
        """更新属性图的分级标准

        Args:
            topic: 专题ID
            region_id: 地区ID
            grading_standard: 分级标准ID

        Returns:
            更新后的配置
        """
        from app.core.grading_standards import get_attr_config, set_current_standard

        config = self.get_config(topic, region_id)
        if config is None or config.attribute_map is None:
            return None

        # 切换分级标准
        if not set_current_standard(grading_standard):
            return None

        config.attribute_map.grading_standard = grading_standard

        # 重新加载属性配置
        attrs = get_attr_config(grading_standard)
        config.attribute_map.attributes = {}
        for key, attr_config in attrs.items():
            levels = []
            for threshold, level, desc in attr_config.get("levels", []):
                levels.append(
                    GradeLevelConfig(
                        threshold=threshold if threshold != float("inf") else 999999,
                        level=level,
                        description=desc,
                    )
                )
            config.attribute_map.attributes[key] = AttributeGradeConfig(
                name=attr_config.get("name", key),
                unit=attr_config.get("unit", ""),
                reverse_display=attr_config.get("reverse_display", False),
                land_filter=attr_config.get("land_filter", ""),
                levels=levels,
            )

        self.save_config(config)
        return config

    def _create_default_data_report_config(self) -> DataReportConfig:
        """创建默认的数据报告配置"""
        from app.core.grading_standards import get_attr_config, get_current_standard

        config = DataReportConfig()
        config.grading_standard = get_current_standard()

        # 从分级标准加载属性配置
        attrs = get_attr_config()
        for key, attr_config in attrs.items():
            levels = []
            for threshold, level, desc in attr_config.get("levels", []):
                levels.append(
                    GradeLevelConfig(
                        threshold=threshold if threshold != float("inf") else 999999,
                        level=level,
                        description=desc,
                    )
                )
            config.attributes[key] = AttributeGradeConfig(
                name=attr_config.get("name", key),
                unit=attr_config.get("unit", ""),
                reverse_display=attr_config.get("reverse_display", False),
                land_filter=attr_config.get("land_filter", ""),
                levels=levels,
            )

        return config

    def update_data_report_grading(
        self, topic: str, region_id: int, grading_standard: str
    ) -> TopicRegionConfig | None:
        """更新数据报告的分级标准

        Args:
            topic: 专题ID
            region_id: 地区ID
            grading_standard: 分级标准ID

        Returns:
            更新后的配置
        """
        from app.core.grading_standards import get_attr_config, set_current_standard

        config = self.get_config(topic, region_id)
        if config is None or config.data_report is None:
            return None

        # 切换分级标准
        if not set_current_standard(grading_standard):
            return None

        config.data_report.grading_standard = grading_standard

        # 重新加载属性配置
        attrs = get_attr_config(grading_standard)
        config.data_report.attributes = {}
        for key, attr_config in attrs.items():
            levels = []
            for threshold, level, desc in attr_config.get("levels", []):
                levels.append(
                    GradeLevelConfig(
                        threshold=threshold if threshold != float("inf") else 999999,
                        level=level,
                        description=desc,
                    )
                )
            config.data_report.attributes[key] = AttributeGradeConfig(
                name=attr_config.get("name", key),
                unit=attr_config.get("unit", ""),
                reverse_display=attr_config.get("reverse_display", False),
                land_filter=attr_config.get("land_filter", ""),
                levels=levels,
            )

        self.save_config(config)
        return config


# 全局实例
topic_config_manager = TopicConfigManager()
