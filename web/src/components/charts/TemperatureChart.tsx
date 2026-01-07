/**
 * Temperature Chart Component
 *
 * Displays temperature and feels-like temperature over time using Victory charts.
 * Uses semantic design tokens from design-tokens.md.
 */

import { VictoryChart, VictoryLine, VictoryAxis, VictoryLegend } from 'victory';
import { type WeatherData } from '../../api';
import { ChartCard } from './ChartCard';

interface TemperatureChartProps {
  data: WeatherData[];
}

// Chart height for compact 2x2 grid layout
const CHART_HEIGHT = 200;

export default function TemperatureChart({ data }: TemperatureChartProps) {
  const hasData = data && data.length > 0;

  const temperatureData = hasData
    ? data
        .map((d) => ({
          x: new Date(d.dateutc),
          y: d.tempf ?? null,
        }))
        .filter((d) => d.y !== null)
    : [];

  const feelsLikeData = hasData
    ? data
        .map((d) => ({
          x: new Date(d.dateutc),
          y: d.feelsLike ?? null,
        }))
        .filter((d) => d.y !== null)
    : [];

  return (
    <ChartCard
      title="Temperature"
      colorCategory="water"
      description="Line chart showing temperature and feels-like temperature over time"
    >
      {!hasData || temperatureData.length === 0 ? (
        <div className="chart-card__empty">
          No data available for selected date range
        </div>
      ) : (
        <VictoryChart height={CHART_HEIGHT} padding={{ top: 30, bottom: 35, left: 50, right: 20 }}>
          <VictoryLegend
            x={60}
            y={0}
            orientation="horizontal"
            gutter={15}
            symbolSpacer={5}
            style={{
              labels: { fontSize: 9, fill: 'var(--color-text-secondary)' },
            }}
            data={[
              { name: 'Temperature', symbol: { fill: 'var(--color-water)' } },
              { name: 'Feels Like', symbol: { fill: 'var(--color-interactive)' } },
            ]}
          />

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
            label="°F"
            style={{
              axis: { stroke: 'var(--color-border)' },
              grid: { stroke: 'var(--chart-grid)', strokeDasharray: '4,4' },
              axisLabel: { fontSize: 9, fill: 'var(--chart-axis)', padding: 30 },
              tickLabels: { fontSize: 8, fill: 'var(--chart-axis)' },
            }}
          />

          <VictoryLine
            data={temperatureData}
            style={{
              data: { stroke: 'var(--color-water)', strokeWidth: 2 },
            }}
          />

          <VictoryLine
            data={feelsLikeData}
            style={{
              data: {
                stroke: 'var(--color-interactive)',
                strokeWidth: 2,
                strokeDasharray: '4,2',
              },
            }}
          />
        </VictoryChart>
      )}
    </ChartCard>
  );
}
