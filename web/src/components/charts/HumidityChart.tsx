/**
 * Humidity Chart Component
 *
 * Displays humidity percentage over time using Victory charts
 */

import { VictoryChart, VictoryLine, VictoryAxis } from 'victory';
import { type WeatherData } from '../../api';

interface HumidityChartProps {
  data: WeatherData[];
}

export default function HumidityChart({ data }: HumidityChartProps) {
  const hasData = data && data.length > 0;

  const humidityData = hasData ? data.map(d => ({
    x: new Date(d.dateutc),
    y: d.humidity ?? null,
  })).filter(d => d.y !== null) : [];

  return (
    <div className="bg-white shadow-md rounded-lg p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Humidity</h3>

      {!hasData || humidityData.length === 0 ? (
        <div className="h-64 flex items-center justify-center text-gray-500">
          No data available for selected date range
        </div>
      ) : (
        <VictoryChart
          height={300}
        >
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
            label="Humidity (%)"
            domain={[0, 100]}
            style={{
              axisLabel: { fontSize: 12, padding: 35 },
              tickLabels: { fontSize: 10 },
            }}
          />

          <VictoryLine
            data={humidityData}
            style={{
              data: { stroke: '#3b82f6', strokeWidth: 2 },
            }}
          />
        </VictoryChart>
      )}
    </div>
  );
}
