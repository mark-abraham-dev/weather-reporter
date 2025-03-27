from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.db.mongodb import db
from app.models.weather import WeatherData
from app.core.config import get_settings
from app.core.exceptions import DatabaseException
import logging
from pymongo import DESCENDING, IndexModel

logger = logging.getLogger("weather_service")
settings = get_settings()


class WeatherRepository:
    """Repository for weather data operations"""

    def __init__(self):
        self.collection = db.db[settings.MONGODB_WEATHER_COLLECTION]

    async def initialize(self):
        """Initialize database indexes"""
        try:
            # Create indexes
            await self.collection.create_indexes([
                IndexModel([("timestamp", DESCENDING)]),
                IndexModel([("location", 1)])
            ])
            logger.info("Weather repository initialized with indexes")
        except Exception as e:
            logger.error(f"Failed to initialize weather repository: {str(e)}")
            raise DatabaseException(f"Database initialization error: {str(e)}")

    async def create(self, weather_data: WeatherData) -> str:
        """Insert new weather record"""
        try:
            weather_dict = weather_data.dict(exclude={"id"})
            result = await self.collection.insert_one(weather_dict)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to insert weather data: {str(e)}")
            raise DatabaseException(f"Error saving weather data: {str(e)}")

    async def get_latest(self, location: str) -> Optional[WeatherData]:
        """Get the latest weather data for a location"""
        try:
            result = await self.collection.find_one(
                {"location": location},
                sort=[("timestamp", DESCENDING)]
            )
            if result:
                result["id"] = str(result["_id"])
                return WeatherData(**result)
            return None
        except Exception as e:
            logger.error(f"Failed to get latest weather data: {str(e)}")
            raise DatabaseException(f"Error retrieving latest weather data: {str(e)}")

    async def get_history(
        self, 
        location: str, 
        start_time: Optional[datetime] = None, 
        end_time: Optional[datetime] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[WeatherData]:
        """Get historical weather data with optional time range"""
        try:
            query = {"location": location}

            if start_time or end_time:
                time_query = {}
                if start_time:
                    time_query["$gte"] = start_time
                if end_time:
                    time_query["$lte"] = end_time
                query["timestamp"] = time_query

            cursor = self.collection.find(query)
            cursor = cursor.sort("timestamp", DESCENDING)
            cursor = cursor.skip(skip).limit(limit)

            result = []
            async for doc in cursor:
                doc["id"] = str(doc["_id"])
                result.append(WeatherData(**doc))

            return result
        except Exception as e:
            logger.error(f"Failed to get weather history: {str(e)}")
            raise DatabaseException(f"Error retrieving weather history: {str(e)}")

    async def count_records(self, location: str) -> int:
        """Count weather records for a location"""
        try:
            return await self.collection.count_documents({"location": location})
        except Exception as e:
            logger.error(f"Failed to count weather records: {str(e)}")
            raise DatabaseException(f"Error counting weather records: {str(e)}")

    async def cleanup_old_records(self, location: str, older_than: datetime) -> int:
        """Delete weather records older than a specific date"""
        try:
            result = await self.collection.delete_many({
                "location": location,
                "timestamp": {"$lt": older_than}
            })
            return result.deleted_count
        except Exception as e:
            logger.error(f"Failed to clean up old records: {str(e)}")
            raise DatabaseException(f"Error cleaning up old weather records: {str(e)}")
