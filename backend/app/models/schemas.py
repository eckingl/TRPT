"""Pydantic 数据模型"""

from datetime import datetime

from pydantic import BaseModel, Field


class GradingLevel(BaseModel):
    """分级等级"""

    level: int = Field(..., description="等级编号")
    name: str = Field(..., description="等级名称")
    min_value: float = Field(..., alias="min", description="最小值")
    max_value: float = Field(..., alias="max", description="最大值")

    model_config = {"populate_by_name": True}


class GradingStandard(BaseModel):
    """分级标准"""

    indicator: str = Field(..., description="指标名称")
    levels: list[GradingLevel] = Field(default_factory=list, description="等级列表")


class ProjectConfig(BaseModel):
    """项目配置"""

    region_name: str = Field(default="", description="区域名称")
    survey_year: int = Field(default=2024, description="普查年份")
    historical_year: int | None = Field(default=None, description="历史对比年份")
    grading_standards: dict[str, list[GradingLevel]] = Field(
        default_factory=dict, description="分级标准"
    )


class FileUploadResponse(BaseModel):
    """文件上传响应"""

    filename: str = Field(..., description="文件名")
    file_path: str = Field(..., description="文件路径")
    rows: int = Field(..., description="数据行数")
    columns: list[str] = Field(..., description="列名列表")
    preview: list[dict] = Field(default_factory=list, description="数据预览")


class TopicInfo(BaseModel):
    """专题信息"""

    id: str = Field(..., description="专题ID")
    name: str = Field(..., description="专题名称")


class ReportGenerateRequest(BaseModel):
    """报告生成请求"""

    topic_id: str = Field(..., description="专题ID")
    config: ProjectConfig = Field(..., description="项目配置")


class ReportGenerateResponse(BaseModel):
    """报告生成响应"""

    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="消息")
    report_path: str | None = Field(default=None, description="报告路径")
    generated_at: datetime = Field(default_factory=datetime.now, description="生成时间")


class HealthResponse(BaseModel):
    """健康检查响应"""

    status: str = Field(default="ok", description="状态")
    version: str = Field(..., description="版本号")
