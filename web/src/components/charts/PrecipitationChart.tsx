/**
 * Precipitation Chart Component
 *
 * Displays hourly and daily precipitation over time using Victory charts.
 * Uses semantic design tokens from design-tokens.md.
 */

import {
  VictoryChart,
  VictoryLine,
  VictoryAxis,
  VictoryLegend,
  VictoryContainer,
} from 'victory';
import { type WeatherData } from '../../api';
import { ChartCard } from './ChartCard';

interface DateRange {
  start: Date;
  end: Date;
}

interface PrecipitationChartProps {
  data: WeatherData[];
  dateRange?: DateRange;
}

// Chart height for compact 2x2 grid layout
const CHART_HEIGHT = 200;

export default function PrecipitationChart({ data, dateRange }: PrecipitationChartProps) {
  const hasData = data && data.length > 0;

  const hourlyRainData = hasData
    ? data
        .map((d) => ({
          x: new Date(d.dateutc),
          y: d.hourlyrainin ?? null,
        }))
        .filter((d) => d.y !== null)
    : [];

  const dailyRainData = hasData
    ? data
        .map((d) => ({
          x: new Date(d.dateutc),
          y: d.dailyrainin ?? null,
        }))
        .filter((d) => d.y !== null)
    : [];

  return (
    <ChartCard
      title="Precipitation"
      colorCategory="water"
      description="Line chart showing hourly and daily precipitation over time"
    >
      {!hasData || (hourlyRainData.length === 0 && dailyRainData.length === 0) ? (
        <div className="chart-card__empty">
          No data available for selected date range
        </div>
      ) : (
        <VictoryChart
          height={CHART_HEIGHT}
          padding={{ top: 30, bottom: 35, left: 50, right: 20 }}
          domain={dateRange ? { x: [dateRange.start, dateRange.end] } : undefined}
          containerComponent={
            <VictoryContainer
              title="Precipitation Chart"
              desc="Line chart showing hourly and daily precipitation over time"
            />
          }
        >
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
              { name: 'Hourly', symbol: { fill: 'var(--color-water)' } },
              { name: 'Daily', symbol: { fill: 'var(--color-interactive)' } },
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
            label="in"
            style={{
              axis: { stroke: 'var(--color-border)' },
              grid: { stroke: 'var(--chart-grid)', strokeDasharray: '4,4' },
              axisLabel: { fontSize: 9, fill: 'var(--chart-axis)', padding: 30 },
              tickLabels: { fontSize: 8, fill: 'var(--chart-axis)' },
            }}
          />

          <VictoryLine
            data={hourlyRainData}
            style={{
              data: { stroke: 'var(--color-water)', strokeWidth: 2 },
            }}
          />

          <VictoryLine
            data={dailyRainData}
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
