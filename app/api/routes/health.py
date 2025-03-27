from fastapi import APIRouter, Depends
from app.db.mongodb import get_database
from app.core.config import get_settings
import asyncio

router = APIRouter(prefix="/health", tags=["Health"])
settings = get_settings()


@router.get("")
async def health_check():
    """
    Health check endpoint to verify API is running
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@router.get("/db")
async def db_health_check():
    """
    Database health check endpoint
    """
    try:
        async with get_database() as db:
            # Simple command to check db connection
            is_primary = await db.command("isMaster")
            return {
                "status": "healthy",
                "database": settings.MONGODB_DB_NAME,
                "is_primary": is_primary.get("ismaster", False)
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "detail": str(e)
        }
