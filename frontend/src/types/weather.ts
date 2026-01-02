/**
 * TypeScript type definitions for Weather App
 * Ensures type safety across the frontend application
 */

export interface WeatherReading {
  id: number;
  dateutc: number;
  date: string;
  tempf?: number;
  humidity?: number;
  baromabsin?: number;
  baromrelin?: number;
  windspeedmph?: number;
  winddir?: number;
  windgustmph?: number;
  maxdailygust?: number;
  hourlyrainin?: number;
  eventrain?: number;
  dailyrainin?: number;
  weeklyrainin?: number;
  monthlyrainin?: number;
  yearlyrainin?: number;
  totalrainin?: number;
  solarradiation?: number;
  uv?: number;
  feelsLike?: number;
  dewPoint?: number;
  feelsLikein?: number;
  dewPointin?: number;
  lastRain?: string;
  tz?: string;
  raw_json?: string;
}

export interface WeatherStats {
  total_records: number;
  min_date?: string;
  max_date?: string;
  avg_temperature?: number;
  min_temperature?: number;
  max_temperature?: number;
  avg_humidity?: number;
  min_humidity?: number;
  max_humidity?: number;
}

export interface DateRangeQuery {
  startDate?: string;
  endDate?: string;
  limit?: number;
}

export interface ChartDataPoint {
  timestamp: string;
  date: string;
  temperature?: number;
  humidity?: number;
  pressure?: number;
  windSpeed?: number;
  rainfall?: number;
}

export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}
