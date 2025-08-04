"""
CompatibilityService单元测试
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from uuid import uuid4
from datetime import datetime

from src.services.compatibility import CompatibilityService
from src.types.database import (
    CreateOtherProfileRequest,
    CompatibilityRequest,
    BirthInfo,
    GenderEnum,
)


class TestCompatibilityService:
    """CompatibilityService测试类"""

    @pytest.fixture
    def service(self, mock_supabase_client):
        """创建测试用的CompatibilityService实例"""
        service = CompatibilityService()
        service.supabase = mock_supabase_client
        service.admin_supabase = mock_supabase_client
        return service

    @pytest.mark.asyncio
    async def test_create_other_profile_success(
        self, service, mock_supabase_client, sample_user_id
    ):
        """测试成功创建他人档案"""
        request = CreateOtherProfileRequest(
            name="测试对象",
            birth_info=BirthInfo(
                year=1995, month=6, day=15, hour=14, minute=30, location="北京市"
            ),
            relation_type="朋友",
            gender=GenderEnum.FEMALE,
        )

        # 设置档案存储响应
        profile_data = {
            "id": str(uuid4()),
            "user_id": sample_user_id,
            "name": "测试对象",
            "birth_year": 1995,
            "birth_month": 6,
            "birth_day": 15,
            "birth_hour": 14,
            "birth_minute": 30,
            "birth_second": None,
            "birth_location": "北京市",
            "birth_longitude": None,
            "birth_latitude": None,
            "relation_type": "朋友",
            "gender": "female",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        mock_response = MagicMock()
        mock_response.data = [profile_data]

        mock_table = mock_supabase_client.table.return_value
        mock_table.insert.return_value.execute.return_value = mock_response

        # 执行测试
        response = await service.create_other_profile(sample_user_id, request)

        # 验证结果
        assert str(response.id) == profile_data["id"]
        assert response.name == "测试对象"
        assert response.relation_type == "朋友"
        assert response.gender == GenderEnum.FEMALE

    @pytest.mark.asyncio
    async def test_create_other_profile_db_error(
        self, service, mock_supabase_client, sample_user_id
    ):
        """测试创建他人档案时数据库错误"""
        request = CreateOtherProfileRequest(
            name="测试对象",
            birth_info=BirthInfo(
                year=1995, month=6, day=15, hour=14, minute=30, location="北京市"
            ),
            relation_type="朋友",
            gender=GenderEnum.FEMALE,
        )

        # 设置数据库错误响应
        mock_table = mock_supabase_client.table.return_value
        mock_table.insert.return_value.execute.side_effect = Exception("Database error")

        # 执行测试，预期抛出异常
        with pytest.raises(Exception, match="Database error"):
            await service.create_other_profile(sample_user_id, request)

    @pytest.mark.asyncio
    async def test_analyze_compatibility_success(
        self, service, mock_supabase_client, mock_httpx_client, sample_user_id
    ):
        """测试成功分析配对度"""
        request = CompatibilityRequest(
            other_profile_id=str(uuid4()), analysis_type="natal_chart"
        )

        # 设置用户profile响应
        user_profile_data = {
            "id": sample_user_id,
            "nickname": "用户A",
            "birth_info": {
                "birth_year": 1990,
                "birth_month": 3,
                "birth_day": 15,
                "birth_hour": 10,
                "birth_minute": 0,
            },
            "location": "上海",
            "gender": "male",
        }

        # 设置他人profile响应
        other_profile_data = {
            "id": str(request.other_profile_id),
            "name": "测试对象",
            "birth_info": {
                "birth_year": 1995,
                "birth_month": 6,
                "birth_day": 15,
                "birth_hour": 14,
                "birth_minute": 30,
            },
            "location": "北京",
            "relationship": "朋友",
            "gender": "female",
        }

        # 设置算法服务响应
        algorithm_response = {
            "compatibility_result": {
                "overall_score": 85,
                "detailed_analysis": {
                    "personality_match": {"score": 90, "explanation": "性格互补性很好"},
                    "life_goal_alignment": {
                        "score": 80,
                        "explanation": "人生目标相对一致",
                    },
                    "communication_style": {"score": 85, "explanation": "沟通风格匹配"},
                },
                "strengths": ["互补性强", "价值观相近"],
                "challenges": ["需要更多沟通"],
                "recommendations": ["多参与共同活动", "保持开放心态"],
                "summary": "你们的配对度很高，建议进一步发展关系。",
            }
        }
        mock_httpx_client.post.return_value.status_code = 200
        mock_httpx_client.post.return_value.json.return_value = algorithm_response

        # 设置配对分析存储响应
        analysis_data = {
            "id": str(uuid4()),
            "user_id": sample_user_id,
            "other_profile_id": str(request.other_profile_id),
            "analysis_type": "natal_chart",
            "compatibility_score": 85,
            "analysis_details": algorithm_response["compatibility_result"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        # 设置活跃session响应
        session_data = {
            "id": str(uuid4()),
            "user_id": sample_user_id,
            "is_active": True,
        }

        # 设置消息存储响应
        message_data = {
            "id": str(uuid4()),
            "session_id": session_data["id"],
            "sender_type": "ai",
            "content": "配对分析已完成",
            "timestamp": datetime.now().isoformat(),
            "message_type": "compatibility_result",
            "related_data": algorithm_response["compatibility_result"],
        }

        mock_table = mock_supabase_client.table.return_value

        # 模拟链式调用的顺序
        user_profile_response = MagicMock()
        user_profile_response.data = [user_profile_data]

        other_profile_response = MagicMock()
        other_profile_response.data = [other_profile_data]

        analysis_response = MagicMock()
        analysis_response.data = [analysis_data]

        session_response = MagicMock()
        session_response.data = [session_data]

        message_response = MagicMock()
        message_response.data = [message_data]

        # 设置多次调用的返回值
        mock_table.select.return_value.eq.return_value.execute.side_effect = [
            user_profile_response,  # 获取用户profile
            other_profile_response,  # 获取他人profile
        ]
        mock_table.insert.return_value.execute.side_effect = [
            analysis_response,  # 插入配对分析
        ]
        mock_table.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = session_response
        mock_table.insert.return_value.execute.return_value = message_response

        # 执行测试
        response = await service.analyze_compatibility(sample_user_id, request)

        # 验证结果
        assert response.analysis.id == analysis_data["id"]
        assert response.analysis.compatibility_score == 85
        assert response.analysis.analysis_details["overall_score"] == 85
        assert (
            "personality_match"
            in response.analysis.analysis_details["detailed_analysis"]
        )
        assert response.related_message is not None
        assert response.message == "配对分析完成"

        # 验证算法服务调用
        mock_httpx_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_compatibility_user_not_found(
        self, service, mock_supabase_client, sample_user_id
    ):
        """测试用户profile不存在时的配对分析"""
        request = CompatibilityRequest(
            other_profile_id=str(uuid4()), analysis_type="natal_chart"
        )

        # 设置用户profile不存在
        mock_response = MagicMock()
        mock_response.data = []

        mock_table = mock_supabase_client.table.return_value
        mock_table.select.return_value.eq.return_value.execute.return_value = (
            mock_response
        )

        # 执行测试，预期抛出异常
        with pytest.raises(Exception, match="User profile not found"):
            await service.analyze_compatibility(sample_user_id, request)

    @pytest.mark.asyncio
    async def test_analyze_compatibility_other_profile_not_found(
        self, service, mock_supabase_client, sample_user_id
    ):
        """测试他人profile不存在时的配对分析"""
        request = CompatibilityRequest(
            other_profile_id=str(uuid4()), analysis_type="natal_chart"
        )

        # 设置用户profile存在，他人profile不存在
        user_profile_response = MagicMock()
        user_profile_response.data = [{"id": sample_user_id}]

        other_profile_response = MagicMock()
        other_profile_response.data = []

        mock_table = mock_supabase_client.table.return_value
        mock_table.select.return_value.eq.return_value.execute.side_effect = [
            user_profile_response,
            other_profile_response,
        ]

        # 执行测试，预期抛出异常
        with pytest.raises(Exception, match="Other profile not found"):
            await service.analyze_compatibility(sample_user_id, request)

    @pytest.mark.asyncio
    async def test_analyze_compatibility_algorithm_fallback(
        self, service, mock_supabase_client, mock_httpx_client, sample_user_id
    ):
        """测试算法服务失败时的fallback"""
        request = CompatibilityRequest(
            other_profile_id=str(uuid4()), analysis_type="natal_chart"
        )

        # 设置profile响应
        user_profile_response = MagicMock()
        user_profile_response.data = [{"id": sample_user_id, "nickname": "用户A"}]

        other_profile_response = MagicMock()
        other_profile_response.data = [
            {"id": str(request.other_profile_id), "name": "测试对象"}
        ]

        # 设置算法服务失败
        mock_httpx_client.post.return_value.status_code = 500

        # 设置配对分析存储响应（fallback结果）
        analysis_data = {
            "id": str(uuid4()),
            "user_id": sample_user_id,
            "other_profile_id": str(request.other_profile_id),
            "analysis_type": "natal_chart",
            "compatibility_score": 70,
            "analysis_details": {
                "overall_score": 70,
                "summary": "暂时无法获取详细分析，建议稍后重试。",
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        analysis_response = MagicMock()
        analysis_response.data = [analysis_data]

        # 设置无活跃session
        session_response = MagicMock()
        session_response.data = []

        mock_table = mock_supabase_client.table.return_value
        mock_table.select.return_value.eq.return_value.execute.side_effect = [
            user_profile_response,
            other_profile_response,
        ]
        mock_table.insert.return_value.execute.return_value = analysis_response
        mock_table.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = session_response

        # 执行测试
        response = await service.analyze_compatibility(sample_user_id, request)

        # 验证fallback结果
        assert response.analysis.compatibility_score == 70
        assert "暂时无法获取详细分析" in response.analysis.analysis_details["summary"]
        assert response.related_message is None  # 无活跃session

    @pytest.mark.asyncio
    async def test_get_compatibility_history_success(
        self, service, mock_supabase_client, sample_user_id, sample_compatibility_data
    ):
        """测试成功获取配对历史"""
        # 设置历史数据
        history_data = [
            sample_compatibility_data,
            {
                **sample_compatibility_data,
                "id": str(uuid4()),
                "other_profile_id": str(uuid4()),
            },
        ]

        mock_response = MagicMock()
        mock_response.data = history_data

        mock_table = mock_supabase_client.table.return_value
        mock_table.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = mock_response

        # 执行测试
        history = await service.get_compatibility_history(sample_user_id, limit=10)

        # 验证结果
        assert len(history) == 2
        assert all(str(analysis.user_id) == sample_user_id for analysis in history)

    @pytest.mark.asyncio
    async def test_get_compatibility_history_empty(
        self, service, mock_supabase_client, sample_user_id
    ):
        """测试获取空的配对历史"""
        mock_response = MagicMock()
        mock_response.data = []

        mock_table = mock_supabase_client.table.return_value
        mock_table.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = mock_response

        # 执行测试
        history = await service.get_compatibility_history(sample_user_id, limit=10)

        # 验证结果
        assert len(history) == 0

    @pytest.mark.asyncio
    async def test_call_compatibility_algorithm_success(
        self, service, mock_httpx_client, sample_user_id
    ):
        """测试成功调用配对算法"""
        user_profile = {"id": sample_user_id, "nickname": "用户A"}
        other_profile = {"id": str(uuid4()), "name": "测试对象"}
        analysis_type = "natal_chart"

        # 设置算法服务响应
        algorithm_response = {
            "compatibility_result": {"overall_score": 85, "summary": "配对度很高"}
        }
        mock_httpx_client.post.return_value.status_code = 200
        mock_httpx_client.post.return_value.json.return_value = algorithm_response

        # 执行测试
        result = await service._call_compatibility_algorithm(
            user_profile, other_profile, analysis_type
        )

        # 验证结果
        assert result["overall_score"] == 85
        assert result["summary"] == "配对度很高"

        # 验证API调用
        mock_httpx_client.post.assert_called_once()
        call_args = mock_httpx_client.post.call_args
        payload = call_args[1]["json"]
        assert payload["user_profile"]["id"] == sample_user_id
        assert payload["other_profile"]["id"] == other_profile["id"]
        assert payload["analysis_type"] == analysis_type

    @pytest.mark.asyncio
    async def test_call_compatibility_algorithm_fallback(
        self, service, mock_httpx_client
    ):
        """测试算法服务失败时的fallback"""
        user_profile = {"id": str(uuid4())}
        other_profile = {"id": str(uuid4())}
        analysis_type = "natal_chart"

        # 设置算法服务失败
        mock_httpx_client.post.return_value.status_code = 500

        # 执行测试
        result = await service._call_compatibility_algorithm(
            user_profile, other_profile, analysis_type
        )

        # 验证fallback结果
        assert result["overall_score"] == 70
        assert "暂时无法获取详细分析" in result["summary"]

    @pytest.mark.asyncio
    async def test_create_compatibility_message_success(
        self, service, mock_supabase_client, sample_user_id
    ):
        """测试成功创建配对消息"""
        compatibility_result = {"overall_score": 85, "summary": "你们的配对度很高"}

        # 设置活跃session响应
        session_id = str(uuid4())
        mock_session_response = MagicMock()
        mock_session_response.data = [
            {"id": session_id, "user_id": sample_user_id, "is_active": True}
        ]

        # 设置消息存储响应
        message_data = {
            "id": str(uuid4()),
            "session_id": session_id,
            "sender_type": "ai",
            "content": "配对分析已完成",
            "timestamp": datetime.now().isoformat(),
            "message_type": "compatibility_result",
            "related_data": compatibility_result,
        }

        mock_message_response = MagicMock()
        mock_message_response.data = [message_data]

        mock_table = mock_supabase_client.table.return_value
        mock_table.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = mock_session_response
        mock_table.insert.return_value.execute.return_value = mock_message_response

        # 执行测试
        result = await service._create_compatibility_message(
            sample_user_id, compatibility_result, "测试对象"
        )

        # 验证结果
        assert result is not None
        assert result["content"] == "配对分析已完成"
        assert result["message_type"] == "compatibility_result"

    @pytest.mark.asyncio
    async def test_create_compatibility_message_no_active_session(
        self, service, mock_supabase_client, sample_user_id
    ):
        """测试无活跃session时创建配对消息"""
        compatibility_result = {"overall_score": 85}

        # 设置无活跃session响应
        mock_session_response = MagicMock()
        mock_session_response.data = []

        mock_table = mock_supabase_client.table.return_value
        mock_table.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = mock_session_response

        # 执行测试
        result = await service._create_compatibility_message(
            sample_user_id, compatibility_result, "测试对象"
        )

        # 验证结果
        assert result is None
