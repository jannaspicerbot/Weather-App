"""
Pydantic models for API responses
"""

from pydantic import BaseModel
from typing import Optional


class WeatherData(BaseModel):
    """Response model for weather data records"""
    id: int
    dateutc: int
    date: str
    tempf: Optional[float] = None
    feelsLike: Optional[float] = None
    dewPoint: Optional[float] = None
    tempinf: Optional[float] = None
    humidity: Optional[int] = None
    humidityin: Optional[int] = None
    baromrelin: Optional[float] = None
    baromabsin: Optional[float] = None
    windspeedmph: Optional[float] = None
    windgustmph: Optional[float] = None
    winddir: Optional[int] = None
    maxdailygust: Optional[float] = None
    hourlyrainin: Optional[float] = None
    dailyrainin: Optional[float] = None
    weeklyrainin: Optional[float] = None
    monthlyrainin: Optional[float] = None
    totalrainin: Optional[float] = None
    solarradiation: Optional[float] = None
    uv: Optional[int] = None
    battout: Optional[int] = None
    battin: Optional[int] = None
    raw_json: Optional[str] = None

    class Config:
        from_attributes = True


class DatabaseStats(BaseModel):
    """Response model for database statistics"""
    total_records: int
    min_date: Optional[str] = None
    max_date: Optional[str] = None
    date_range_days: Optional[int] = None
