"""文件上传 API"""

from fastapi import APIRouter, HTTPException, UploadFile, status

from app.models import FileUploadResponse

router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile) -> FileUploadResponse:
    """上传数据文件

    Args:
        file: 上传的文件

    Returns:
        文件上传响应，包含文件信息和数据预览

    Raises:
        HTTPException: 文件类型不支持或文件过大
    """
    # TODO: P2 阶段实现
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="文件上传功能将在 P2 阶段实现",
    )
