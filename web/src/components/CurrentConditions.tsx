/**
 * Current Conditions Display Component
 *
 * Shows the latest weather reading with all available metrics
 */

import { type WeatherData } from '../api';

interface CurrentConditionsProps {
  weather: WeatherData;
}

export default function CurrentConditions({ weather }: CurrentConditionsProps) {
  const formatValue = (value: number | null | undefined, unit: string, decimals: number = 1): string => {
    if (value == null) return 'N/A';
    return `${value.toFixed(decimals)}${unit}`;
  };

  const metrics = [
    {
      label: 'Temperature',
      value: formatValue(weather.tempf, '°F'),
      icon: '🌡️',
    },
    {
      label: 'Feels Like',
      value: formatValue(weather.feelsLike, '°F'),
      icon: '🌡️',
    },
    {
      label: 'Humidity',
      value: formatValue(weather.humidity, '%', 0),
      icon: '💧',
    },
    {
      label: 'Dew Point',
      value: formatValue(weather.dewPoint, '°F'),
      icon: '💧',
    },
    {
      label: 'Wind Speed',
      value: formatValue(weather.windspeedmph, ' mph'),
      icon: '💨',
    },
    {
      label: 'Wind Gust',
      value: formatValue(weather.windgustmph, ' mph'),
      icon: '💨',
    },
    {
      label: 'Wind Direction',
      value: weather.winddir != null ? `${weather.winddir}°` : 'N/A',
      icon: '🧭',
    },
    {
      label: 'Pressure',
      value: formatValue(weather.baromrelin, ' inHg', 2),
      icon: '⏱️',
    },
    {
      label: 'Hourly Rain',
      value: formatValue(weather.hourlyrainin, ' in', 2),
      icon: '🌧️',
    },
    {
      label: 'Daily Rain',
      value: formatValue(weather.dailyrainin, ' in', 2),
      icon: '🌧️',
    },
    {
      label: 'Solar Radiation',
      value: formatValue(weather.solarradiation, ' W/m²', 0),
      icon: '☀️',
    },
    {
      label: 'UV Index',
      value: weather.uv != null ? weather.uv.toString() : 'N/A',
      icon: '☀️',
    },
  ];

  return (
    <div className="bg-white shadow-md rounded-lg p-6 mb-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-semibold text-gray-900">Current Conditions</h2>
        <p className="text-sm text-gray-600">{weather.date}</p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
        {metrics.map((metric) => (
          <div key={metric.label} className="text-center">
            <div className="text-2xl mb-1">{metric.icon}</div>
            <p className="text-xs text-gray-600 mb-1">{metric.label}</p>
            <p className="text-lg font-semibold text-gray-900">{metric.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
