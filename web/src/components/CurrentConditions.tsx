/**
 * Current Conditions Display Component
 *
 * Shows the latest weather reading with all available metrics.
 * Follows design system from docs/design/dashboard-layout.md and docs/design/design-tokens.md
 *
 * Features:
 * - Drag-and-drop reordering of metric cards (dnd-kit)
 * - Responsive masonry grid layout
 * - WCAG 2.2 AA accessibility (keyboard nav, screen reader announcements)
 * - localStorage persistence of user's preferred order
 *
 * Layout: Responsive masonry grid
 * - Desktop (≥1024px): 6 columns
 * - Tablet (768-1023px): 4 columns
 * - Mobile (<768px): 2 columns
 */

import { type WeatherData } from '../api';
import { MetricCard } from './MetricCard';
import { MetricsGrid } from './dashboard/MetricsGrid';
import { SortableMetricCard } from './dashboard/SortableMetricCard';
import { type MetricId } from '../hooks/useMetricsLayout';

interface CurrentConditionsProps {
  weather: WeatherData;
  metricsOrder: MetricId[];
  onMetricsReorder: (newOrder: MetricId[]) => void;
}

type ColorCategory = 'water' | 'growth' | 'interactive';

interface MetricConfig {
  label: string;
  value: string;
  icon: string;
  colorCategory: ColorCategory;
  description?: string;
}

export default function CurrentConditions({
  weather,
  metricsOrder,
  onMetricsReorder,
}: CurrentConditionsProps) {
  const formatValue = (
    value: number | null | undefined,
    unit: string,
    decimals: number = 1
  ): string => {
    if (value == null) return 'N/A';
    return `${value.toFixed(decimals)}${unit}`;
  };

  // Metrics configuration map - keyed by MetricId for easy lookup
  // Colors organized by semantic categories per design-tokens.md:
  // - water: Temperature, rain, humidity (blue family)
  // - growth: Wind, air quality, nature metrics (green family)
  // - interactive: Special/highlighted metrics (accent color)
  const metricsConfig: Record<MetricId, MetricConfig> = {
    temperature: {
      label: 'Temperature',
      value: formatValue(weather.tempf, '°F'),
      icon: '🌡️',
      colorCategory: 'water',
      description: 'Current outdoor temperature',
    },
    feelsLike: {
      label: 'Feels Like',
      value: formatValue(weather.feelsLike, '°F'),
      icon: '🌡️',
      colorCategory: 'water',
      description: 'Apparent temperature accounting for wind and humidity',
    },
    humidity: {
      label: 'Humidity',
      value: formatValue(weather.humidity, '%', 0),
      icon: '💧',
      colorCategory: 'water',
      description: 'Relative humidity percentage',
    },
    dewPoint: {
      label: 'Dew Point',
      value: formatValue(weather.dewPoint, '°F'),
      icon: '💧',
      colorCategory: 'water',
      description: 'Temperature at which dew forms',
    },
    windSpeed: {
      label: 'Wind Speed',
      value: formatValue(weather.windspeedmph, ' mph'),
      icon: '💨',
      colorCategory: 'growth',
      description: 'Current wind speed',
    },
    windGust: {
      label: 'Wind Gust',
      value: formatValue(weather.windgustmph, ' mph'),
      icon: '💨',
      colorCategory: 'growth',
      description: 'Maximum wind gust speed',
    },
    windDirection: {
      label: 'Wind Direction',
      value: weather.winddir != null ? `${weather.winddir}°` : 'N/A',
      icon: '🧭',
      colorCategory: 'growth',
      description: 'Wind direction in degrees',
    },
    pressure: {
      label: 'Pressure',
      value: formatValue(weather.baromrelin, ' inHg', 2),
      icon: '⏱️',
      colorCategory: 'interactive',
      description: 'Barometric pressure',
    },
    hourlyRain: {
      label: 'Hourly Rain',
      value: formatValue(weather.hourlyrainin, ' in', 2),
      icon: '🌧️',
      colorCategory: 'water',
      description: 'Rainfall in the past hour',
    },
    dailyRain: {
      label: 'Daily Rain',
      value: formatValue(weather.dailyrainin, ' in', 2),
      icon: '🌧️',
      colorCategory: 'water',
      description: 'Total rainfall today',
    },
    solarRadiation: {
      label: 'Solar Radiation',
      value: formatValue(weather.solarradiation, ' W/m²', 0),
      icon: '☀️',
      colorCategory: 'interactive',
      description: 'Solar radiation intensity',
    },
    uvIndex: {
      label: 'UV Index',
      value: weather.uv != null ? weather.uv.toString() : 'N/A',
      icon: '☀️',
      colorCategory: 'interactive',
      description: 'Ultraviolet radiation index',
    },
  };

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

      <MetricsGrid metricsOrder={metricsOrder} onReorder={onMetricsReorder}>
        {metricsOrder.map((metricId) => {
          const config = metricsConfig[metricId];
          return (
            <SortableMetricCard key={metricId} id={metricId}>
              <MetricCard
                label={config.label}
                value={config.value}
                icon={config.icon}
                colorCategory={config.colorCategory}
                description={config.description}
              />
            </SortableMetricCard>
          );
        })}
      </MetricsGrid>

      {/* Compact instructions for reordering */}
      <details className="metrics-instructions">
        <summary className="metrics-instructions__toggle">
          Reorder metrics
        </summary>
        <div className="metrics-instructions__content">
          <p><strong>Mouse:</strong> Drag cards to reorder</p>
          <p><strong>Touch:</strong> Long-press and drag</p>
          <p><strong>Keyboard:</strong> Tab to card, Enter, Arrow keys, Enter</p>
        </div>
      </details>
    </section>
  );
}
