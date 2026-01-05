/**
 * Precipitation Chart Component
 *
 * Displays hourly and daily precipitation over time using Victory charts
 */

import { VictoryChart, VictoryLine, VictoryAxis, VictoryLegend } from 'victory';
import { type WeatherData } from '../../api';

interface PrecipitationChartProps {
  data: WeatherData[];
}

export default function PrecipitationChart({ data }: PrecipitationChartProps) {
  const hasData = data && data.length > 0;

  const hourlyRainData = hasData ? data.map(d => ({
    x: new Date(d.dateutc),
    y: d.hourlyrainin ?? null,
  })).filter(d => d.y !== null) : [];

  const dailyRainData = hasData ? data.map(d => ({
    x: new Date(d.dateutc),
    y: d.dailyrainin ?? null,
  })).filter(d => d.y !== null) : [];

  return (
    <div className="bg-white shadow-md rounded-lg p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Precipitation</h3>

      {!hasData || (hourlyRainData.length === 0 && dailyRainData.length === 0) ? (
        <div className="h-64 flex items-center justify-center text-gray-500">
          No data available for selected date range
        </div>
      ) : (
        <VictoryChart
          height={300}
        >
          <VictoryLegend
            x={80}
            y={10}
            orientation="horizontal"
            gutter={20}
            data={[
              { name: 'Hourly', symbol: { fill: '#0ea5e9' } },
              { name: 'Daily Total', symbol: { fill: '#8b5cf6' } },
            ]}
          />

          <VictoryAxis
            tickFormat={(t) => {
              const date = new Date(t);
              return `${date.getMonth() + 1}/${date.getDate()}`;
            }}
            style={{
              tickLabels: { fontSize: 10, padding: 5 },
            }}
          />

          <VictoryAxis
            dependentAxis
            label="Precipitation (inches)"
            style={{
              axisLabel: { fontSize: 12, padding: 35 },
              tickLabels: { fontSize: 10 },
            }}
          />

          <VictoryLine
            data={hourlyRainData}
            style={{
              data: { stroke: '#0ea5e9', strokeWidth: 2 },
            }}
          />

          <VictoryLine
            data={dailyRainData}
            style={{
              data: { stroke: '#8b5cf6', strokeWidth: 2, strokeDasharray: '4,2' },
            }}
          />
        </VictoryChart>
      )}
    </div>
  );
}
