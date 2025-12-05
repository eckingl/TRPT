"""健康检查 API 测试"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client() -> AsyncClient:
    """创建测试客户端"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient) -> None:
    """测试健康检查端点"""
    response = await client.get("/api/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


@pytest.mark.asyncio
async def test_list_topics(client: AsyncClient) -> None:
    """测试获取专题列表"""
    response = await client.get("/api/topics")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_config(client: AsyncClient) -> None:
    """测试获取配置"""
    response = await client.get("/api/config")
    assert response.status_code == 200

    data = response.json()
    assert "region_name" in data
    assert "survey_year" in data
