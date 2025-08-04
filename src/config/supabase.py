"""
Supabase Client Configuration
"""
from typing import Any

from .env import settings

supabase_client: Any = None
admin_client: Any = None

try:
    from supabase import create_client  # type: ignore[attr-defined]

    # Create Supabase client instance
    supabase_client = create_client(
        supabase_url=settings.SUPABASE_URL, supabase_key=settings.SUPABASE_KEY
    )

    # Create admin client for service operations
    admin_client = create_client(
        supabase_url=settings.SUPABASE_URL,
        supabase_key=settings.SUPABASE_SERVICE_ROLE_KEY,
    )
except ImportError:
    # Handle case where supabase is not installed
    pass  # Clients remain None
