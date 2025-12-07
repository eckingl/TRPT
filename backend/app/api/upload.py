"""文件上传 API"""

import shutil
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.config import get_settings
from app.core.data import load_csv
from app.models import FileUploadResponse

router = APIRouter()
settings = get_settings()


class UploadedFileInfo(BaseModel):
    """已上传文件信息"""

    filename: str
    file_path: str
    size: int
    upload_time: str
    rows: int | None = None
    columns: list[str] | None = None


class UploadedFilesResponse(BaseModel):
    """已上传文件列表响应"""

    files: list[UploadedFileInfo]
    total: int


def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    return Path(filename).suffix.lower()


def generate_unique_filename(original_filename: str) -> str:
    """生成唯一文件名，保留原文件名并添加时间戳

    格式: 原文件名_时间戳.扩展名
    例如: 样点统计数据_20241208_143025.csv
    """
    ext = get_file_extension(original_filename)
    # 获取不含扩展名的原文件名
    name_without_ext = Path(original_filename).stem
    # 清理文件名中的特殊字符
    safe_name = "".join(c for c in name_without_ext if c.isalnum() or c in "._- 中文")
    # 保留中文字符
    safe_name = name_without_ext.replace("/", "_").replace("\\", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{safe_name}_{timestamp}{ext}"


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


@router.get("/upload/files", response_model=UploadedFilesResponse)
async def list_uploaded_files() -> UploadedFilesResponse:
    """获取已上传文件列表

    Returns:
        已上传文件列表
    """
    files: list[UploadedFileInfo] = []

    if not settings.UPLOAD_DIR.exists():
        return UploadedFilesResponse(files=[], total=0)

    for file_path in settings.UPLOAD_DIR.iterdir():
        if not file_path.is_file():
            continue

        ext = get_file_extension(file_path.name)
        if ext not in settings.ALLOWED_EXTENSIONS:
            continue

        # 获取文件信息
        stat = file_path.stat()
        upload_time = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")

        # 尝试读取文件获取行数和列信息
        rows = None
        columns = None
        try:
            if ext == ".csv":
                df = load_csv(file_path)
            else:
                import pandas as pd

                df = pd.read_excel(file_path)
            rows = len(df)
            columns = df.columns.tolist()
        except Exception:
            pass

        files.append(
            UploadedFileInfo(
                filename=file_path.name,
                file_path=str(file_path),
                size=stat.st_size,
                upload_time=upload_time,
                rows=rows,
                columns=columns,
            )
        )

    # 按上传时间倒序排序
    files.sort(key=lambda x: x.upload_time, reverse=True)

    return UploadedFilesResponse(files=files, total=len(files))


@router.get("/upload/files/{filename}", response_model=FileUploadResponse)
async def get_uploaded_file_info(filename: str) -> FileUploadResponse:
    """获取单个已上传文件的详细信息

    Args:
        filename: 文件名

    Returns:
        文件详细信息，包含数据预览
    """
    file_path = settings.UPLOAD_DIR / filename

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"文件不存在: {filename}",
        )

    ext = get_file_extension(filename)
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型: {ext}",
        )

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
            filename=filename,
            file_path=str(file_path),
            rows=rows,
            columns=columns,
            preview=preview,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件读取失败: {str(e)}",
        )


@router.delete("/upload/files/{filename}")
async def delete_uploaded_file(filename: str) -> dict:
    """删除已上传的文件

    Args:
        filename: 文件名

    Returns:
        删除结果
    """
    file_path = settings.UPLOAD_DIR / filename

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"文件不存在: {filename}",
        )

    try:
        file_path.unlink()
        return {"success": True, "message": f"文件 {filename} 已删除"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除失败: {str(e)}",
        )


@router.delete("/upload/files")
async def delete_multiple_files(filenames: list[str]) -> dict:
    """批量删除已上传的文件

    Args:
        filenames: 文件名列表

    Returns:
        删除结果
    """
    deleted = []
    failed = []

    for filename in filenames:
        file_path = settings.UPLOAD_DIR / filename
        if file_path.exists():
            try:
                file_path.unlink()
                deleted.append(filename)
            except Exception as e:
                failed.append({"filename": filename, "error": str(e)})
        else:
            failed.append({"filename": filename, "error": "文件不存在"})

    return {
        "success": len(failed) == 0,
        "deleted_count": len(deleted),
        "failed_count": len(failed),
        "deleted": deleted,
        "failed": failed,
    }


@router.get("/upload/stats")
async def get_upload_stats() -> dict:
    """获取上传文件统计信息

    Returns:
        统计信息
    """
    if not settings.UPLOAD_DIR.exists():
        return {
            "total_files": 0,
            "total_size": 0,
            "total_size_readable": "0 B",
            "file_types": {},
        }

    total_files = 0
    total_size = 0
    file_types: dict[str, int] = {}

    for file_path in settings.UPLOAD_DIR.iterdir():
        if not file_path.is_file():
            continue

        ext = get_file_extension(file_path.name)
        if ext not in settings.ALLOWED_EXTENSIONS:
            continue

        total_files += 1
        total_size += file_path.stat().st_size

        if ext in file_types:
            file_types[ext] += 1
        else:
            file_types[ext] = 1

    # 格式化文件大小
    def format_size(size: int) -> str:
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.2f} GB"

    return {
        "total_files": total_files,
        "total_size": total_size,
        "total_size_readable": format_size(total_size),
        "file_types": file_types,
    }
