from fastapi import Depends
from app.services.weather_service import WeatherService
from app.db.repositories.weather_repository import WeatherRepository


async def get_weather_repository() -> WeatherRepository:
    """Dependency for getting the weather repository"""
    repository = WeatherRepository()
    return repository


async def get_weather_service(
    repository: WeatherRepository = Depends(get_weather_repository)
) -> WeatherService:
    """Dependency for getting the weather service"""
    return WeatherService(repository=repository)
