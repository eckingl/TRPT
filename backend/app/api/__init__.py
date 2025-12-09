"""API 路由模块"""

from fastapi import APIRouter

from app.api import (
    ai_config,
    config,
    data_manage,
    grading,
    region,
    report,
    topic_config,
    upload,
)

router = APIRouter(prefix="/api")

router.include_router(upload.router, tags=["upload"])
router.include_router(config.router, tags=["config"])
router.include_router(report.router, tags=["report"])
router.include_router(region.router, tags=["region"])
router.include_router(data_manage.router, tags=["data-manage"])
router.include_router(ai_config.router, tags=["ai-config"])
router.include_router(grading.router, tags=["grading"])
router.include_router(topic_config.router, tags=["topic-config"])
