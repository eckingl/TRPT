"""FastAPI 应用入口"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import router as api_router
from app.config import get_settings
from app.models import HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理"""
    settings = get_settings()
    print(f"[启动] {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"[配置] 模板目录: {settings.TEMPLATES_DIR}")
    print(f"[配置] 输出目录: {settings.OUTPUT_DIR}")
    yield
    print("[关闭] 应用已关闭")


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="农业土壤普查报告自动生成系统",
        lifespan=lifespan,
    )

    # 配置 CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册 API 路由
    app.include_router(api_router)

    # 健康检查端点
    @app.get("/api/health", response_model=HealthResponse)
    async def health_check() -> HealthResponse:
        """健康检查"""
        return HealthResponse(status="ok", version=settings.APP_VERSION)

    # 挂载静态文件（前端构建产物）
    frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
    if frontend_dist.exists():
        app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
