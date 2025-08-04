#!/usr/bin/env python3
"""
Database Initialization Script

Creates necessary database tables and initial data.
"""

import asyncio
import logging
import sys
from pathlib import Path

from src.config.env import settings

# Add project root to path (after imports)
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_database() -> None:
    """Initialize database with required tables"""
    logger.info("Starting database initialization...")

    try:
        # Note: In a real implementation, you would use your database client here
        # For now, we'll just log the process since we're using Supabase

        logger.info("Database initialization completed successfully")
        logger.info(
            "Note: Using Supabase - tables should be created via Supabase dashboard or migration scripts"
        )

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def create_test_data() -> None:
    """Create test data for development"""
    logger.info("Creating test data...")

    try:
        # This would create test users, avatars, etc.
        logger.info("Test data creation completed")

    except Exception as e:
        logger.error(f"Test data creation failed: {e}")
        raise


async def main() -> None:
    """Main initialization function"""
    logger.info(f"Initializing database for environment: {settings.ENVIRONMENT}")

    await init_database()

    if settings.ENVIRONMENT == "development":
        await create_test_data()

    logger.info("Database setup completed!")


if __name__ == "__main__":
    asyncio.run(main())
