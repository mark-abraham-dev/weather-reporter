import logging.config
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.core.exceptions import WeatherAPIException, DatabaseException
from app.core.logging_config import setup_logging, get_logger
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.services.scheduler_service import SchedulerService
from app.api.routes import weather, health

# Setup logging first before importing other modules
setup_logging()
logger = get_logger()

settings = get_settings()
scheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan - handles startup and shutdown events
    """
    global scheduler

    # Startup
    logger.info("Starting Weather Monitoring Service")
    try:
        await connect_to_mongo()

        # Initialize and start the scheduler
        scheduler = SchedulerService()
        scheduler.start()

        logger.info("Application startup complete")
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down Weather Monitoring Service")
    try:
        if scheduler:
            scheduler.shutdown()
        await close_mongo_connection()
        logger.info("Application shutdown complete")
    except Exception as e:
        logger.error(f"Shutdown error: {str(e)}")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API for monitoring and storing Austin weather data",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api")
app.include_router(weather.router, prefix="/api")


# Exception handlers
@app.exception_handler(WeatherAPIException)
async def handle_weather_api_exception(request: Request, exc: WeatherAPIException):
    logger.error(f"Weather API error: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


@app.exception_handler(DatabaseException)
async def handle_database_exception(request: Request, exc: DatabaseException):
    logger.error(f"Database error: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


@app.get("/api")
async def root():
    return {
        "name": settings.APP_NAME, 
        "version": settings.APP_VERSION,
        "description": "Weather Monitoring Service for Austin, TX"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
