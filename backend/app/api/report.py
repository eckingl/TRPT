"""报告生成 API"""

from datetime import datetime
from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

from app.config import get_settings
from app.models import (
    ReportGenerateRequest,
    ReportGenerateResponse,
)
from app.topics.attribute_map import process_attribute_data, process_mapping_data

router = APIRouter(prefix="/report")
settings = get_settings()


class AttributeDataRequest(BaseModel):
    """属性图数据处理请求"""

    sample_files: list[str] = Field(..., description="样点统计文件路径列表")
    area_files: list[str] = Field(..., description="制图统计文件路径列表")


class MappingDataRequest(BaseModel):
    """属性图上图处理请求"""

    area_files: list[str] = Field(..., description="制图统计文件路径列表")


class ProcessResponse(BaseModel):
    """处理响应"""

    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="消息")
    download_url: str | None = Field(default=None, description="下载链接")
    filename: str | None = Field(default=None, description="文件名")


@router.post("/attribute-data", response_model=ProcessResponse)
async def process_attribute_data_api(request: AttributeDataRequest) -> ProcessResponse:
    """处理属性图数据

    Args:
        request: 包含样点文件和制图文件路径的请求

    Returns:
        处理结果
    """
    # 验证文件是否存在
    for file_path in request.sample_files:
        if not Path(file_path).exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"样点文件不存在: {file_path}",
            )

    for file_path in request.area_files:
        if not Path(file_path).exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"制图文件不存在: {file_path}",
            )

    # 处理数据
    success, result = process_attribute_data(
        sample_paths=request.sample_files,
        area_paths=request.area_files,
    )

    if not success:
        return ProcessResponse(
            success=False,
            message=f"处理失败: {result}",
        )

    # 保存结果文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"属性图数据处理_{timestamp}.xlsx"
    output_path = settings.OUTPUT_DIR / output_filename

    with open(output_path, "wb") as f:
        f.write(result)

    return ProcessResponse(
        success=True,
        message="处理完成",
        download_url=f"/api/report/download/{output_filename}",
        filename=output_filename,
    )


@router.post("/mapping-data", response_model=ProcessResponse)
async def process_mapping_data_api(request: MappingDataRequest) -> ProcessResponse:
    """处理属性图上图数据

    Args:
        request: 包含制图文件路径的请求

    Returns:
        处理结果
    """
    # 验证文件是否存在
    for file_path in request.area_files:
        if not Path(file_path).exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"制图文件不存在: {file_path}",
            )

    # 处理数据
    success, result = process_mapping_data(area_paths=request.area_files)

    if not success:
        return ProcessResponse(
            success=False,
            message=f"处理失败: {result}",
        )

    # 保存结果文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"属性图上图处理_{timestamp}.xlsx"
    output_path = settings.OUTPUT_DIR / output_filename

    with open(output_path, "wb") as f:
        f.write(result)

    return ProcessResponse(
        success=True,
        message="处理完成",
        download_url=f"/api/report/download/{output_filename}",
        filename=output_filename,
    )


@router.get("/download/{filename}")
async def download_report_file(filename: str) -> StreamingResponse:
    """下载报告文件

    Args:
        filename: 文件名

    Returns:
        文件流响应
    """
    file_path = settings.OUTPUT_DIR / filename

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"文件不存在: {filename}",
        )

    def iter_file():
        with open(file_path, "rb") as f:
            yield from f

    # 设置Content-Disposition头，支持中文文件名
    encoded_filename = quote(filename)

    return StreamingResponse(
        iter_file(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        },
    )


@router.get("/list")
async def list_reports() -> list[dict]:
    """获取已生成的报告列表

    Returns:
        报告文件列表
    """
    reports = []
    for file_path in settings.OUTPUT_DIR.glob("*.xlsx"):
        stat = file_path.stat()
        reports.append(
            {
                "filename": file_path.name,
                "size": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "download_url": f"/api/report/download/{file_path.name}",
            }
        )

    # 按创建时间倒序排列
    reports.sort(key=lambda x: x["created_at"], reverse=True)
    return reports


@router.post("/generate", response_model=ReportGenerateResponse)
async def generate_report(request: ReportGenerateRequest) -> ReportGenerateResponse:
    """生成报告

    Args:
        request: 报告生成请求

    Returns:
        报告生成响应

    Raises:
        HTTPException: 专题不存在或生成失败
    """
    # TODO: P4 阶段实现完整的Word报告生成
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Word报告生成功能将在 P4 阶段实现",
    )


@router.get("/preview/{report_id}")
async def preview_report(report_id: str) -> dict:
    """预览报告

    Args:
        report_id: 报告ID

    Returns:
        预览数据

    Raises:
        HTTPException: 报告不存在
    """
    # TODO: P4 阶段实现
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="报告预览功能将在 P4 阶段实现",
    )


@router.get("/download-by-id/{report_id}")
async def download_report(report_id: str) -> FileResponse:
    """下载报告

    Args:
        report_id: 报告ID

    Returns:
        报告文件

    Raises:
        HTTPException: 报告不存在
    """
    # TODO: P4 阶段实现
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="报告下载功能将在 P4 阶段实现",
    )
