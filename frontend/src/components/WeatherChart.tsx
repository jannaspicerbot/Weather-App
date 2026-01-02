/**
 * Weather Chart Component
 * Displays temperature and humidity data using Recharts
 */

import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { format } from 'date-fns';
import type { WeatherReading } from '../types/weather';

interface WeatherChartProps {
  data: WeatherReading[];
  metric?: 'temperature' | 'humidity' | 'pressure' | 'wind';
  height?: number;
}

export const WeatherChart: React.FC<WeatherChartProps> = ({
  data,
  metric = 'temperature',
  height = 400,
}) => {
  // Transform data for chart
  const chartData = data.map((reading) => ({
    timestamp: reading.dateutc,
    date: format(new Date(reading.dateutc * 1000), 'MM/dd HH:mm'),
    temperature: reading.tempf,
    humidity: reading.humidity,
    pressure: reading.baromrelin,
    windSpeed: reading.windspeedmph,
  }));

  const getMetricConfig = () => {
    switch (metric) {
      case 'temperature':
        return {
          dataKey: 'temperature',
          name: 'Temperature (°F)',
          stroke: '#ef4444',
          unit: '°F',
        };
      case 'humidity':
        return {
          dataKey: 'humidity',
          name: 'Humidity (%)',
          stroke: '#3b82f6',
          unit: '%',
        };
      case 'pressure':
        return {
          dataKey: 'pressure',
          name: 'Pressure (inHg)',
          stroke: '#8b5cf6',
          unit: ' inHg',
        };
      case 'wind':
        return {
          dataKey: 'windSpeed',
          name: 'Wind Speed (mph)',
          stroke: '#10b981',
          unit: ' mph',
        };
      default:
        return {
          dataKey: 'temperature',
          name: 'Temperature (°F)',
          stroke: '#ef4444',
          unit: '°F',
        };
    }
  };

  const config = getMetricConfig();

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart
        data={chartData}
        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" className="stroke-gray-300 dark:stroke-gray-700" />
        <XAxis
          dataKey="date"
          className="text-sm"
          tick={{ fill: 'currentColor' }}
        />
        <YAxis
          className="text-sm"
          tick={{ fill: 'currentColor' }}
          label={{ value: config.name, angle: -90, position: 'insideLeft' }}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            border: '1px solid #e5e7eb',
            borderRadius: '0.5rem',
          }}
          formatter={(value: number) => `${value?.toFixed(1)}${config.unit}`}
        />
        <Legend />
        <Line
          type="monotone"
          dataKey={config.dataKey}
          stroke={config.stroke}
          name={config.name}
          dot={false}
          strokeWidth={2}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};
