#!/usr/bin/env python3
"""
Health Check Script

Performs comprehensive health checks on the BFF service.
"""

import asyncio
import logging
import sys
from pathlib import Path

import httpx

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def check_service_health(base_url: str = "http://127.0.0.1:8000") -> None:
    """Check service health endpoints"""

    async with httpx.AsyncClient() as client:
        try:
            # Check main health endpoint
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                logger.info("✅ Main health check passed")
                logger.info(f"Response: {response.json()}")
            else:
                logger.error(f"❌ Main health check failed: {response.status_code}")

            # Check API health endpoint
            response = await client.get(f"{base_url}/api/v1/health")
            if response.status_code == 200:
                logger.info("✅ API health check passed")
                logger.info(f"Response: {response.json()}")
            else:
                logger.error(f"❌ API health check failed: {response.status_code}")

        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")


async def check_database_connection() -> None:
    """Check database connectivity"""
    try:
        # This would check Supabase connection in a real implementation
        logger.info("✅ Database connection check (stubbed for Supabase)")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")


async def check_algorithm_service() -> None:
    """Check algorithm service connectivity"""
    try:
        # This would ping the algorithm service
        logger.info("✅ Algorithm service check (stubbed)")
    except Exception as e:
        logger.error(f"❌ Algorithm service connection failed: {e}")


async def main() -> None:
    """Run all health checks"""
    logger.info("Starting comprehensive health check...")

    await check_service_health()
    await check_database_connection()
    await check_algorithm_service()

    logger.info("Health check completed!")


if __name__ == "__main__":
    asyncio.run(main())
