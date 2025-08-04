"""
测试配置和通用fixtures
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, date


# Mock Supabase responses
@pytest.fixture
def mock_supabase_response():
    """创建mock的Supabase响应"""
    mock_response = MagicMock()
    mock_response.data = []
    mock_response.count = 0
    return mock_response


@pytest.fixture
def mock_supabase_client():
    """创建mock的Supabase客户端"""
    with patch("src.config.supabase.supabase_client") as mock_client:
        # 设置table方法返回的mock chain
        mock_table = MagicMock()
        mock_client.table.return_value = mock_table

        # 设置链式调用方法
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.insert.return_value = mock_table
        mock_table.update.return_value = mock_table
        mock_table.delete.return_value = mock_table
        mock_table.upsert.return_value = mock_table
        mock_table.order.return_value = mock_table
        mock_table.limit.return_value = mock_table
        mock_table.range.return_value = mock_table

        # 默认execute返回空结果
        mock_response = MagicMock()
        mock_response.data = []
        mock_response.count = 0
        mock_table.execute.return_value = mock_response

        yield mock_client


@pytest.fixture
def mock_httpx_client():
    """创建mock的httpx客户端"""
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # 默认响应
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_response.text = "Success"
        mock_client.post.return_value = mock_response
        mock_client.get.return_value = mock_response

        yield mock_client


@pytest.fixture
def sample_user_id():
    """样例用户ID"""
    return str(uuid4())


@pytest.fixture
def sample_avatar_id():
    """样例虚拟形象ID"""
    return str(uuid4())


@pytest.fixture
def sample_avatar_data():
    """样例虚拟形象数据"""
    return {
        "id": str(uuid4()),
        "name": "星语者·小满",
        "description": "温柔而智慧的星相导师",
        "image_url": "/avatars/xiaoman.png",
        "abilities": ["星座分析", "生辰八字", "人际关系", "情感咨询"],
        "initial_dialogue_prompt": "你好，我是小满，你的专属星相导师...",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }


@pytest.fixture
def sample_profile_data():
    """样例用户档案数据"""
    user_id = str(uuid4())
    return {
        "id": user_id,
        "nickname": "测试用户",
        "gender": "female",
        "birth_year": 1995,
        "birth_month": 8,
        "birth_day": 15,
        "birth_hour": 14,
        "birth_minute": 30,
        "birth_second": 0,
        "birth_location": "北京市",
        "birth_longitude": 116.4074,
        "birth_latitude": 39.9042,
        "selected_avatar_id": str(uuid4()),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }


@pytest.fixture
def sample_birth_info():
    """样例出生信息"""
    return {
        "year": 1995,
        "month": 8,
        "day": 15,
        "hour": 14,
        "minute": 30,
        "second": 0,
        "location": "北京市",
        "longitude": 116.4074,
        "latitude": 39.9042,
    }


@pytest.fixture
def sample_chat_session_data(sample_user_id):
    """样例聊天会话数据"""
    return {
        "id": str(uuid4()),
        "user_id": sample_user_id,
        "avatar_id": str(uuid4()),
        "session_start_time": datetime.now().isoformat(),
        "session_end_time": None,
        "is_active": True,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }


@pytest.fixture
def sample_chat_message_data():
    """样例聊天消息数据"""
    return {
        "id": str(uuid4()),
        "session_id": str(uuid4()),
        "sender_type": "user",
        "content": "你好，今天运势如何？",
        "timestamp": datetime.now().isoformat(),
        "message_type": "text",
        "related_data": None,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }


@pytest.fixture
def sample_daily_fortune_data(sample_user_id):
    """样例每日运势数据"""
    return {
        "id": str(uuid4()),
        "user_id": sample_user_id,
        "fortune_date": date.today().isoformat(),
        "fortune_data": {
            "luck_level": "吉",
            "suitability": ["宜出行", "宜社交"],
            "lucky_color": "红色",
            "lucky_number": 8,
            "general_summary": "今日运势不错，适合新的开始。",
        },
        "generated_at": datetime.now().isoformat(),
        "is_pushed": False,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }


@pytest.fixture
def sample_other_profile_data():
    """样例他人档案数据"""
    return {
        "id": str(uuid4()),
        "user_id": str(uuid4()),
        "name": "张三",
        "gender": "male",
        "birth_year": 1990,
        "birth_month": 5,
        "birth_day": 20,
        "birth_hour": 10,
        "birth_minute": 0,
        "birth_second": 0,
        "birth_location": "上海市",
        "birth_longitude": 121.4737,
        "birth_latitude": 31.2304,
        "relation_type": "朋友",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }


@pytest.fixture
def sample_compatibility_result():
    """样例合盘分析结果"""
    return {
        "overall_score": 85,
        "aspect_scores": {
            "emotional_connection": 90,
            "communication_style": 80,
            "values_alignment": 85,
            "conflict_resolution": 75,
        },
        "relationship_overview": "你们之间有着很好的匹配度",
        "short_term_outlook": "短期内关系和谐",
        "medium_term_outlook": "中期需要增进沟通",
        "long_term_outlook": "长期前景良好",
        "strengths": ["情感连接强", "价值观相近"],
        "challenges": ["沟通方式有差异"],
        "actionable_advice": ["多进行深度交流", "学会换位思考"],
    }


@pytest.fixture
def sample_compatibility_data(sample_user_id):
    """样例配对分析数据"""
    return {
        "id": str(uuid4()),
        "user_id": sample_user_id,
        "other_profile_id": str(uuid4()),
        "analysis_type": "natal_chart",
        "compatibility_score": 85,
        "analysis_details": {
            "overall_score": 85,
            "detailed_analysis": {
                "personality_match": {"score": 90, "explanation": "性格互补性很好"},
                "life_goal_alignment": {"score": 80, "explanation": "人生目标相对一致"},
            },
            "strengths": ["互补性强", "价值观相近"],
            "challenges": ["需要更多沟通"],
            "recommendations": ["多参与共同活动"],
            "summary": "你们的配对度很高，建议进一步发展关系。",
        },
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }


@pytest.fixture
def mock_algorithm_response():
    """Mock算法服务响应"""
    return {
        "user_id": str(uuid4()),
        "analysis_results": {
            "birth_chart_traditional": {
                "heavenly_stems": ["甲", "乙", "丙", "丁"],
                "earthly_branches": ["子", "丑", "寅", "卯"],
                "five_elements_balance": {"wood": "balanced", "fire": "strong"},
                "lucky_elements": ["wood", "water"],
                "summary": "根据八字分析，您具备很好的创造力",
            },
            "birth_chart_astrology": {
                "sun_sign": "Leo",
                "moon_sign": "Cancer",
                "rising_sign": "Scorpio",
                "summary": "根据您的星盘，您是一个富有感情的人",
            },
        },
    }
