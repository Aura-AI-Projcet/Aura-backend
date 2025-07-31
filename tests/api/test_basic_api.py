"""
基本 API 测试
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def test_app():
    """创建测试用的 FastAPI 应用"""
    app = FastAPI(
        title="Aura Backend API - Test Mode",
        description="Basic test without Supabase connection",
        version="1.0.0-test"
    )

    @app.get("/health")
    async def health_check():
        """健康检查端点"""
        return {
            "status": "healthy", 
            "environment": "test",
            "version": "1.0.0-test",
            "message": "Basic API is working"
        }

    @app.get("/api/v1/health")
    async def api_health_check():
        """API-级别健康检查"""
        return {"status": "healthy", "message": "API is running in test mode"}

    @app.get("/")
    async def root():
        """根端点"""
        return {"message": "Welcome to Aura Backend API (Test Mode)"}

    @app.get("/api/v1/onboarding/avatars")
    async def get_test_avatars():
        """测试虚拟形象端点"""
        return [
            {
                "id": "test-avatar-1",
                "name": "星语者·小满",
                "description": "温柔而智慧的星相导师",
                "image_url": "/avatars/xiaoman.png",
                "abilities": ["星座分析", "生辰八字", "人际关系", "情感咨询"]
            },
            {
                "id": "test-avatar-2", 
                "name": "塔罗师·月影",
                "description": "神秘的塔罗牌大师",
                "image_url": "/avatars/yueying.png",
                "abilities": ["塔罗占卜", "灵性指导", "直觉洞察", "人生指引"]
            }
        ]
    
    return app


@pytest.fixture
def client(test_app):
    """创建测试客户端"""
    return TestClient(test_app)


def test_health_check(client):
    """测试健康检查端点"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["environment"] == "test"
    assert data["version"] == "1.0.0-test"


def test_api_health_check(client):
    """测试 API 级别健康检查"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "test mode" in data["message"]


def test_root_endpoint(client):
    """测试根端点"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Welcome to Aura Backend API" in data["message"]


def test_avatars_endpoint(client):
    """测试虚拟形象端点"""
    response = client.get("/api/v1/onboarding/avatars")
    assert response.status_code == 200
    avatars = response.json()
    assert len(avatars) == 2
    
    # 验证第一个形象
    avatar1 = avatars[0]
    assert avatar1["id"] == "test-avatar-1"
    assert avatar1["name"] == "星语者·小满"
    assert "星座分析" in avatar1["abilities"]
    
    # 验证第二个形象
    avatar2 = avatars[1]
    assert avatar2["id"] == "test-avatar-2"
    assert avatar2["name"] == "塔罗师·月影"
    assert "塔罗占卜" in avatar2["abilities"]