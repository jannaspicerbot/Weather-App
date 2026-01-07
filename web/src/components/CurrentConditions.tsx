/**
 * Current Conditions Display Component
 *
 * Shows the latest weather reading with all available metrics.
 * Follows design system from docs/design/dashboard-layout.md and docs/design/design-tokens.md
 *
 * Layout: Responsive masonry grid
 * - Desktop (≥1024px): 6 columns
 * - Tablet (768-1023px): 4 columns
 * - Mobile (<768px): 2 columns
 */

import { type WeatherData } from '../api';
import { MetricCard } from './MetricCard';

interface CurrentConditionsProps {
  weather: WeatherData;
}

type ColorCategory = 'water' | 'growth' | 'interactive';

interface MetricConfig {
  label: string;
  value: string;
  icon: string;
  colorCategory: ColorCategory;
  description?: string;
}

export default function CurrentConditions({ weather }: CurrentConditionsProps) {
  const formatValue = (
    value: number | null | undefined,
    unit: string,
    decimals: number = 1
  ): string => {
    if (value == null) return 'N/A';
    return `${value.toFixed(decimals)}${unit}`;
  };

  // Metrics organized by semantic color categories per design-tokens.md:
  // - water: Temperature, rain, humidity (blue family)
  // - growth: Wind, air quality, nature metrics (green family)
  // - interactive: Special/highlighted metrics (accent color)
  const metrics: MetricConfig[] = [
    {
      label: 'Temperature',
      value: formatValue(weather.tempf, '°F'),
      icon: '🌡️',
      colorCategory: 'water',
      description: 'Current outdoor temperature',
    },
    {
      label: 'Feels Like',
      value: formatValue(weather.feelsLike, '°F'),
      icon: '🌡️',
      colorCategory: 'water',
      description: 'Apparent temperature accounting for wind and humidity',
    },
    {
      label: 'Humidity',
      value: formatValue(weather.humidity, '%', 0),
      icon: '💧',
      colorCategory: 'water',
      description: 'Relative humidity percentage',
    },
    {
      label: 'Dew Point',
      value: formatValue(weather.dewPoint, '°F'),
      icon: '💧',
      colorCategory: 'water',
      description: 'Temperature at which dew forms',
    },
    {
      label: 'Wind Speed',
      value: formatValue(weather.windspeedmph, ' mph'),
      icon: '💨',
      colorCategory: 'growth',
      description: 'Current wind speed',
    },
    {
      label: 'Wind Gust',
      value: formatValue(weather.windgustmph, ' mph'),
      icon: '💨',
      colorCategory: 'growth',
      description: 'Maximum wind gust speed',
    },
    {
      label: 'Wind Direction',
      value: weather.winddir != null ? `${weather.winddir}°` : 'N/A',
      icon: '🧭',
      colorCategory: 'growth',
      description: 'Wind direction in degrees',
    },
    {
      label: 'Pressure',
      value: formatValue(weather.baromrelin, ' inHg', 2),
      icon: '⏱️',
      colorCategory: 'interactive',
      description: 'Barometric pressure',
    },
    {
      label: 'Hourly Rain',
      value: formatValue(weather.hourlyrainin, ' in', 2),
      icon: '🌧️',
      colorCategory: 'water',
      description: 'Rainfall in the past hour',
    },
    {
      label: 'Daily Rain',
      value: formatValue(weather.dailyrainin, ' in', 2),
      icon: '🌧️',
      colorCategory: 'water',
      description: 'Total rainfall today',
    },
    {
      label: 'Solar Radiation',
      value: formatValue(weather.solarradiation, ' W/m²', 0),
      icon: '☀️',
      colorCategory: 'interactive',
      description: 'Solar radiation intensity',
    },
    {
      label: 'UV Index',
      value: weather.uv != null ? weather.uv.toString() : 'N/A',
      icon: '☀️',
      colorCategory: 'interactive',
      description: 'Ultraviolet radiation index',
    },
  ];

  // Format the date for display
  const formatDate = (dateStr: string): string => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleString(undefined, {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
      });
    } catch {
      return dateStr;
    }
  };

  return (
    <section
      className="current-conditions"
      aria-labelledby="current-conditions-heading"
    >
      <header className="current-conditions__header">
        <h2
          id="current-conditions-heading"
          className="current-conditions__title"
        >
          Current Conditions
        </h2>
        <time
          className="current-conditions__timestamp"
          dateTime={weather.date}
        >
          {formatDate(weather.date)}
        </time>
      </header>

      <div
        className="current-conditions__grid"
        role="list"
        aria-label="Weather metrics"
      >
        {metrics.map((metric) => (
          <div key={metric.label} role="listitem">
            <MetricCard
              label={metric.label}
              value={metric.value}
              icon={metric.icon}
              colorCategory={metric.colorCategory}
              description={metric.description}
            />
          </div>
        ))}
      </div>
    </section>
  );
}
