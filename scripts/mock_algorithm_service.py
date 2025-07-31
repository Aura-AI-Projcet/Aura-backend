"""
Mock Algorithm Service for Development

This is a simple mock service that simulates the algorithm service
responses for testing and development purposes.
"""
import time
from typing import Any

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Mock Algorithm Service", version="1.0.0")

class BirthInfo(BaseModel):
    year: int
    month: int
    day: int
    hour: int | None = None
    minute: int | None = None
    second: int | None = None
    location: str
    longitude: float | None = None
    latitude: float | None = None

class UserProfileAnalysisRequest(BaseModel):
    user_id: str
    birth_info: BirthInfo

@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "service": "mock-algorithm"}

@app.post("/api/algorithm/user-profile-analysis")
async def user_profile_analysis(request: UserProfileAnalysisRequest) -> dict[str, Any]:
    """Mock user profile analysis endpoint"""

    # Simulate processing time
    time.sleep(2)

    # Generate mock analysis result
    analysis_results = {
        "birth_chart_traditional": {
            "heavenly_stems": ["甲", "乙", "丙", "丁"],
            "earthly_branches": ["子", "丑", "寅", "卯"],
            "five_elements_balance": {
                "wood": "balanced",
                "fire": "strong",
                "earth": "weak",
                "metal": "balanced",
                "water": "strong"
            },
            "lucky_elements": ["wood", "water"],
            "summary": f"根据您{request.birth_info.year}年{request.birth_info.month}月{request.birth_info.day}日的出生信息，您的八字显示出独特的命理特征。",
            "detailed_analysis": {
                "personality": "您天生具备领导力，但在感情中可能略显强势。",
                "career": "适合从事创新型工作，在艺术或科技领域能发挥所长。",
                "health": "需要注意心血管健康，建议多做有氧运动。"
            }
        },
        "birth_chart_astrology": {
            "sun_sign": "Leo",
            "moon_sign": "Cancer",
            "rising_sign": "Scorpio",
            "planets_positions": [
                {"planet": "Mars", "sign": "Aries", "degree": 15},
                {"planet": "Venus", "sign": "Gemini", "degree": 22},
                {"planet": "Mercury", "sign": "Leo", "degree": 8}
            ],
            "aspects": [
                {"planet1": "Sun", "planet2": "Moon", "type": "trine", "orb": 2},
                {"planet1": "Mars", "planet2": "Venus", "type": "square", "orb": 3}
            ],
            "houses_cusps": {
                "house1": "Scorpio",
                "house2": "Sagittarius",
                "house3": "Capricorn"
            },
            "summary": "根据您的星盘，您具备强烈的个人魅力和创造力。",
            "detailed_analysis": {
                "love": "在感情中比较主动，但需要学会倾听伴侣的声音。",
                "money": "财运不错，但要避免冲动消费。",
                "career": "创意型工作最适合您，能够充分发挥天赋。"
            }
        },
        "general_insights": [
            "您天生具备领导力，但在感情中可能略显强势。",
            "近期需关注肠胃健康，建议多食绿色蔬菜。",
            "本月有贵人相助，适合主动社交和合作。",
            f"您的幸运数字是{(request.birth_info.day + request.birth_info.month) % 9 + 1}，幸运颜色是蓝色。"
        ]
    }

    return {
        "user_id": request.user_id,
        "analysis_results": analysis_results
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
