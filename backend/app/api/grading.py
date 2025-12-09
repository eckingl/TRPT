"""分级标准管理 API"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.grading_standards import (
    get_attr_config,
    get_current_standard,
    get_standard,
    list_standards,
    set_current_standard,
)

router = APIRouter(prefix="/grading", tags=["grading"])


class StandardInfo(BaseModel):
    """分级标准信息"""

    id: str
    name: str
    description: str


class StandardDetailResponse(BaseModel):
    """分级标准详情响应"""

    id: str
    name: str
    description: str
    attributes: dict


class SetStandardRequest(BaseModel):
    """设置当前标准请求"""

    standard_id: str


class CurrentStandardResponse(BaseModel):
    """当前标准响应"""

    current_standard: str
    name: str
    description: str


@router.get("/standards", response_model=list[StandardInfo])
async def get_grading_standards():
    """获取所有可用的分级标准列表"""
    standards = list_standards()
    return [
        StandardInfo(id=s["id"], name=s["name"], description=s["description"])
        for s in standards
    ]


@router.get("/standards/current", response_model=CurrentStandardResponse)
async def get_current_grading_standard():
    """获取当前使用的分级标准"""
    current = get_current_standard()
    std = get_standard(current)
    return CurrentStandardResponse(
        current_standard=current,
        name=std["name"],
        description=std["description"],
    )


@router.post("/standards/current", response_model=CurrentStandardResponse)
async def set_current_grading_standard(request: SetStandardRequest):
    """设置当前使用的分级标准"""
    if not set_current_standard(request.standard_id):
        raise HTTPException(
            status_code=404,
            detail=f"分级标准 '{request.standard_id}' 不存在",
        )
    std = get_standard(request.standard_id)
    return CurrentStandardResponse(
        current_standard=request.standard_id,
        name=std["name"],
        description=std["description"],
    )


@router.get("/standards/{standard_id}", response_model=StandardDetailResponse)
async def get_grading_standard_detail(standard_id: str):
    """获取指定分级标准的详细配置"""
    standards = {s["id"]: s for s in list_standards()}
    if standard_id not in standards:
        raise HTTPException(
            status_code=404,
            detail=f"分级标准 '{standard_id}' 不存在",
        )
    std = get_standard(standard_id)
    return StandardDetailResponse(
        id=standard_id,
        name=std["name"],
        description=std["description"],
        attributes=std["attributes"],
    )


@router.get("/attributes")
async def get_current_attributes():
    """获取当前分级标准的属性配置"""
    current = get_current_standard()
    attrs = get_attr_config(current)

    # 转换为前端友好的格式
    result = []
    for key, config in attrs.items():
        levels_info = []
        for threshold, level, desc in config.get("levels", []):
            levels_info.append(
                {
                    "threshold": threshold if threshold != float("inf") else "∞",
                    "level": level,
                    "description": desc,
                }
            )
        result.append(
            {
                "key": key,
                "name": config.get("name", key),
                "unit": config.get("unit", ""),
                "reverse_display": config.get("reverse_display", False),
                "land_filter": config.get("land_filter", ""),
                "levels": levels_info,
            }
        )

    return {"standard": current, "attributes": result}
