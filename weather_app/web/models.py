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


class CredentialValidationRequest(BaseModel):
    """Request model for credential validation"""

    api_key: str
    app_key: str


class DeviceInfo(BaseModel):
    """Information about a weather device"""

    mac_address: str
    name: str | None = None
    last_data: str | None = None


class CredentialValidationResponse(BaseModel):
    """Response model for credential validation"""

    valid: bool
    message: str
    devices: list[DeviceInfo] = []


class CredentialStatusResponse(BaseModel):
    """Response model for credential status check"""

    configured: bool
    has_api_key: bool
    has_app_key: bool


class BackfillStartRequest(BaseModel):
    """Request model for starting a backfill"""

    api_key: str | None = None
    app_key: str | None = None


class BackfillProgressResponse(BaseModel):
    """Response model for backfill progress"""

    progress_id: int | None = None
    status: str  # 'idle', 'in_progress', 'completed', 'failed'
    message: str
    total_records: int = 0
    inserted_records: int = 0
    skipped_records: int = 0
    current_date: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    estimated_time_remaining_seconds: int | None = None
    requests_made: int = 0
    requests_per_second: float = 1.0
    records_per_request: int = 288
