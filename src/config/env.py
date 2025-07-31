"""
Environment Configuration
"""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Supabase Configuration
    SUPABASE_URL: str = Field(default="", description="Supabase project URL")
    SUPABASE_KEY: str = Field(default="", description="Supabase anon key")
    SUPABASE_SERVICE_ROLE_KEY: str = Field(default="", description="Supabase service role key")

    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql://postgres:password@localhost:54322/postgres",
        description="Database connection URL"
    )

    # API Configuration
    API_HOST: str = Field(default="127.0.0.1", description="API host")
    API_PORT: int = Field(default=8000, description="API port")
    API_RELOAD: bool = Field(default=True, description="API auto-reload")

    # Environment
    ENVIRONMENT: str = Field(default="development", description="Environment name")

    # CORS Configuration
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="CORS allowed origins"
    )

    # Algorithm Service Configuration
    ALGORITHM_SERVICE_URL: str = Field(
        default="http://localhost:8001",
        description="Algorithm service URL"
    )

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
