/**
 * useMetricsLayout Hook
 *
 * Manages Current Conditions metrics ordering with localStorage persistence.
 * Allows users to customize their metrics display via drag-and-drop.
 *
 * Follows same pattern as useDashboardLayout for charts.
 */

import { useState, useEffect } from 'react';

export type MetricId =
  | 'temperature'
  | 'feelsLike'
  | 'humidity'
  | 'dewPoint'
  | 'windSpeed'
  | 'windGust'
  | 'windDirection'
  | 'pressure'
  | 'hourlyRain'
  | 'dailyRain'
  | 'solarRadiation'
  | 'uvIndex';

export const DEFAULT_METRICS_ORDER: MetricId[] = [
  'temperature',
  'feelsLike',
  'humidity',
  'dewPoint',
  'windSpeed',
  'windGust',
  'windDirection',
  'pressure',
  'hourlyRain',
  'dailyRain',
  'solarRadiation',
  'uvIndex',
];

const STORAGE_KEY = 'metrics-layout';

export function useMetricsLayout() {
  const [metricsOrder, setMetricsOrder] = useState<MetricId[]>(() => {
    // Load from localStorage on mount
    if (typeof window !== 'undefined') {
      try {
        const saved = localStorage.getItem(STORAGE_KEY);
        if (saved) {
          const parsed = JSON.parse(saved);
          // Validate that all expected metrics are present
          if (
            Array.isArray(parsed) &&
            parsed.length === DEFAULT_METRICS_ORDER.length &&
            DEFAULT_METRICS_ORDER.every((id) => parsed.includes(id))
          ) {
            return parsed;
          }
        }
      } catch (error) {
        console.error('Failed to load metrics layout from localStorage:', error);
      }
    }
    return DEFAULT_METRICS_ORDER;
  });

  useEffect(() => {
    // Persist to localStorage whenever order changes
    if (typeof window !== 'undefined') {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(metricsOrder));
      } catch (error) {
        console.error('Failed to save metrics layout to localStorage:', error);
      }
    }
  }, [metricsOrder]);

  const resetMetricsLayout = () => {
    setMetricsOrder(DEFAULT_METRICS_ORDER);
  };

  return { metricsOrder, setMetricsOrder, resetMetricsLayout };
}
