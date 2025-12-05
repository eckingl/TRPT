"""API 路由模块"""

from fastapi import APIRouter

from app.api import config, report, upload

router = APIRouter(prefix="/api")

router.include_router(upload.router, tags=["upload"])
router.include_router(config.router, tags=["config"])
router.include_router(report.router, tags=["report"])
