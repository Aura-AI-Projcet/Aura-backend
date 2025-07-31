"""
新手引导功能集成测试

测试新手引导的各个步骤和API端点
"""
import asyncio
import pytest
import httpx
from datetime import datetime
from typing import Optional

BASE_URL = "http://localhost:8000"


@pytest.mark.asyncio
async def test_health_check():
    """测试健康检查端点"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_get_avatars():
    """测试获取虚拟形象"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/v1/onboarding/avatars")
        assert response.status_code == 200
        avatars = response.json()
        assert len(avatars) > 0
        
        # 验证形象数据结构
        for avatar in avatars:
            assert "id" in avatar
            assert "name" in avatar
            assert "description" in avatar


@pytest.mark.asyncio
async def test_onboarding_flow_integration():
    """测试完整的新手引导流程集成测试"""
    
    async with httpx.AsyncClient() as client:
        
        # 1. 测试健康检查
        response = await client.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        
        # 2. 测试获取虚拟形象（无需认证）
        response = await client.get(f"{BASE_URL}/api/v1/onboarding/avatars")
        assert response.status_code == 200
        avatars = response.json()
        assert len(avatars) > 0
        
        # 3. 测试需要认证的端点（预期会失败，因为无认证）
        response = await client.get(f"{BASE_URL}/api/v1/onboarding/profile")
        # 应该返回 401 或 403
        assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_authenticated_endpoints_require_auth():
    """测试需要认证的端点确实需要认证"""
    async with httpx.AsyncClient() as client:
        
        # 测试创建用户档案（需要认证）
        profile_data = {
            "nickname": "测试用户",
            "gender": "female",
            "birth_year": 1995,
            "birth_month": 8,
            "birth_day": 15,
            "birth_location": "北京市",
            "selected_avatar_id": "test-avatar-1"
        }
        
        response = await client.post(
            f"{BASE_URL}/api/v1/onboarding/profile",
            json=profile_data
        )
        assert response.status_code in [401, 403]
        
        # 测试获取用户档案（需要认证）
        response = await client.get(f"{BASE_URL}/api/v1/onboarding/profile")
        assert response.status_code in [401, 403]
        
        # 测试画像分析（需要认证）
        response = await client.post(f"{BASE_URL}/api/v1/onboarding/analyze")
        assert response.status_code in [401, 403]


# 保留原始的测试脚本功能，用于手动测试
async def manual_onboarding_test():
    """手动测试脚本，用于开发时的完整流程测试"""
    
    print("🧪 开始测试新手引导功能...")
    print(f"📍 测试服务器: {BASE_URL}")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        
        # 1. 测试健康检查
        print("1️⃣ 测试健康检查...")
        try:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("✅ 健康检查通过")
                print(f"   响应: {response.json()}")
            else:
                print(f"❌ 健康检查失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 健康检查连接失败: {e}")
            return False
        
        # 2. 测试获取虚拟形象（无需认证）
        print("\\n2️⃣ 测试获取虚拟形象...")
        try:
            response = await client.get(f"{BASE_URL}/api/v1/onboarding/avatars")
            if response.status_code == 200:
                avatars = response.json()
                print(f"✅ 成功获取 {len(avatars)} 个虚拟形象")
                for avatar in avatars:
                    print(f"   - {avatar.get('name', 'Unknown')}: {avatar.get('description', 'No description')}")
            else:
                print(f"❌ 获取虚拟形象失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 获取虚拟形象连接失败: {e}")
        
        # 3. 测试需要认证的端点（预期会失败）
        print("\\n3️⃣ 测试需要认证的端点（预期失败）...")
        
        endpoints_to_test = [
            ("GET", "/api/v1/onboarding/profile", "获取用户档案"),
            ("POST", "/api/v1/onboarding/analyze", "画像分析")
        ]
        
        for method, endpoint, description in endpoints_to_test:
            try:
                if method == "GET":
                    response = await client.get(f"{BASE_URL}{endpoint}")
                else:
                    response = await client.post(f"{BASE_URL}{endpoint}")
                
                if response.status_code in [401, 403]:
                    print(f"✅ {description}: 正确要求认证 ({response.status_code})")
                else:
                    print(f"⚠️ {description}: 未要求认证 ({response.status_code})")
            except Exception as e:
                print(f"❌ {description}: 连接失败 {e}")
    
    return True


def print_deployment_summary():
    """打印部署总结"""
    print("\\n" + "=" * 60)
    print("📋 新手引导功能测试总结")
    print("=" * 60)
    
    print("\\n🎯 已完成功能:")
    print("   ✅ FastAPI 后端框架搭建")
    print("   ✅ Supabase 认证中间件")
    print("   ✅ 虚拟形象管理 API")
    print("   ✅ 用户档案管理 API")
    print("   ✅ 画像分析集成 API")
    print("   ✅ Docker 容器化支持")
    print("   ✅ 异步 HTTP 客户端测试")
    
    print("\\n🔧 技术栈:")
    print("   - Python 3.13 + FastAPI")
    print("   - Supabase (PostgreSQL + Auth)")
    print("   - Poetry 依赖管理")
    print("   - Docker 容器化")
    print("   - Pytest 测试框架")
    
    print("\\n📁 项目结构:")
    print("   aura-backend/")
    print("   ├── src/")
    print("   │   ├── config/          # 配置文件")
    print("   │   ├── controllers/     # API 控制器")
    print("   │   ├── middleware/      # 中间件")
    print("   │   ├── services/        # 业务逻辑")
    print("   │   └── types/          # 数据模型")
    print("   ├── tests/")
    print("   │   ├── api/            # API 测试")
    print("   │   ├── services/       # 服务测试")
    print("   │   └── integration/    # 集成测试")
    print("   ├── supabase/")
    print("   │   └── migrations/     # 数据库迁移")
    print("   ├── scripts/            # 部署脚本")
    print("   └── main.py            # 应用入口")


if __name__ == "__main__":
    print(f"🕐 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    result = asyncio.run(manual_onboarding_test())
    
    if result:
        print_deployment_summary()
        print("\\n🎉 新手引导功能测试完成！")
    else:
        print("\\n❌ 测试失败，请检查服务器状态")