"""
Supabase Client Configuration
"""
from supabase import Client, create_client

from .env import settings

# Create Supabase client instance
supabase_client: Client = create_client(
    supabase_url=settings.SUPABASE_URL,
    supabase_key=settings.SUPABASE_KEY
)

# Create admin client for service operations
admin_client: Client = create_client(
    supabase_url=settings.SUPABASE_URL,
    supabase_key=settings.SUPABASE_SERVICE_ROLE_KEY
)
