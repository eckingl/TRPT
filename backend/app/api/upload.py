"""文件上传 API"""

import shutil
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.config import get_settings
from app.core.data import load_csv
from app.models import FileUploadResponse

router = APIRouter()
settings = get_settings()


def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    return Path(filename).suffix.lower()


def generate_unique_filename(original_filename: str) -> str:
    """生成唯一文件名"""
    ext = get_file_extension(original_filename)
    unique_id = uuid.uuid4().hex[:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{timestamp}_{unique_id}{ext}"


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)) -> FileUploadResponse:
    """上传数据文件

    Args:
        file: 上传的文件

    Returns:
        文件上传响应，包含文件信息和数据预览

    Raises:
        HTTPException: 文件类型不支持或文件过大
    """
    if file.filename is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件名不能为空",
        )

    # 检查文件扩展名
    ext = get_file_extension(file.filename)
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型: {ext}，支持的类型: {', '.join(settings.ALLOWED_EXTENSIONS)}",
        )

    # 生成唯一文件名并保存
    unique_filename = generate_unique_filename(file.filename)
    file_path = settings.UPLOAD_DIR / unique_filename

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件保存失败: {str(e)}",
        )

    # 检查文件大小
    file_size = file_path.stat().st_size
    if file_size > settings.MAX_UPLOAD_SIZE:
        file_path.unlink()  # 删除文件
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件过大，最大允许 {settings.MAX_UPLOAD_SIZE // (1024 * 1024)}MB",
        )

    # 读取文件获取列信息和预览
    try:
        if ext == ".csv":
            df = load_csv(file_path)
        else:
            import pandas as pd

            df = pd.read_excel(file_path)

        columns = df.columns.tolist()
        rows = len(df)

        # 数据预览（前10行）
        preview_df = df.head(10)
        preview = preview_df.to_dict(orient="records")

        return FileUploadResponse(
            filename=file.filename,
            file_path=str(file_path),
            rows=rows,
            columns=columns,
            preview=preview,
        )

    except Exception as e:
        file_path.unlink()  # 删除文件
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件读取失败: {str(e)}",
        )


@router.post("/upload/multiple")
async def upload_multiple_files(
    files: list[UploadFile] = File(...),
) -> list[FileUploadResponse]:
    """上传多个数据文件

    Args:
        files: 上传的文件列表

    Returns:
        文件上传响应列表
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="未上传任何文件",
        )

    responses = []
    for file in files:
        response = await upload_file(file)
        responses.append(response)

    return responses
