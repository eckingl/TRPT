"""数据管理 API - 提供数据的增删改查功能"""

import json
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.core.database import db

router = APIRouter(prefix="/data-manage")


# ==================== 请求/响应模型 ====================


class RegionCreate(BaseModel):
    """创建地区请求"""

    name: str = Field(..., description="地区名称")
    category: str = Field(..., description="大类")
    topic: str = Field(..., description="专题")
    item: str = Field(default="default", description="具体项目")
    province: str | None = Field(default=None, description="省份")
    city: str | None = Field(default=None, description="城市")
    county: str | None = Field(default=None, description="区县")


class RegionUpdate(BaseModel):
    """更新地区请求"""

    name: str = Field(..., description="地区名称")


class ProjectDataCreate(BaseModel):
    """创建项目数据请求"""

    region_id: int = Field(..., description="地区ID")
    data_type: str = Field(..., description="数据类型")
    data_content: str = Field(..., description="数据内容(JSON字符串)")
    file_name: str | None = Field(default=None, description="文件名")


class ProjectDataUpdate(BaseModel):
    """更新项目数据请求"""

    data_content: str = Field(..., description="数据内容(JSON字符串)")


class ProjectConfigUpdate(BaseModel):
    """更新项目配置请求"""

    config: dict = Field(..., description="配置内容")


# ==================== 统计接口 ====================


@router.get("/stats")
async def get_database_stats() -> dict:
    """获取数据库统计信息"""
    import aiosqlite

    async with aiosqlite.connect(db.db_path) as conn:
        # 地区数量
        cursor = await conn.execute("SELECT COUNT(*) FROM regions")
        regions_count = (await cursor.fetchone())[0]

        # 项目数据数量
        cursor = await conn.execute("SELECT COUNT(*) FROM project_data")
        data_count = (await cursor.fetchone())[0]

        # 配置数量
        cursor = await conn.execute("SELECT COUNT(*) FROM project_config")
        config_count = (await cursor.fetchone())[0]

        # 按类别统计地区
        cursor = await conn.execute(
            "SELECT category, COUNT(*) as count FROM regions GROUP BY category"
        )
        category_stats = [
            {"category": row[0], "count": row[1]} for row in await cursor.fetchall()
        ]

        # 按专题统计地区
        cursor = await conn.execute(
            "SELECT topic, COUNT(*) as count FROM regions GROUP BY topic"
        )
        topic_stats = [
            {"topic": row[0], "count": row[1]} for row in await cursor.fetchall()
        ]

        # 数据库文件大小
        import os

        db_size = os.path.getsize(db.db_path) if db.db_path.exists() else 0

    return {
        "regions_count": regions_count,
        "data_count": data_count,
        "config_count": config_count,
        "category_stats": category_stats,
        "topic_stats": topic_stats,
        "db_size_bytes": db_size,
        "db_size_mb": round(db_size / 1024 / 1024, 2),
    }


# ==================== 地区管理 ====================


@router.get("/regions")
async def list_all_regions(
    category: str | None = Query(default=None, description="按类别筛选"),
    topic: str | None = Query(default=None, description="按专题筛选"),
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量"),
) -> dict:
    """获取所有地区列表（分页）"""
    regions = await db.get_regions(category=category, topic=topic)

    # 分页
    total = len(regions)
    start = (page - 1) * page_size
    end = start + page_size
    items = regions[start:end]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.get("/regions/{region_id}")
async def get_region_detail(region_id: int) -> dict:
    """获取地区详情（包含数据和配置）"""
    region = await db.get_region_by_id(region_id)
    if not region:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="地区不存在")

    # 获取关联的数据
    project_data = await db.get_project_data(region_id)

    # 获取配置
    config = await db.get_project_config(region_id)

    return {
        "region": region,
        "project_data": project_data,
        "config": config,
    }


@router.post("/regions")
async def create_region(request: RegionCreate) -> dict:
    """创建新地区"""
    try:
        region_id = await db.create_region(
            name=request.name,
            category=request.category,
            topic=request.topic,
            item=request.item,
            province=request.province,
            city=request.city,
            county=request.county,
        )
        return {"id": region_id, "message": "创建成功"}
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该地区已存在",
            ) from None
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.put("/regions/{region_id}")
async def update_region(region_id: int, request: RegionUpdate) -> dict:
    """更新地区信息"""
    region = await db.get_region_by_id(region_id)
    if not region:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="地区不存在")

    await db.update_region(region_id, request.name)
    return {"message": "更新成功"}


@router.delete("/regions/{region_id}")
async def delete_region(region_id: int) -> dict:
    """删除地区（同时删除关联的数据和配置）"""
    region = await db.get_region_by_id(region_id)
    if not region:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="地区不存在")

    await db.delete_region(region_id)
    return {"message": "删除成功"}


# ==================== 项目数据管理 ====================


@router.get("/project-data")
async def list_project_data(
    region_id: int | None = Query(default=None, description="按地区ID筛选"),
    data_type: str | None = Query(default=None, description="按数据类型筛选"),
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量"),
) -> dict:
    """获取项目数据列表"""
    import aiosqlite

    async with aiosqlite.connect(db.db_path) as conn:
        conn.row_factory = aiosqlite.Row

        query = """
            SELECT pd.*, r.name as region_name
            FROM project_data pd
            LEFT JOIN regions r ON pd.region_id = r.id
            WHERE 1=1
        """
        params = []

        if region_id is not None:
            query += " AND pd.region_id = ?"
            params.append(region_id)
        if data_type:
            query += " AND pd.data_type = ?"
            params.append(data_type)

        query += " ORDER BY pd.updated_at DESC"

        cursor = await conn.execute(query, params)
        all_rows = await cursor.fetchall()

    # 转换为字典并计算数据大小
    items_full = []
    for row in all_rows:
        item = dict(row)
        # 计算数据大小
        content = item.get("data_content", "")
        item["data_size"] = len(content) if content else 0
        # 预览数据（前200字符）
        item["data_preview"] = content[:200] + "..." if len(content) > 200 else content
        items_full.append(item)

    # 分页
    total = len(items_full)
    start = (page - 1) * page_size
    end = start + page_size
    items = items_full[start:end]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.get("/project-data/{data_id}")
async def get_project_data_detail(data_id: int) -> dict:
    """获取项目数据详情"""
    import aiosqlite

    async with aiosqlite.connect(db.db_path) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            """
            SELECT pd.*, r.name as region_name
            FROM project_data pd
            LEFT JOIN regions r ON pd.region_id = r.id
            WHERE pd.id = ?
            """,
            (data_id,),
        )
        row = await cursor.fetchone()

    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="数据不存在")

    item = dict(row)

    # 尝试解析JSON
    try:
        item["data_parsed"] = json.loads(item["data_content"])
    except (json.JSONDecodeError, TypeError):
        item["data_parsed"] = None

    return item


@router.post("/project-data")
async def create_project_data(request: ProjectDataCreate) -> dict:
    """创建项目数据"""
    # 验证地区存在
    region = await db.get_region_by_id(request.region_id)
    if not region:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="地区不存在")

    data_id = await db.save_project_data(
        region_id=request.region_id,
        data_type=request.data_type,
        data_content=request.data_content,
        file_name=request.file_name,
    )

    return {"id": data_id, "message": "创建成功"}


@router.put("/project-data/{data_id}")
async def update_project_data(data_id: int, request: ProjectDataUpdate) -> dict:
    """更新项目数据"""
    import aiosqlite

    now = datetime.now().isoformat()

    async with aiosqlite.connect(db.db_path) as conn:
        # 检查数据是否存在
        cursor = await conn.execute(
            "SELECT id FROM project_data WHERE id = ?", (data_id,)
        )
        if not await cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="数据不存在"
            )

        # 更新数据
        await conn.execute(
            "UPDATE project_data SET data_content = ?, updated_at = ? WHERE id = ?",
            (request.data_content, now, data_id),
        )
        await conn.commit()

    return {"message": "更新成功"}


@router.delete("/project-data/{data_id}")
async def delete_project_data(data_id: int) -> dict:
    """删除项目数据"""
    import aiosqlite

    async with aiosqlite.connect(db.db_path) as conn:
        # 检查数据是否存在
        cursor = await conn.execute(
            "SELECT id FROM project_data WHERE id = ?", (data_id,)
        )
        if not await cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="数据不存在"
            )

        await conn.execute("DELETE FROM project_data WHERE id = ?", (data_id,))
        await conn.commit()

    return {"message": "删除成功"}


# ==================== 项目配置管理 ====================


@router.get("/project-config/{region_id}")
async def get_project_config(region_id: int) -> dict:
    """获取项目配置"""
    region = await db.get_region_by_id(region_id)
    if not region:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="地区不存在")

    config = await db.get_project_config(region_id)
    return {"region_id": region_id, "config": config}


@router.put("/project-config/{region_id}")
async def update_project_config(region_id: int, request: ProjectConfigUpdate) -> dict:
    """更新项目配置"""
    region = await db.get_region_by_id(region_id)
    if not region:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="地区不存在")

    await db.save_project_config(region_id, request.config)
    return {"message": "更新成功"}


# ==================== 批量操作 ====================


@router.post("/batch-delete/regions")
async def batch_delete_regions(region_ids: list[int]) -> dict:
    """批量删除地区"""
    deleted = 0
    for region_id in region_ids:
        try:
            await db.delete_region(region_id)
            deleted += 1
        except Exception:
            pass

    return {"deleted": deleted, "total": len(region_ids)}


@router.post("/batch-delete/project-data")
async def batch_delete_project_data(data_ids: list[int]) -> dict:
    """批量删除项目数据"""
    import aiosqlite

    deleted = 0
    async with aiosqlite.connect(db.db_path) as conn:
        for data_id in data_ids:
            try:
                await conn.execute("DELETE FROM project_data WHERE id = ?", (data_id,))
                deleted += 1
            except Exception:
                pass
        await conn.commit()

    return {"deleted": deleted, "total": len(data_ids)}
