"""
Pydantic models for API responses
"""

from pydantic import BaseModel


class WeatherData(BaseModel):
    """Response model for weather data records"""

    id: int
    dateutc: int
    date: str
    tempf: float | None = None
    feelsLike: float | None = None
    dewPoint: float | None = None
    tempinf: float | None = None
    humidity: int | None = None
    humidityin: int | None = None
    baromrelin: float | None = None
    baromabsin: float | None = None
    windspeedmph: float | None = None
    windgustmph: float | None = None
    winddir: int | None = None
    maxdailygust: float | None = None
    hourlyrainin: float | None = None
    dailyrainin: float | None = None
    weeklyrainin: float | None = None
    monthlyrainin: float | None = None
    totalrainin: float | None = None
    solarradiation: float | None = None
    uv: int | None = None
    battout: int | None = None
    battin: int | None = None
    raw_json: str | None = None

    class Config:
        from_attributes = True


class DatabaseStats(BaseModel):
    """Response model for database statistics"""

    total_records: int
    min_date: str | None = None
    max_date: str | None = None
    date_range_days: int | None = None
