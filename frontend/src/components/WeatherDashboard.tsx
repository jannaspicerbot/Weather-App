/**
 * Weather Dashboard Component
 * Main dashboard showing weather statistics and charts
 */

import React, { useState } from 'react';
import { useLatestWeather, useWeatherStats } from '../hooks/useWeatherData';
import { WeatherChart } from './WeatherChart';

type MetricType = 'temperature' | 'humidity' | 'pressure' | 'wind';

export const WeatherDashboard: React.FC = () => {
  const [selectedMetric, setSelectedMetric] = useState<MetricType>('temperature');
  const [dataLimit, setDataLimit] = useState(288); // 24 hours at 5-min intervals

  const { data: weatherData, isLoading, error } = useLatestWeather(dataLimit);
  const { data: stats } = useWeatherStats();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading weather data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <p className="font-bold">Error loading weather data</p>
          <p>{error.message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            Weather Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Ambient Weather Station Data Analytics
          </p>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Records</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">
                {stats.total_records.toLocaleString()}
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Avg Temperature</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">
                {stats.avg_temperature?.toFixed(1)}°F
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Avg Humidity</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">
                {stats.avg_humidity?.toFixed(0)}%
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Date Range</p>
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {stats.min_date ? new Date(stats.min_date).toLocaleDateString() : 'N/A'}
                <br />
                to {stats.max_date ? new Date(stats.max_date).toLocaleDateString() : 'N/A'}
              </p>
            </div>
          </div>
        )}

        {/* Controls */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-8">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Metric
              </label>
              <select
                value={selectedMetric}
                onChange={(e) => setSelectedMetric(e.target.value as MetricType)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
              >
                <option value="temperature">Temperature</option>
                <option value="humidity">Humidity</option>
                <option value="pressure">Pressure</option>
                <option value="wind">Wind Speed</option>
              </select>
            </div>
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Time Range
              </label>
              <select
                value={dataLimit}
                onChange={(e) => setDataLimit(Number(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
              >
                <option value={288}>Last 24 Hours</option>
                <option value={288 * 3}>Last 3 Days</option>
                <option value={288 * 7}>Last Week</option>
                <option value={288 * 30}>Last Month</option>
              </select>
            </div>
          </div>
        </div>

        {/* Chart */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
            {selectedMetric.charAt(0).toUpperCase() + selectedMetric.slice(1)} Trend
          </h2>
          {weatherData && weatherData.length > 0 ? (
            <WeatherChart
              data={weatherData}
              metric={selectedMetric}
              height={500}
            />
          ) : (
            <p className="text-gray-600 dark:text-gray-400 text-center py-12">
              No data available for the selected time range
            </p>
          )}
        </div>
      </div>
    </div>
  );
};
