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
      <div className="p-4 text-gray-600">
        Loading weather data...
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 text-red-600">
        Error: {error}
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Weather Data (Type-Safe API Test)</h1>

      {/* Latest Weather */}
      {latestWeather && (
        <div className="bg-white shadow-md rounded-lg p-6 mb-6">
          <h2 className="text-2xl font-semibold mb-4">Latest Reading</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Date</p>
              <p className="text-lg font-medium">{latestWeather.date}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Temperature</p>
              {/* TypeScript knows tempf is number | null | undefined */}
              <p className="text-lg font-medium">
                {latestWeather.tempf?.toFixed(1) ?? 'N/A'}°F
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Feels Like</p>
              <p className="text-lg font-medium">
                {latestWeather.feelsLike?.toFixed(1) ?? 'N/A'}°F
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Humidity</p>
              <p className="text-lg font-medium">
                {latestWeather.humidity ?? 'N/A'}%
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Wind Speed</p>
              <p className="text-lg font-medium">
                {latestWeather.windspeedmph?.toFixed(1) ?? 'N/A'} mph
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Wind Gust</p>
              <p className="text-lg font-medium">
                {latestWeather.windgustmph?.toFixed(1) ?? 'N/A'} mph
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Database Stats */}
      {stats && (
        <div className="bg-white shadow-md rounded-lg p-6">
          <h2 className="text-2xl font-semibold mb-4">Database Statistics</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Total Records</p>
              <p className="text-lg font-medium">{stats.total_records.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Date Range</p>
              <p className="text-lg font-medium">
                {stats.date_range_days ? `${stats.date_range_days} days` : 'N/A'}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Oldest Reading</p>
              <p className="text-lg font-medium">{stats.min_date ?? 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Latest Reading</p>
              <p className="text-lg font-medium">{stats.max_date ?? 'N/A'}</p>
            </div>
          </div>
        </div>
      )}

      {/* Type Safety Demo */}
      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded">
        <h3 className="font-semibold text-blue-900 mb-2">✅ Type Safety Verified</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• API response types auto-generated from FastAPI</li>
          <li>• TypeScript autocomplete works for all fields</li>
          <li>• Compile-time errors if API contract changes</li>
          <li>• Zero manual type maintenance required</li>
        </ul>
      </div>
    </div>
  );
}
