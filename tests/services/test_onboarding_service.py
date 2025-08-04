"""
OnboardingService单元测试
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from uuid import uuid4
from datetime import datetime

from src.services.onboarding import OnboardingService
from src.types.database import (
    BirthInfo,
    CreateProfileRequest,
    UpdateProfileRequest,
    GenderEnum,
    OnboardingStep,
)


class TestOnboardingService:
    """OnboardingService测试类"""

    @pytest.fixture
    def service(self, mock_supabase_client):
        """创建测试用的OnboardingService实例"""
        service = OnboardingService()
        service.supabase = mock_supabase_client
        service.admin_supabase = mock_supabase_client
        return service

    @pytest.mark.asyncio
    async def test_get_avatars_success(
        self, service, mock_supabase_client, sample_avatar_data
    ):
        """测试成功获取虚拟形象列表"""
        # 设置mock响应
        mock_response = MagicMock()
        mock_response.data = [sample_avatar_data]

        mock_supabase_client.table.return_value.select.return_value.execute.return_value = mock_response

        # 执行测试
        avatars = await service.get_avatars()

        # 验证结果
        assert len(avatars) == 1
        assert avatars[0].name == "星语者·小满"
        assert avatars[0].description == "温柔而智慧的星相导师"
        assert "星座分析" in avatars[0].abilities

        # 验证调用
        mock_supabase_client.table.assert_called_with("avatars")

    @pytest.mark.asyncio
    async def test_get_avatars_empty(self, service, mock_supabase_client):
        """测试获取空的虚拟形象列表"""
        # 设置mock响应
        mock_response = MagicMock()
        mock_response.data = []

        mock_supabase_client.table.return_value.select.return_value.execute.return_value = mock_response

        # 执行测试
        avatars = await service.get_avatars()

        # 验证结果
        assert len(avatars) == 0

    @pytest.mark.asyncio
    async def test_get_user_profile_exists(
        self, service, mock_supabase_client, sample_profile_data, sample_avatar_data
    ):
        """测试获取存在的用户档案"""
        user_id = sample_profile_data["id"]

        # 设置profile响应
        profile_data = sample_profile_data.copy()
        profile_data["selected_avatar"] = sample_avatar_data

        mock_profile_response = MagicMock()
        mock_profile_response.data = [profile_data]

        # 设置analysis响应（无分析结果）
        mock_analysis_response = MagicMock()
        mock_analysis_response.data = []

        mock_table = mock_supabase_client.table.return_value
        mock_table.select.return_value.eq.return_value.execute.side_effect = [
            mock_profile_response,  # get_user_profile调用
            mock_analysis_response,  # get_user_analysis调用
        ]

        # 执行测试
        profile = await service.get_user_profile(user_id)

        # 验证结果
        assert profile is not None
        assert profile.nickname == "测试用户"
        assert profile.gender == GenderEnum.FEMALE
        assert profile.birth_year == 1995
        assert profile.selected_avatar.name == "星语者·小满"
        assert profile.analysis_completed is False

    @pytest.mark.asyncio
    async def test_get_user_profile_not_exists(self, service, mock_supabase_client):
        """测试获取不存在的用户档案"""
        user_id = str(uuid4())

        # 设置mock响应
        mock_response = MagicMock()
        mock_response.data = []

        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response

        # 执行测试
        profile = await service.get_user_profile(user_id)

        # 验证结果
        assert profile is None

    @pytest.mark.asyncio
    async def test_create_or_update_profile_success(
        self,
        service,
        mock_supabase_client,
        sample_user_id,
        sample_avatar_id,
        mock_httpx_client,
    ):
        """测试成功创建或更新用户档案"""
        # 创建请求数据
        birth_info = BirthInfo(
            year=1995, month=8, day=15, hour=14, minute=30, location="北京市"
        )

        request = CreateProfileRequest(
            nickname="测试用户",
            gender=GenderEnum.FEMALE,
            birth_info=birth_info,
            selected_avatar_id=uuid4(),
        )

        # 设置upsert响应
        profile_data = {
            "id": sample_user_id,
            "nickname": "测试用户",
            "gender": "female",
            "birth_year": 1995,
            "birth_month": 8,
            "birth_day": 15,
            "birth_hour": 14,
            "birth_minute": 30,
            "birth_second": None,
            "birth_location": "北京市",
            "birth_longitude": None,
            "birth_latitude": None,
            "selected_avatar_id": str(request.selected_avatar_id),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        mock_upsert_response = MagicMock()
        mock_upsert_response.data = [profile_data]

        # 设置获取profile响应（用于返回结果）
        mock_get_response = MagicMock()
        mock_get_response.data = [profile_data]

        # 设置analysis响应
        mock_analysis_response = MagicMock()
        mock_analysis_response.data = []

        mock_table = mock_supabase_client.table.return_value
        mock_table.upsert.return_value.execute.return_value = mock_upsert_response
        mock_table.select.return_value.eq.return_value.execute.side_effect = [
            mock_get_response,  # get_user_profile调用
            mock_analysis_response,  # get_user_analysis调用
        ]

        # Mock算法服务调用
        with patch("asyncio.create_task"):
            # 执行测试
            profile = await service.create_or_update_profile(sample_user_id, request)

        # 验证结果
        assert profile is not None
        assert profile.nickname == "测试用户"
        assert profile.gender == GenderEnum.FEMALE
        assert profile.birth_year == 1995

        # 验证upsert调用
        mock_supabase_client.table.assert_called_with("profiles")

    @pytest.mark.asyncio
    async def test_update_profile_success(
        self, service, mock_supabase_client, sample_user_id
    ):
        """测试成功更新用户档案"""
        # 创建更新请求
        update_request = UpdateProfileRequest(nickname="新昵称", gender=GenderEnum.MALE)

        # 设置update响应
        updated_data = {
            "id": sample_user_id,
            "nickname": "新昵称",
            "gender": "male",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        mock_update_response = MagicMock()
        mock_update_response.data = [updated_data]

        # 设置获取profile响应
        mock_get_response = MagicMock()
        mock_get_response.data = [updated_data]

        # 设置analysis响应
        mock_analysis_response = MagicMock()
        mock_analysis_response.data = []

        mock_table = mock_supabase_client.table.return_value
        mock_table.update.return_value.eq.return_value.execute.return_value = (
            mock_update_response
        )
        mock_table.select.return_value.eq.return_value.execute.side_effect = [
            mock_get_response,  # get_user_profile调用
            mock_analysis_response,  # get_user_analysis调用
        ]

        # 执行测试
        profile = await service.update_profile(sample_user_id, update_request)

        # 验证结果
        assert profile is not None
        assert profile.nickname == "新昵称"
        assert profile.gender == GenderEnum.MALE

    @pytest.mark.asyncio
    async def test_get_user_analysis_exists(
        self, service, mock_supabase_client, sample_user_id
    ):
        """测试获取存在的用户分析结果"""
        # 设置分析数据
        analysis_data = {
            "id": str(uuid4()),
            "user_id": sample_user_id,
            "analysis_data": {
                "birth_chart_traditional": {
                    "summary": "根据八字分析，您具备很好的创造力"
                }
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        mock_response = MagicMock()
        mock_response.data = [analysis_data]

        mock_table = mock_supabase_client.table.return_value
        mock_table.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = mock_response

        # 执行测试
        analysis = await service.get_user_analysis(sample_user_id)

        # 验证结果
        assert analysis is not None
        assert str(analysis.user_id) == sample_user_id
        assert "birth_chart_traditional" in analysis.analysis_data

    @pytest.mark.asyncio
    async def test_get_user_analysis_not_exists(
        self, service, mock_supabase_client, sample_user_id
    ):
        """测试获取不存在的用户分析结果"""
        mock_response = MagicMock()
        mock_response.data = []

        mock_table = mock_supabase_client.table.return_value
        mock_table.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = mock_response

        # 执行测试
        analysis = await service.get_user_analysis(sample_user_id)

        # 验证结果
        assert analysis is None

    @pytest.mark.asyncio
    async def test_get_onboarding_status_new_user(self, service, mock_supabase_client):
        """测试新用户的引导状态"""
        user_id = str(uuid4())

        # 设置无profile和无avatar响应
        mock_empty_response = MagicMock()
        mock_empty_response.data = []

        mock_table = mock_supabase_client.table.return_value
        mock_table.select.return_value.eq.return_value.execute.return_value = (
            mock_empty_response
        )
        mock_table.select.return_value.execute.return_value = mock_empty_response

        # 执行测试
        status = await service.get_onboarding_status(user_id)

        # 验证结果
        assert status.current_step == OnboardingStep.BASIC_INFO
        assert len(status.completed_steps) == 0
        assert status.profile is None
        assert len(status.available_avatars) == 0

    @pytest.mark.asyncio
    async def test_get_onboarding_status_completed_user(
        self, service, mock_supabase_client, sample_profile_data, sample_avatar_data
    ):
        """测试已完成引导的用户状态"""
        user_id = sample_profile_data["id"]

        # 设置完整的profile数据
        profile_data = sample_profile_data.copy()
        profile_data["selected_avatar"] = sample_avatar_data

        mock_profile_response = MagicMock()
        mock_profile_response.data = [profile_data]

        # 设置avatar列表响应
        mock_avatar_response = MagicMock()
        mock_avatar_response.data = [sample_avatar_data]

        # 设置analysis响应（有分析结果）
        analysis_data = {
            "id": str(uuid4()),
            "user_id": user_id,
            "analysis_data": {"test": "data"},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        mock_analysis_response = MagicMock()
        mock_analysis_response.data = [analysis_data]

        # 针对不同表的查询设置不同的mock响应
        def mock_table_side_effect(table_name):
            mock_result = MagicMock()
            mock_result.select.return_value = mock_result
            mock_result.eq.return_value = mock_result

            if table_name == "avatars":
                mock_result.execute.return_value = mock_avatar_response
            elif table_name == "profiles":
                mock_result.execute.return_value = mock_profile_response
            elif table_name == "user_profile_analysis":
                mock_result.execute.return_value = mock_analysis_response

            return mock_result

        mock_supabase_client.table.side_effect = mock_table_side_effect

        # 执行测试
        status = await service.get_onboarding_status(user_id)

        # 验证结果
        assert status.current_step == OnboardingStep.COMPLETED
        assert OnboardingStep.BASIC_INFO in status.completed_steps
        assert OnboardingStep.BIRTH_INFO in status.completed_steps
        assert OnboardingStep.AVATAR_SELECTION in status.completed_steps
        assert OnboardingStep.ANALYSIS_PROCESSING in status.completed_steps
        assert OnboardingStep.FIRST_CHAT in status.completed_steps
        assert status.profile is not None
        assert len(status.available_avatars) == 1

    @pytest.mark.asyncio
    async def test_trigger_profile_analysis_success(
        self,
        service,
        mock_httpx_client,
        sample_user_id,
        sample_birth_info,
        mock_algorithm_response,
    ):
        """测试触发用户画像分析成功"""
        birth_info = BirthInfo(**sample_birth_info)

        # 设置算法服务响应
        mock_httpx_client.post.return_value.status_code = 200
        mock_httpx_client.post.return_value.json.return_value = mock_algorithm_response

        # 设置存储响应
        mock_store_response = MagicMock()
        mock_store_response.data = [{"id": str(uuid4())}]

        with patch.object(
            service, "_store_analysis_result", return_value=None
        ) as mock_store:
            # 执行测试
            await service._trigger_profile_analysis(sample_user_id, birth_info)

        # 验证算法服务调用
        mock_httpx_client.post.assert_called_once()
        call_args = mock_httpx_client.post.call_args
        assert "/api/algorithm/user-profile-analysis" in call_args[1]["json"]

        # 验证存储调用
        mock_store.assert_called_once()

    @pytest.mark.asyncio
    async def test_trigger_profile_analysis_algorithm_error(
        self, service, mock_httpx_client, sample_user_id, sample_birth_info
    ):
        """测试算法服务错误时的处理"""
        birth_info = BirthInfo(**sample_birth_info)

        # 设置算法服务错误响应
        mock_httpx_client.post.return_value.status_code = 500
        mock_httpx_client.post.return_value.text = "Internal Server Error"

        # 执行测试（不应该抛出异常）
        await service._trigger_profile_analysis(sample_user_id, birth_info)

        # 验证调用
        mock_httpx_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_store_analysis_result_success(
        self, service, mock_supabase_client, sample_user_id
    ):
        """测试成功存储分析结果"""
        analysis_data = {"test": "data", "summary": "Test analysis"}

        # 设置插入响应
        mock_response = MagicMock()
        mock_response.data = [{"id": str(uuid4())}]

        mock_supabase_client.table.return_value.insert.return_value.execute.return_value = mock_response

        # 执行测试
        await service._store_analysis_result(sample_user_id, analysis_data)

        # 验证调用
        mock_supabase_client.table.assert_called_with("user_profiles_analysis")

    @pytest.mark.asyncio
    async def test_store_analysis_result_failure(
        self, service, mock_supabase_client, sample_user_id
    ):
        """测试存储分析结果失败"""
        analysis_data = {"test": "data"}

        # 设置插入失败响应
        mock_response = MagicMock()
        mock_response.data = []

        mock_supabase_client.table.return_value.insert.return_value.execute.return_value = mock_response

        # 执行测试，应该抛出异常
        with pytest.raises(Exception, match="Failed to store analysis result"):
            await service._store_analysis_result(sample_user_id, analysis_data)
