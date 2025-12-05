"""报告生成 API"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse

from app.models import (
    ReportGenerateRequest,
    ReportGenerateResponse,
    TopicInfo,
)
from app.topics import get_available_topics

router = APIRouter()


@router.get("/topics", response_model=list[TopicInfo])
async def list_topics() -> list[TopicInfo]:
    """获取可用专题列表

    Returns:
        专题列表
    """
    topics = get_available_topics()
    return [TopicInfo(**topic) for topic in topics]


@router.post("/report/generate", response_model=ReportGenerateResponse)
async def generate_report(request: ReportGenerateRequest) -> ReportGenerateResponse:
    """生成报告

    Args:
        request: 报告生成请求

    Returns:
        报告生成响应

    Raises:
        HTTPException: 专题不存在或生成失败
    """
    # TODO: P4 阶段实现
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="报告生成功能将在 P4 阶段实现",
    )


@router.get("/report/preview/{report_id}")
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


@router.get("/report/download/{report_id}")
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
