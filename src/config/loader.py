"""
Configuration Loader

Supports loading configuration from YAML files for different environments.
"""
import os
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore[import-untyped]
except ImportError:
    yaml = None

from pydantic import Field
from pydantic_settings import BaseSettings


class YamlConfigLoader:
    """YAML configuration loader"""

    @staticmethod
    def load_yaml_config(config_path: str) -> dict[str, Any]:
        """Load configuration from YAML file"""
        if yaml is None:
            print("Warning: PyYAML not installed, skipping YAML config loading")
            return {}

        try:
            with open(config_path, encoding="utf-8") as file:
                config = yaml.safe_load(file)
                return config or {}
        except FileNotFoundError:
            print(f"Warning: Config file {config_path} not found")
            return {}
        except yaml.YAMLError as e:
            print(f"Error parsing YAML config file {config_path}: {e}")
            return {}

    @staticmethod
    def get_config_path(environment: str) -> str:
        """Get configuration file path for environment"""
        project_root = Path(__file__).parent.parent.parent
        config_file = f"env-{environment}.yaml"
        return str(project_root / "config" / config_file)


class EnhancedSettings(BaseSettings):
    """Enhanced settings with YAML config support"""

    # Environment
    ENVIRONMENT: str = Field(default="development", description="Environment name")

    # Supabase Configuration
    SUPABASE_URL: str = Field(default="", description="Supabase project URL")
    SUPABASE_KEY: str = Field(default="", description="Supabase anon key")
    SUPABASE_SERVICE_ROLE_KEY: str = Field(
        default="", description="Supabase service role key"
    )

    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql://postgres:password@localhost:54322/postgres",
        description="Database connection URL",
    )

    # API Configuration
    API_HOST: str = Field(default="127.0.0.1", description="API host")
    API_PORT: int = Field(default=8000, description="API port")
    API_RELOAD: bool = Field(default=True, description="API auto-reload")
    API_WORKERS: int = Field(default=1, description="API worker count")

    # CORS Configuration
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="CORS allowed origins",
    )

    # Algorithm Service Configuration
    ALGORITHM_SERVICE_URL: str = Field(
        default="http://localhost:8001", description="Algorithm service URL"
    )
    ALGORITHM_SERVICE_TIMEOUT: int = Field(
        default=30, description="Algorithm service timeout"
    )
    ALGORITHM_SERVICE_RETRIES: int = Field(
        default=3, description="Algorithm service retries"
    )

    # External API Configuration
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key")
    OPENAI_MODEL: str = Field(default="gpt-3.5-turbo", description="OpenAI model")
    CLAUDE_API_KEY: str = Field(default="", description="Claude API key")
    CLAUDE_MODEL: str = Field(
        default="claude-3-sonnet-20240229", description="Claude model"
    )

    # Payment Service Configuration
    STRIPE_SECRET_KEY: str = Field(default="", description="Stripe secret key")
    STRIPE_WEBHOOK_SECRET: str = Field(default="", description="Stripe webhook secret")
    STRIPE_MODE: str = Field(default="test", description="Stripe mode")
    ALIPAY_APP_ID: str = Field(default="", description="Alipay app ID")
    ALIPAY_PRIVATE_KEY: str = Field(default="", description="Alipay private key")
    ALIPAY_MODE: str = Field(default="sandbox", description="Alipay mode")

    # Push Notification Configuration
    FCM_SERVER_KEY: str = Field(default="", description="Firebase FCM server key")
    APNS_KEY_ID: str = Field(default="", description="Apple Push Notification key ID")
    APNS_TEAM_ID: str = Field(default="", description="Apple Push Notification team ID")
    APNS_BUNDLE_ID: str = Field(
        default="", description="Apple Push Notification bundle ID"
    )
    APNS_ENVIRONMENT: str = Field(
        default="sandbox", description="Apple Push Notification environment"
    )

    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FILE: str = Field(default="logs/aura.log", description="Log file path")
    LOG_MAX_SIZE: str = Field(default="10MB", description="Log file max size")
    LOG_BACKUP_COUNT: int = Field(default=5, description="Log backup count")

    # Rate Limiting Configuration
    RATE_LIMITING_ENABLED: bool = Field(
        default=False, description="Enable rate limiting"
    )
    RATE_LIMITING_DEFAULT: str = Field(
        default="100/hour", description="Default rate limit"
    )
    RATE_LIMITING_PREMIUM: str = Field(
        default="1000/hour", description="Premium rate limit"
    )

    # Security Configuration
    TRUSTED_HOSTS: list[str] = Field(default=["*"], description="Trusted hosts")
    FORCE_HTTPS: bool = Field(default=False, description="Force HTTPS")

    # Cache Configuration
    REDIS_URL: str = Field(default="", description="Redis URL")
    CACHE_DEFAULT_TTL: int = Field(default=3600, description="Cache default TTL")

    # Monitoring Configuration
    MONITORING_ENABLED: bool = Field(default=False, description="Enable monitoring")
    PROMETHEUS_METRICS: bool = Field(
        default=False, description="Enable Prometheus metrics"
    )
    SENTRY_DSN: str = Field(default="", description="Sentry DSN")

    def __init__(self, **kwargs: Any) -> None:
        # Load YAML configuration first
        env = os.getenv("ENVIRONMENT", "development")
        config_path = YamlConfigLoader.get_config_path(env)
        yaml_config = YamlConfigLoader.load_yaml_config(config_path)

        # Flatten YAML config to match field names
        flattened_config = self._flatten_yaml_config(yaml_config)
        # Merge with kwargs (environment variables and direct parameters)
        merged_config = {**flattened_config, **kwargs}

        super().__init__(**merged_config)

    def _flatten_yaml_config(self, config: dict[str, Any]) -> dict[str, Any]:
        """Flatten nested YAML config to match Pydantic field names"""
        flattened = {}

        # Map YAML structure to Pydantic fields
        mapping = {
            "environment": "ENVIRONMENT",
            "api.host": "API_HOST",
            "api.port": "API_PORT",
            "api.reload": "API_RELOAD",
            "api.workers": "API_WORKERS",
            "supabase.url": "SUPABASE_URL",
            "supabase.anon_key": "SUPABASE_KEY",
            "supabase.service_role_key": "SUPABASE_SERVICE_ROLE_KEY",
            "database.url": "DATABASE_URL",
            "algorithm_service.url": "ALGORITHM_SERVICE_URL",
            "algorithm_service.timeout": "ALGORITHM_SERVICE_TIMEOUT",
            "algorithm_service.retries": "ALGORITHM_SERVICE_RETRIES",
            "cors.origins": "CORS_ORIGINS",
            "external_apis.openai.api_key": "OPENAI_API_KEY",
            "external_apis.openai.model": "OPENAI_MODEL",
            "external_apis.claude.api_key": "CLAUDE_API_KEY",
            "external_apis.claude.model": "CLAUDE_MODEL",
            "payment.stripe.secret_key": "STRIPE_SECRET_KEY",
            "payment.stripe.webhook_secret": "STRIPE_WEBHOOK_SECRET",
            "payment.stripe.mode": "STRIPE_MODE",
            "payment.alipay.app_id": "ALIPAY_APP_ID",
            "payment.alipay.private_key": "ALIPAY_PRIVATE_KEY",
            "payment.alipay.mode": "ALIPAY_MODE",
            "push_notification.fcm.server_key": "FCM_SERVER_KEY",
            "push_notification.apns.key_id": "APNS_KEY_ID",
            "push_notification.apns.team_id": "APNS_TEAM_ID",
            "push_notification.apns.bundle_id": "APNS_BUNDLE_ID",
            "push_notification.apns.environment": "APNS_ENVIRONMENT",
            "logging.level": "LOG_LEVEL",
            "logging.file": "LOG_FILE",
            "logging.max_size": "LOG_MAX_SIZE",
            "logging.backup_count": "LOG_BACKUP_COUNT",
            "rate_limiting.enabled": "RATE_LIMITING_ENABLED",
            "rate_limiting.default_limit": "RATE_LIMITING_DEFAULT",
            "rate_limiting.premium_limit": "RATE_LIMITING_PREMIUM",
            "security.trusted_hosts": "TRUSTED_HOSTS",
            "security.force_https": "FORCE_HTTPS",
            "cache.redis_url": "REDIS_URL",
            "cache.default_ttl": "CACHE_DEFAULT_TTL",
            "monitoring.enabled": "MONITORING_ENABLED",
            "monitoring.prometheus_metrics": "PROMETHEUS_METRICS",
            "monitoring.sentry_dsn": "SENTRY_DSN",
        }

        for yaml_path, field_name in mapping.items():
            value = self._get_nested_value(config, yaml_path)
            if value is not None:
                flattened[field_name] = value

        return flattened

    def _get_nested_value(self, data: dict[str, Any], path: str) -> Any:
        """Get value from nested dictionary using dot notation"""
        keys = path.split(".")
        current = data

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None

        return current

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create enhanced settings instance
def create_settings() -> EnhancedSettings:
    """Create settings instance with environment-specific configuration"""
    return EnhancedSettings()
