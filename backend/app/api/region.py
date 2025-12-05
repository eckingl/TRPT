"""地区管理 API"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.core.database import db

router = APIRouter()


class RegionCreate(BaseModel):
    """创建地区请求"""

    name: str = Field(..., min_length=1, description="地区名称")
    category: str = Field(..., description="大类")
    topic: str = Field(..., description="专题")
    item: str = Field(..., description="具体项目")


class RegionUpdate(BaseModel):
    """更新地区请求"""

    name: str = Field(..., min_length=1, description="地区名称")


class RegionResponse(BaseModel):
    """地区响应"""

    id: int
    name: str
    category: str
    topic: str
    item: str
    created_at: str
    updated_at: str


class RegionListResponse(BaseModel):
    """地区列表响应"""

    regions: list[RegionResponse]
    total: int


@router.post("/regions", response_model=RegionResponse)
async def create_region(data: RegionCreate) -> RegionResponse:
    """创建新地区

    Args:
        data: 地区创建数据

    Returns:
        创建的地区信息

    Raises:
        HTTPException: 地区已存在
    """
    try:
        region_id = await db.create_region(
            name=data.name,
            category=data.category,
            topic=data.topic,
            item=data.item,
        )
        region = await db.get_region_by_id(region_id)
        if not region:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建地区失败",
            )
        return RegionResponse(**region)
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该地区已存在",
            )
        raise


@router.get("/regions", response_model=RegionListResponse)
async def list_regions(
    category: str | None = None,
    topic: str | None = None,
    item: str | None = None,
) -> RegionListResponse:
    """获取地区列表

    Args:
        category: 筛选大类
        topic: 筛选专题
        item: 筛选具体项目

    Returns:
        地区列表
    """
    regions = await db.get_regions(category=category, topic=topic, item=item)
    return RegionListResponse(
        regions=[RegionResponse(**r) for r in regions],
        total=len(regions),
    )


@router.get("/regions/{region_id}", response_model=RegionResponse)
async def get_region(region_id: int) -> RegionResponse:
    """获取单个地区详情

    Args:
        region_id: 地区ID

    Returns:
        地区信息

    Raises:
        HTTPException: 地区不存在
    """
    region = await db.get_region_by_id(region_id)
    if not region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="地区不存在",
        )
    return RegionResponse(**region)


@router.put("/regions/{region_id}", response_model=RegionResponse)
async def update_region(region_id: int, data: RegionUpdate) -> RegionResponse:
    """更新地区名称

    Args:
        region_id: 地区ID
        data: 更新数据

    Returns:
        更新后的地区信息

    Raises:
        HTTPException: 地区不存在
    """
    region = await db.get_region_by_id(region_id)
    if not region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="地区不存在",
        )

    await db.update_region(region_id, data.name)
    updated_region = await db.get_region_by_id(region_id)
    if not updated_region:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新失败",
        )
    return RegionResponse(**updated_region)


@router.delete("/regions/{region_id}")
async def delete_region(region_id: int) -> dict:
    """删除地区及其所有数据

    Args:
        region_id: 地区ID

    Returns:
        删除结果

    Raises:
        HTTPException: 地区不存在
    """
    region = await db.get_region_by_id(region_id)
    if not region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="地区不存在",
        )

    await db.delete_region(region_id)
    return {"success": True, "message": "删除成功"}
