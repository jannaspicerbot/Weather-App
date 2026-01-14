/**
 * Humidity Chart Component
 *
 * Displays humidity percentage over time using Victory charts.
 * Uses semantic design tokens from design-tokens.md.
 */

import { VictoryChart, VictoryLine, VictoryAxis, VictoryContainer } from 'victory';
import { type WeatherData } from '../../api';
import { ChartCard } from './ChartCard';

interface DateRange {
  start: Date;
  end: Date;
}

interface HumidityChartProps {
  data: WeatherData[];
  dateRange?: DateRange;
}

// Chart height for compact 2x2 grid layout
const CHART_HEIGHT = 200;

export default function HumidityChart({ data, dateRange }: HumidityChartProps) {
  const hasData = data && data.length > 0;

  const humidityData = hasData
    ? data
        .map((d) => ({
          x: new Date(d.dateutc),
          y: d.humidity ?? null,
        }))
        .filter((d) => d.y !== null)
    : [];

  return (
    <ChartCard
      title="Humidity"
      colorCategory="water"
      description="Line chart showing humidity percentage over time"
    >
      {!hasData || humidityData.length === 0 ? (
        <div className="chart-card__empty">
          No data available for selected date range
        </div>
      ) : (
        <VictoryChart
          height={CHART_HEIGHT}
          padding={{ top: 15, bottom: 35, left: 50, right: 20 }}
          domain={dateRange ? { x: [dateRange.start, dateRange.end] } : undefined}
          containerComponent={
            <VictoryContainer
              title="Humidity Chart"
              desc="Line chart showing humidity percentage over time"
            />
          }
        >
          <VictoryAxis
            tickFormat={(t) => {
              const date = new Date(t);
              return `${date.getMonth() + 1}/${date.getDate()}`;
            }}
            style={{
              axis: { stroke: 'var(--color-border)' },
              grid: { stroke: 'var(--chart-grid)', strokeDasharray: '4,4' },
              tickLabels: { fontSize: 8, fill: 'var(--chart-axis)', padding: 4 },
            }}
          />

          <VictoryAxis
            dependentAxis
            label="%"
            domain={[0, 100]}
            style={{
              axis: { stroke: 'var(--color-border)' },
              grid: { stroke: 'var(--chart-grid)', strokeDasharray: '4,4' },
              axisLabel: { fontSize: 9, fill: 'var(--chart-axis)', padding: 30 },
              tickLabels: { fontSize: 8, fill: 'var(--chart-axis)' },
            }}
          />

          <VictoryLine
            data={humidityData}
            style={{
              data: { stroke: 'var(--color-water)', strokeWidth: 2 },
            }}
          />
        </VictoryChart>
      )}
    </ChartCard>
  );
}
