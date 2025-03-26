from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional
from datetime import datetime, timedelta
from app.services.weather_service import WeatherService
from app.models.weather import WeatherResponse, WeatherHistoryResponse
from app.api.deps import get_weather_service

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get("/current", response_model=WeatherResponse)
async def get_current_weather(
    weather_service: WeatherService = Depends(get_weather_service)
):
    """
    Get the most recent weather data for Austin, TX
    """
    weather_data = await weather_service.get_latest_weather()
    if not weather_data:
        # If no data exists, fetch new data
        weather_data = await weather_service.fetch_and_store_weather()

    return {
        "data": weather_data,
        "message": "Current weather data retrieved successfully"
    }


@router.get("/history", response_model=WeatherHistoryResponse)
async def get_weather_history(
    start_date: Optional[datetime] = Query(None, description="Start date/time in ISO format"),
    end_date: Optional[datetime] = Query(None, description="End date/time in ISO format"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    weather_service: WeatherService = Depends(get_weather_service)
):
    """
    Get historical weather data for Austin, TX with optional date range filtering
    """
    # Default to last 24 hours if no dates specified
    if not start_date and not end_date:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=1)

    history_data = await weather_service.repository.get_history(
        location=weather_service.location,
        start_time=start_date,
        end_time=end_date,
        limit=limit,
        skip=offset
    )

    total_count = await weather_service.repository.count_records(weather_service.location)

    return {
        "data": history_data,
        "count": total_count,
        "message": f"Retrieved {len(history_data)} weather records"
    }


@router.post("/refresh", response_model=WeatherResponse, status_code=status.HTTP_201_CREATED)
async def refresh_weather_data(
    weather_service: WeatherService = Depends(get_weather_service)
):
    """
    Force a refresh of weather data by fetching the current weather
    """
    weather_data = await weather_service.fetch_and_store_weather()

    return {
        "data": weather_data,
        "message": "Weather data refreshed successfully"
    }
