"""
Environment Configuration
"""

from .loader import EnhancedSettings, create_settings

# Global settings instance
settings: EnhancedSettings = create_settings()
