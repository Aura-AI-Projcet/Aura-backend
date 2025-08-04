"""
FortuneService单元测试
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from uuid import uuid4
from datetime import date, datetime

from src.services.fortune import FortuneService
from src.types.database import (
    FortuneRequest,
    MessageType,
    SenderType,
)


class TestFortuneService:
    """FortuneService测试类"""

    @pytest.fixture
    def service(self, mock_supabase_client):
        """创建测试用的FortuneService实例"""
        service = FortuneService()
        service.supabase = mock_supabase_client
        service.admin_supabase = mock_supabase_client
        return service

    @pytest.mark.asyncio
    async def test_get_daily_fortune_new_user(
        self, service, mock_supabase_client, mock_httpx_client, sample_user_id
    ):
        """测试新用户获取每日运势"""
        target_date = date.today().isoformat()

        # 设置无现有运势响应
        mock_existing_response = MagicMock()
        mock_existing_response.data = []

        # 设置用户profile响应
        mock_profile_response = MagicMock()
        mock_profile_response.data = [{"id": sample_user_id, "nickname": "测试用户"}]

        # 设置算法服务响应
        algorithm_response = {
            "fortune_details": {
                "luck_level": "吉",
                "suitability": ["宜出行", "宜社交"],
                "lucky_color": "红色",
                "lucky_number": 8,
                "general_summary": "今日运势很好，适合新的开始。",
            }
        }
        mock_httpx_client.post.return_value.status_code = 200
        mock_httpx_client.post.return_value.json.return_value = algorithm_response

        # 设置运势存储响应
        fortune_data = {
            "id": str(uuid4()),
            "user_id": sample_user_id,
            "fortune_date": target_date,
            "fortune_data": algorithm_response["fortune_details"],
            "generated_at": datetime.now().isoformat(),
            "is_pushed": False,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        mock_insert_response = MagicMock()
        mock_insert_response.data = [fortune_data]

        # 设置链式调用
        mock_table = mock_supabase_client.table.return_value

        # 第一次调用：检查现有运势
        mock_table.select.return_value.eq.return_value.execute.return_value = (
            mock_existing_response
        )

        # 第二次调用：获取用户profile
        mock_table.select.return_value.eq.return_value.execute.return_value = (
            mock_profile_response
        )

        # 第三次调用：插入新运势
        mock_table.insert.return_value.execute.return_value = mock_insert_response

        # 执行测试
        response = await service.get_daily_fortune(sample_user_id, target_date)

        # 验证结果
        assert str(response.fortune.user_id) == sample_user_id
        assert response.fortune.fortune_date.strftime("%Y-%m-%d") == target_date
        assert response.fortune.fortune_data["luck_level"] == "吉"
        assert response.fortune.fortune_data["lucky_color"] == "红色"
        assert response.fortune.fortune_data["lucky_number"] == 8
        assert response.can_generate_new is True

        # 验证API调用
        mock_httpx_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_daily_fortune_existing(
        self, service, mock_supabase_client, sample_user_id, sample_daily_fortune_data
    ):
        """测试获取已存在的每日运势"""
        target_date = date.today().isoformat()

        # 设置现有运势响应
        mock_existing_response = MagicMock()
        mock_existing_response.data = [sample_daily_fortune_data]

        mock_table = mock_supabase_client.table.return_value
        mock_table.select.return_value.eq.return_value.execute.return_value = (
            mock_existing_response
        )

        # 执行测试
        response = await service.get_daily_fortune(sample_user_id, target_date)

        # 验证结果
        assert str(response.fortune.id) == sample_daily_fortune_data["id"]
        assert response.fortune.fortune_data["luck_level"] == "吉"
        assert response.can_generate_new is False

    @pytest.mark.asyncio
    async def test_get_daily_fortune_default_date(
        self, service, mock_supabase_client, sample_user_id
    ):
        """测试使用默认日期获取运势"""
        # 设置无现有运势响应
        mock_existing_response = MagicMock()
        mock_existing_response.data = []

        # 设置用户profile响应
        mock_profile_response = MagicMock()
        mock_profile_response.data = [{"id": sample_user_id}]

        # 设置fallback运势存储响应
        fortune_data = {
            "id": str(uuid4()),
            "user_id": sample_user_id,
            "fortune_date": date.today().isoformat(),
            "fortune_data": {
                "luck_level": "平",
                "suitability": ["宜保持心情愉悦"],
                "lucky_color": "蓝色",
                "lucky_number": 7,
                "general_summary": "今日运势平稳。",
            },
            "generated_at": datetime.now().isoformat(),
            "is_pushed": False,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        mock_insert_response = MagicMock()
        mock_insert_response.data = [fortune_data]

        # 针对不同表的查询设置不同的mock响应
        def mock_table_side_effect(table_name):
            mock_result = MagicMock()
            mock_result.select.return_value = mock_result
            mock_result.eq.return_value = mock_result
            mock_result.insert.return_value = mock_result

            if table_name == "daily_fortunes":
                mock_result.execute.return_value = mock_existing_response
            elif table_name == "profiles":
                mock_result.execute.return_value = mock_profile_response

            # 对于insert操作
            mock_result.execute.return_value = mock_insert_response
            return mock_result

        mock_supabase_client.table.side_effect = mock_table_side_effect

        # Mock算法服务失败，使用fallback
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.return_value.status_code = 500

            # 执行测试（不传入target_date）
            response = await service.get_daily_fortune(sample_user_id)

        # 验证使用今日日期
        assert response.fortune.fortune_date == date.today().isoformat()

    @pytest.mark.asyncio
    async def test_predict_fortune_tarot(
        self, service, mock_supabase_client, mock_httpx_client, sample_user_id
    ):
        """测试塔罗牌预测"""
        request = FortuneRequest(request_type="tarot", question="我的爱情运势如何？")

        # 设置用户profile响应
        mock_profile_response = MagicMock()
        mock_profile_response.data = [{"id": sample_user_id, "nickname": "测试用户"}]

        # 设置算法服务响应
        algorithm_response = {
            "fortune_result": {
                "type": "tarot_reading",
                "summary": "爱情运势很好",
                "details": {
                    "tarot_cards": [
                        {
                            "name": "太阳",
                            "meaning": "光明与希望",
                            "is_reversed": False,
                            "position_meaning": "现在",
                        }
                    ],
                    "explanation": "塔罗牌显示你的爱情运势非常积极",
                    "actionable_advice": ["保持开放的心态", "主动出击"],
                },
            }
        }
        mock_httpx_client.post.return_value.status_code = 200
        mock_httpx_client.post.return_value.json.return_value = algorithm_response

        # 设置活跃session响应
        mock_session_response = MagicMock()
        mock_session_response.data = [
            {"id": str(uuid4()), "user_id": sample_user_id, "is_active": True}
        ]

        # 设置消息存储响应
        mock_message_response = MagicMock()
        mock_message_response.data = [
            {
                "id": str(uuid4()),
                "session_id": mock_session_response.data[0]["id"],
                "sender_type": "ai",
                "content": "爱情运势很好",
                "timestamp": datetime.now().isoformat(),
                "message_type": "tarot_result",
                "related_data": algorithm_response["fortune_result"],
            }
        ]

        mock_table = mock_supabase_client.table.return_value
        mock_table.select.return_value.eq.return_value.execute.side_effect = [
            mock_profile_response,  # 获取用户profile
            mock_session_response,  # 获取活跃session
        ]
        mock_table.insert.return_value.execute.return_value = mock_message_response

        # 执行测试
        response = await service.predict_fortune(sample_user_id, request)

        # 验证结果
        assert response.fortune_result["type"] == "tarot_reading"
        assert response.fortune_result["summary"] == "爱情运势很好"
        assert "tarot_cards" in response.fortune_result["details"]
        assert response.related_message is not None

    @pytest.mark.asyncio
    async def test_predict_fortune_divination(
        self, service, mock_supabase_client, mock_httpx_client, sample_user_id
    ):
        """测试抽签卜卦"""
        request = FortuneRequest(
            request_type="divination", divination_type="求签", question="事业发展如何？"
        )

        # 设置用户profile响应
        mock_profile_response = MagicMock()
        mock_profile_response.data = [{"id": sample_user_id}]

        # 设置算法服务响应
        algorithm_response = {
            "fortune_result": {
                "type": "divination_result",
                "summary": "上上签，事业有成",
                "details": {
                    "divination_output": "事业有成，前程似锦",
                    "explanation": "此签暗示你的事业发展将会很顺利",
                    "judgment": "吉",
                    "actionable_advice": ["把握机会", "勇敢前进"],
                },
            }
        }
        mock_httpx_client.post.return_value.status_code = 200
        mock_httpx_client.post.return_value.json.return_value = algorithm_response

        # 设置无活跃session响应
        mock_session_response = MagicMock()
        mock_session_response.data = []

        mock_table = mock_supabase_client.table.return_value
        mock_table.select.return_value.eq.return_value.execute.side_effect = [
            mock_profile_response,  # 获取用户profile
            mock_session_response,  # 获取活跃session（无）
        ]

        # 执行测试
        response = await service.predict_fortune(sample_user_id, request)

        # 验证结果
        assert response.fortune_result["type"] == "divination_result"
        assert response.fortune_result["summary"] == "上上签，事业有成"
        assert response.related_message is None  # 无活跃session

    @pytest.mark.asyncio
    async def test_predict_fortune_daily(
        self, service, mock_supabase_client, mock_httpx_client, sample_user_id
    ):
        """测试每日运势预测"""
        request = FortuneRequest(request_type="daily_fortune", date="2024-01-15")

        # 设置用户profile响应
        mock_profile_response = MagicMock()
        mock_profile_response.data = [{"id": sample_user_id}]

        # 设置算法服务响应
        algorithm_response = {
            "fortune_result": {
                "type": "daily_fortune",
                "summary": "今日运势不错",
                "details": {
                    "luck_level": "吉",
                    "suitability": ["宜出行", "宜谈判"],
                    "lucky_color": "绿色",
                    "lucky_number": 6,
                },
            }
        }
        mock_httpx_client.post.return_value.status_code = 200
        mock_httpx_client.post.return_value.json.return_value = algorithm_response

        mock_table = mock_supabase_client.table.return_value
        mock_table.select.return_value.eq.return_value.execute.return_value = (
            mock_profile_response
        )

        # 执行测试
        response = await service.predict_fortune(sample_user_id, request)

        # 验证结果
        assert response.fortune_result["type"] == "daily_fortune"
        assert response.fortune_result["details"]["luck_level"] == "吉"

    @pytest.mark.asyncio
    async def test_get_fortune_history_success(
        self, service, mock_supabase_client, sample_user_id, sample_daily_fortune_data
    ):
        """测试成功获取运势历史"""
        # 设置历史数据
        history_data = [
            sample_daily_fortune_data,
            {
                **sample_daily_fortune_data,
                "id": str(uuid4()),
                "fortune_date": "2024-01-14",
            },
        ]

        mock_response = MagicMock()
        mock_response.data = history_data

        mock_table = mock_supabase_client.table.return_value
        mock_table.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = mock_response

        # 执行测试
        history = await service.get_fortune_history(sample_user_id, limit=10)

        # 验证结果
        assert len(history) == 2
        assert all(str(fortune.user_id) == sample_user_id for fortune in history)

    @pytest.mark.asyncio
    async def test_generate_daily_fortune_success(
        self, service, mock_supabase_client, mock_httpx_client, sample_user_id
    ):
        """测试成功生成每日运势"""
        fortune_date = "2024-01-15"

        # 设置用户profile响应
        mock_profile_response = MagicMock()
        mock_profile_response.data = [{"id": sample_user_id, "nickname": "测试用户"}]

        # 设置算法服务响应
        algorithm_response = {
            "fortune_details": {
                "luck_level": "吉",
                "suitability": ["宜出行"],
                "lucky_color": "红色",
                "lucky_number": 8,
                "general_summary": "今日运势不错",
            }
        }
        mock_httpx_client.post.return_value.status_code = 200
        mock_httpx_client.post.return_value.json.return_value = algorithm_response

        mock_table = mock_supabase_client.table.return_value
        mock_table.select.return_value.eq.return_value.execute.return_value = (
            mock_profile_response
        )

        # 执行测试
        result = await service._generate_daily_fortune(sample_user_id, fortune_date)

        # 验证结果
        assert result["luck_level"] == "吉"
        assert result["lucky_color"] == "红色"
        assert result["lucky_number"] == 8

    @pytest.mark.asyncio
    async def test_generate_daily_fortune_fallback(
        self, service, mock_supabase_client, mock_httpx_client, sample_user_id
    ):
        """测试算法服务失败时的fallback运势"""
        fortune_date = "2024-01-15"

        # 设置用户profile响应
        mock_profile_response = MagicMock()
        mock_profile_response.data = []

        # 设置算法服务错误响应
        mock_httpx_client.post.return_value.status_code = 500

        mock_table = mock_supabase_client.table.return_value
        mock_table.select.return_value.eq.return_value.execute.return_value = (
            mock_profile_response
        )

        # 执行测试
        result = await service._generate_daily_fortune(sample_user_id, fortune_date)

        # 验证fallback结果
        assert result["luck_level"] == "平"
        assert result["lucky_color"] == "蓝色"
        assert result["lucky_number"] == 7
        assert "平稳" in result["general_summary"]

    @pytest.mark.asyncio
    async def test_call_fortune_algorithm_success(
        self, service, mock_httpx_client, sample_user_id
    ):
        """测试成功调用算法服务"""
        request = FortuneRequest(request_type="tarot", question="测试问题")
        user_profile = {"id": sample_user_id, "nickname": "测试用户"}

        # 设置算法服务响应
        algorithm_response = {
            "fortune_result": {"type": "tarot_reading", "summary": "测试结果"}
        }
        mock_httpx_client.post.return_value.status_code = 200
        mock_httpx_client.post.return_value.json.return_value = algorithm_response

        # 执行测试
        result = await service._call_fortune_algorithm(
            sample_user_id, request, user_profile
        )

        # 验证结果
        assert result["type"] == "tarot_reading"
        assert result["summary"] == "测试结果"

        # 验证API调用
        mock_httpx_client.post.assert_called_once()
        call_args = mock_httpx_client.post.call_args
        payload = call_args[1]["json"]
        assert payload["user_id"] == sample_user_id
        assert payload["request_type"] == "tarot"
        assert payload["tarot_question"] == "测试问题"

    @pytest.mark.asyncio
    async def test_call_fortune_algorithm_fallback(
        self, service, mock_httpx_client, sample_user_id
    ):
        """测试算法服务失败时的fallback"""
        request = FortuneRequest(request_type="tarot")
        user_profile = {}

        # 设置算法服务错误响应
        mock_httpx_client.post.return_value.status_code = 500

        # 执行测试
        result = await service._call_fortune_algorithm(
            sample_user_id, request, user_profile
        )

        # 验证fallback结果
        assert result["type"] == "tarot"
        assert "暂时无法获取结果" in result["summary"]

    @pytest.mark.asyncio
    async def test_create_fortune_message_success(
        self, service, mock_supabase_client, sample_user_id
    ):
        """测试成功创建运势消息"""
        fortune_result = {
            "summary": "你的塔罗牌结果已生成",
            "details": {"test": "data"},
        }
        fortune_type = "tarot"

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
            "content": "你的塔罗牌结果已生成",
            "timestamp": datetime.now().isoformat(),
            "message_type": "tarot_result",
            "related_data": fortune_result,
        }

        mock_message_response = MagicMock()
        mock_message_response.data = [message_data]

        mock_table = mock_supabase_client.table.return_value
        mock_table.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = mock_session_response
        mock_table.insert.return_value.execute.return_value = mock_message_response

        # 执行测试
        result = await service._create_fortune_message(
            sample_user_id, fortune_result, fortune_type
        )

        # 验证结果
        assert result is not None
        assert result["content"] == "你的塔罗牌结果已生成"
        assert result["message_type"] == "tarot_result"

    @pytest.mark.asyncio
    async def test_create_fortune_message_no_active_session(
        self, service, mock_supabase_client, sample_user_id
    ):
        """测试无活跃session时创建运势消息"""
        fortune_result = {"summary": "测试结果"}
        fortune_type = "divination"

        # 设置无活跃session响应
        mock_session_response = MagicMock()
        mock_session_response.data = []

        mock_table = mock_supabase_client.table.return_value
        mock_table.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = mock_session_response

        # 执行测试
        result = await service._create_fortune_message(
            sample_user_id, fortune_result, fortune_type
        )

        # 验证结果
        assert result is None
