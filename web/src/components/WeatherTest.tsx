/**
 * Test component to verify OpenAPI TypeScript codegen works correctly
 *
 * This component demonstrates:
 * 1. Using generated TypeScript types (WeatherData)
 * 2. Using generated API service (DefaultService)
 * 3. Full type safety from backend to frontend
 */

import { useEffect, useState } from 'react';
import { DefaultService, type WeatherData, type DatabaseStats } from '../api';

export default function WeatherTest() {
  const [latestWeather, setLatestWeather] = useState<WeatherData | null>(null);
  const [stats, setStats] = useState<DatabaseStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);

        // TypeScript knows the exact return type!
        const [weather, dbStats] = await Promise.all([
          DefaultService.getLatestWeatherWeatherLatestGet(),
          DefaultService.getDatabaseStatsWeatherStatsGet(),
        ]);

        // TypeScript autocomplete works here
        setLatestWeather(weather);
        setStats(dbStats);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
        console.error('Failed to fetch weather data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="weather-test__loading">
        Loading weather data...
      </div>
    );
  }

  if (error) {
    return (
      <div className="weather-test__error">
        Error: {error}
      </div>
    );
  }

  return (
    <div className="weather-test">
      <h1 className="weather-test__title">Weather Data (Type-Safe API Test)</h1>

      {/* Latest Weather */}
      {latestWeather && (
        <div className="weather-test__card">
          <h2 className="weather-test__card-title">Latest Reading</h2>
          <div className="weather-test__grid">
            <div>
              <p className="weather-test__field-label">Date</p>
              <p className="weather-test__field-value">{latestWeather.date}</p>
            </div>
            <div>
              <p className="weather-test__field-label">Temperature</p>
              {/* TypeScript knows tempf is number | null | undefined */}
              <p className="weather-test__field-value">
                {latestWeather.tempf?.toFixed(1) ?? 'N/A'}°F
              </p>
            </div>
            <div>
              <p className="weather-test__field-label">Feels Like</p>
              <p className="weather-test__field-value">
                {latestWeather.feelsLike?.toFixed(1) ?? 'N/A'}°F
              </p>
            </div>
            <div>
              <p className="weather-test__field-label">Humidity</p>
              <p className="weather-test__field-value">
                {latestWeather.humidity ?? 'N/A'}%
              </p>
            </div>
            <div>
              <p className="weather-test__field-label">Wind Speed</p>
              <p className="weather-test__field-value">
                {latestWeather.windspeedmph?.toFixed(1) ?? 'N/A'} mph
              </p>
            </div>
            <div>
              <p className="weather-test__field-label">Wind Gust</p>
              <p className="weather-test__field-value">
                {latestWeather.windgustmph?.toFixed(1) ?? 'N/A'} mph
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Database Stats */}
      {stats && (
        <div className="weather-test__card">
          <h2 className="weather-test__card-title">Database Statistics</h2>
          <div className="weather-test__grid">
            <div>
              <p className="weather-test__field-label">Total Records</p>
              <p className="weather-test__field-value">{stats.total_records.toLocaleString()}</p>
            </div>
            <div>
              <p className="weather-test__field-label">Date Range</p>
              <p className="weather-test__field-value">
                {stats.date_range_days ? `${stats.date_range_days} days` : 'N/A'}
              </p>
            </div>
            <div>
              <p className="weather-test__field-label">Oldest Reading</p>
              <p className="weather-test__field-value">{stats.min_date ?? 'N/A'}</p>
            </div>
            <div>
              <p className="weather-test__field-label">Latest Reading</p>
              <p className="weather-test__field-value">{stats.max_date ?? 'N/A'}</p>
            </div>
          </div>
        </div>
      )}

      {/* Type Safety Demo */}
      <div className="weather-test__info">
        <h3 className="weather-test__info-title">Type Safety Verified</h3>
        <ul className="weather-test__info-list">
          <li>API response types auto-generated from FastAPI</li>
          <li>TypeScript autocomplete works for all fields</li>
          <li>Compile-time errors if API contract changes</li>
          <li>Zero manual type maintenance required</li>
        </ul>
      </div>
    </div>
  );
}
