import httpx
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from app.core.config import get_settings
from app.models.weather import WeatherData, WeatherLocation, WeatherCurrent, WeatherCondition
from app.core.exceptions import WeatherAPIException
from app.db.repositories.weather_repository import WeatherRepository

logger = logging.getLogger("weather_service")
settings = get_settings()


class WeatherService:
    """Service for fetching and processing weather data"""

    def __init__(self, repository: Optional[WeatherRepository] = None):
        self.api_key = settings.WEATHER_API_KEY
        self.api_url = settings.WEATHER_API_URL
        self.location = settings.WEATHER_LOCATION
        self.repository = repository or WeatherRepository()

    async def fetch_current_weather(self) -> WeatherData:
        """Fetch current weather data from the API"""
        try:
            # Parameters for OpenWeatherMap API
            params = {
                "appid": self.api_key,
                "lat": 30.2672,  # Austin latitude
                "lon": -97.7431,  # Austin longitude
                "units": "metric"  # Use metric for Celsius
            }

            async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
                response = await client.get(self.api_url, params=params)

                if response.status_code != 200:
                    error_detail = response.json() if response.headers.get("content-type") == "application/json" else response.text
                    logger.error(f"Weather API error: {error_detail}")
                    raise WeatherAPIException(
                        f"Weather API returned error {response.status_code}: {error_detail}", 
                        response.status_code
                    )

                api_data = response.json()
                return self._transform_openweathermap_data(api_data)

        except httpx.TimeoutException:
            logger.error("Weather API request timed out")
            raise WeatherAPIException("Weather API request timed out", 408)

        except httpx.RequestError as e:
            logger.error(f"Weather API request failed: {str(e)}")
            raise WeatherAPIException(f"Weather API request failed: {str(e)}")

        except Exception as e:
            logger.error(f"Unexpected error fetching weather: {str(e)}")
            raise WeatherAPIException(f"Error fetching weather data: {str(e)}")

    def _transform_openweathermap_data(self, api_data: Dict[Any, Any]) -> WeatherData:
        """Transform OpenWeatherMap API response to WeatherData model"""
        try:
            # Convert OpenWeatherMap data format to our model format
            location_data = WeatherLocation(
                name=api_data["name"],
                region=api_data.get("sys", {}).get("country", "Unknown"),
                country=api_data.get("sys", {}).get("country", "Unknown"),
                lat=api_data["coord"]["lat"],
                lon=api_data["coord"]["lon"],
                tz_id=f"UTC{int(api_data.get('timezone', 0)//3600):+d}",  # Convert seconds to hours offset
                localtime=datetime.utcfromtimestamp(
                    api_data.get("dt", datetime.utcnow().timestamp())
                ).strftime("%Y-%m-%d %H:%M")
            )

            # Get first weather condition if available
            weather_condition = api_data.get("weather", [{"main": "Unknown", "id": 0, "icon": ""}])[0]
            
            condition = WeatherCondition(
                text=weather_condition.get("description", "Unknown"),
                code=weather_condition.get("id", 0),
                icon=f"https://openweathermap.org/img/wn/{weather_condition.get('icon', '01d')}@2x.png"
            )

            # Convert temperature from Kelvin if needed (if units=metric was not used)
            temp_c = api_data["main"]["temp"]
            if temp_c > 100:  # Likely in Kelvin
                temp_c = temp_c - 273.15
                
            temp_f = (temp_c * 9/5) + 32

            # Convert wind speed from m/s to kph
            wind_kph = api_data.get("wind", {}).get("speed", 0) * 3.6  # m/s to kph
            wind_mph = wind_kph / 1.609344  # kph to mph

            current = WeatherCurrent(
                temp_c=temp_c,
                temp_f=temp_f,
                feelslike_c=api_data["main"].get("feels_like", temp_c),
                feelslike_f=(api_data["main"].get("feels_like", temp_c) * 9/5) + 32,
                humidity=api_data["main"].get("humidity", 0),
                wind_kph=wind_kph,
                wind_mph=wind_mph,
                wind_dir=self._degrees_to_direction(api_data.get("wind", {}).get("deg", 0)),
                pressure_mb=api_data["main"].get("pressure", 0),
                precip_mm=api_data.get("rain", {}).get("1h", 0) if "rain" in api_data else 0,
                cloud=api_data.get("clouds", {}).get("all", 0),
                uv=api_data.get("uvi", 0),  # OpenWeatherMap doesn't provide UV in basic API
                condition=condition
            )

            return WeatherData(
                location=self.location,
                timestamp=datetime.utcnow(),
                location_data=location_data,
                current=current
            )

        except KeyError as e:
            logger.error(f"Error parsing OpenWeatherMap API data: Missing key {e}")
            raise WeatherAPIException(f"Weather API returned unexpected data format: Missing key {e}")

    def _degrees_to_direction(self, degrees: float) -> str:
        """Convert wind direction in degrees to cardinal direction"""
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                      "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        index = round(degrees / 22.5) % 16
        return directions[index]

    async def fetch_and_store_weather(self) -> WeatherData:
        """Fetch weather data and store in the database"""
        weather_data = await self.fetch_current_weather()
        weather_id = await self.repository.create(weather_data)
        weather_data.id = weather_id
        logger.info(f"Weather data saved with ID: {weather_id}")
        return weather_data

    async def get_latest_weather(self) -> Optional[WeatherData]:
        """Get the latest weather data from the database"""
        return await self.repository.get_latest(self.location)

    async def perform_maintenance(self, retention_days: int = 30) -> int:
        """Clean up old weather records based on retention policy"""
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        deleted_count = await self.repository.cleanup_old_records(self.location, cutoff_date)
        logger.info(f"Cleaned up {deleted_count} weather records older than {retention_days} days")
        return deleted_count
