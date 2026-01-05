/**
 * Wind Chart Component
 *
 * Displays wind speed and gusts over time using Victory charts
 */

import { VictoryChart, VictoryLine, VictoryAxis, VictoryLegend } from 'victory';
import { type WeatherData } from '../../api';

interface WindChartProps {
  data: WeatherData[];
}

export default function WindChart({ data }: WindChartProps) {
  const hasData = data && data.length > 0;

  const windSpeedData = hasData ? data.map(d => ({
    x: new Date(d.dateutc),
    y: d.windspeedmph ?? null,
  })).filter(d => d.y !== null) : [];

  const windGustData = hasData ? data.map(d => ({
    x: new Date(d.dateutc),
    y: d.windgustmph ?? null,
  })).filter(d => d.y !== null) : [];

  return (
    <div className="bg-white shadow-md rounded-lg p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Wind</h3>

      {!hasData || (windSpeedData.length === 0 && windGustData.length === 0) ? (
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
              { name: 'Speed', symbol: { fill: '#10b981' } },
              { name: 'Gusts', symbol: { fill: '#6366f1' } },
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
            label="Wind Speed (mph)"
            style={{
              axisLabel: { fontSize: 12, padding: 35 },
              tickLabels: { fontSize: 10 },
            }}
          />

          <VictoryLine
            data={windSpeedData}
            style={{
              data: { stroke: '#10b981', strokeWidth: 2 },
            }}
          />

          <VictoryLine
            data={windGustData}
            style={{
              data: { stroke: '#6366f1', strokeWidth: 2, strokeDasharray: '4,2' },
            }}
          />
        </VictoryChart>
      )}
    </div>
  );
}
