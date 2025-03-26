import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from app.core.config import get_settings
from app.services.weather_service import WeatherService

logger = logging.getLogger("weather_service")
settings = get_settings()


class SchedulerService:
    """Service for managing scheduled tasks"""

    def __init__(self, weather_service: WeatherService = None):
        self.scheduler = AsyncIOScheduler()
        self.weather_service = weather_service or WeatherService()
        self.interval_seconds = settings.WEATHER_UPDATE_INTERVAL_SECONDS

    async def fetch_weather_task(self):
        """Task that fetches and stores weather data"""
        try:
            logger.info(f"Executing scheduled weather update at {datetime.utcnow().isoformat()}")
            await self.weather_service.fetch_and_store_weather()
        except Exception as e:
            logger.error(f"Error in scheduled weather update: {str(e)}")

    async def maintenance_task(self):
        """Task that performs database maintenance"""
        try:
            logger.info(f"Executing scheduled maintenance at {datetime.utcnow().isoformat()}")
            await self.weather_service.perform_maintenance(retention_days=30)
        except Exception as e:
            logger.error(f"Error in scheduled maintenance: {str(e)}")

    def start(self):
        """Start the scheduler with all jobs"""
        if self.scheduler.running:
            return

        try:
            # Weather update job - runs every X seconds
            self.scheduler.add_job(
                self.fetch_weather_task,
                IntervalTrigger(seconds=self.interval_seconds),
                id="weather_update",
                replace_existing=True,
                max_instances=1,
            )

            # Maintenance job - runs daily at 3 AM
            self.scheduler.add_job(
                self.maintenance_task,
                CronTrigger(hour=3, minute=0),
                id="db_maintenance",
                replace_existing=True,
                max_instances=1,
            )

            self.scheduler.start()
            logger.info(f"Scheduler started with weather updates every {self.interval_seconds} seconds")
        except Exception as e:
            logger.error(f"Failed to start scheduler: {str(e)}")

    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            try:
                self.scheduler.shutdown()
                logger.info("Scheduler shut down")
            except Exception as e:
                logger.error(f"Error shutting down scheduler: {str(e)}")
