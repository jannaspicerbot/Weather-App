/**
 * Temperature Chart Component
 *
 * Displays temperature and feels-like temperature over time using Victory charts
 */

import { VictoryChart, VictoryLine, VictoryAxis, VictoryLegend, VictoryTooltip, VictoryVoronoiContainer } from 'victory';
import { type WeatherData } from '../../api';

interface TemperatureChartProps {
  data: WeatherData[];
}

export default function TemperatureChart({ data }: TemperatureChartProps) {
  const hasData = data && data.length > 0;

  const temperatureData = hasData ? data.map(d => ({
    x: new Date(d.dateutc),
    y: d.tempf ?? null,
  })).filter(d => d.y !== null) : [];

  const feelsLikeData = hasData ? data.map(d => ({
    x: new Date(d.dateutc),
    y: d.feelsLike ?? null,
  })).filter(d => d.y !== null) : [];

  return (
    <div className="bg-white shadow-md rounded-lg p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Temperature</h3>

      {!hasData || temperatureData.length === 0 ? (
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
              { name: 'Temperature', symbol: { fill: '#ef4444' } },
              { name: 'Feels Like', symbol: { fill: '#f97316' } },
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
            label="Temperature (°F)"
            style={{
              axisLabel: { fontSize: 12, padding: 35 },
              tickLabels: { fontSize: 10 },
            }}
          />

          <VictoryLine
            data={temperatureData}
            style={{
              data: { stroke: '#ef4444', strokeWidth: 2 },
            }}
          />

          <VictoryLine
            data={feelsLikeData}
            style={{
              data: { stroke: '#f97316', strokeWidth: 2, strokeDasharray: '4,2' },
            }}
          />
        </VictoryChart>
      )}
    </div>
  );
}
