from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional, AsyncGenerator
import logging
from app.core.config import get_settings
from contextlib import asynccontextmanager

logger = logging.getLogger("weather_service")
settings = get_settings()


class Database:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None


db = Database()


async def connect_to_mongo():
    """Connect to MongoDB"""
    logger.info("Connecting to MongoDB...")
    db.client = AsyncIOMotorClient(settings.MONGODB_URI)
    db.db = db.client[settings.MONGODB_DB_NAME]
    logger.info("Connected to MongoDB")


async def close_mongo_connection():
    """Close MongoDB connection"""
    logger.info("Closing MongoDB connection...")
    if db.client:
        db.client.close()
        logger.info("MongoDB connection closed")


@asynccontextmanager
async def get_database() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Get database connection as a context manager"""
    if db.db is None:
        await connect_to_mongo()

    try:
        yield db.db
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise
