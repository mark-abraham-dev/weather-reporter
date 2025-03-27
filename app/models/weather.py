from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List


class WeatherBase(BaseModel):
    """Base weather model with common attributes"""
    location: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WeatherCondition(BaseModel):
    """Weather condition details"""
    text: str
    code: int
    icon: str


class WeatherCurrent(BaseModel):
    """Current weather data"""
    temp_c: float
    temp_f: float
    feelslike_c: float
    feelslike_f: float
    humidity: int
    wind_kph: float
    wind_mph: float
    wind_dir: str
    pressure_mb: float
    precip_mm: float
    cloud: int
    uv: float
    condition: WeatherCondition


class WeatherLocation(BaseModel):
    """Location information"""
    name: str
    region: str
    country: str
    lat: float
    lon: float
    tz_id: str
    localtime: str


class WeatherData(WeatherBase):
    """Complete weather data model"""
    id: Optional[str] = None
    location_data: WeatherLocation
    current: WeatherCurrent

    model_config = {
        "json_schema_extra": {
            "example": {
                "location": "Austin,TX",
                "timestamp": "2023-10-15T14:30:00.000Z",
                "location_data": {
                    "name": "Austin",
                    "region": "Texas",
                    "country": "USA",
                    "lat": 30.27,
                    "lon": -97.74,
                    "tz_id": "America/Chicago",
                    "localtime": "2023-10-15 09:30"
                },
                "current": {
                    "temp_c": 24.0,
                    "temp_f": 75.2,
                    "feelslike_c": 24.8,
                    "feelslike_f": 76.6,
                    "humidity": 65,
                    "wind_kph": 14.4,
                    "wind_mph": 8.9,
                    "wind_dir": "SSE",
                    "pressure_mb": 1015.0,
                    "precip_mm": 0.0,
                    "cloud": 25,
                    "uv": 5.0,
                    "condition": {
                        "text": "Partly cloudy",
                        "code": 1003,
                        "icon": "//cdn.weatherapi.com/weather/64x64/day/116.png"
                    }
                }
            }
        }
    }


class WeatherResponse(BaseModel):
    """API response model for weather data"""
    data: WeatherData
    message: str = "Weather data retrieved successfully"


class WeatherHistoryResponse(BaseModel):
    """API response model for weather history"""
    data: List[WeatherData]
    count: int
    message: str = "Weather history retrieved successfully"
