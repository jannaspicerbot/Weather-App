/**
 * Historical Conditions Component
 *
 * Wraps the date range selector and historical charts in a unified card
 * Provides a consistent visual structure matching the Current Conditions section
 */

import { type WeatherData } from '../api';
import { type ChartId } from '../hooks/useDashboardLayout';
import DateRangeSelector from './DateRangeSelector';
import TemperatureChart from './charts/TemperatureChart';
import HumidityChart from './charts/HumidityChart';
import WindChart from './charts/WindChart';
import PrecipitationChart from './charts/PrecipitationChart';
import { DashboardGrid } from './dashboard/DashboardGrid';
import { SortableChartCard } from './dashboard/SortableChartCard';

interface HistoricalConditionsProps {
  dateRange: { start: Date; end: Date };
  historicalData: WeatherData[];
  chartOrder: ChartId[];
  onDateRangeChange: (start: Date, end: Date) => void;
  onExportCSV: () => void;
  onChartReorder: (newOrder: ChartId[]) => void;
}

export default function HistoricalConditions({
  dateRange,
  historicalData,
  chartOrder,
  onDateRangeChange,
  onExportCSV,
  onChartReorder,
}: HistoricalConditionsProps) {
  // Chart component mapping
  const chartComponents: Record<ChartId, React.ReactElement> = {
    temperature: <TemperatureChart data={historicalData} />,
    humidity: <HumidityChart data={historicalData} />,
    wind: <WindChart data={historicalData} />,
    precipitation: <PrecipitationChart data={historicalData} />,
  };

  return (
    <div className="historical-conditions">
      {/* Header */}
      <div className="historical-conditions__header">
        <h2 className="historical-conditions__title">Historical Conditions</h2>
      </div>

      {/* Date Range Selector */}
      <DateRangeSelector
        start={dateRange.start}
        end={dateRange.end}
        onChange={onDateRangeChange}
        onExport={onExportCSV}
      />

      {/* Charts Grid with Drag-and-Drop */}
      <DashboardGrid chartOrder={chartOrder} onReorder={onChartReorder}>
        {chartOrder.map((chartId) => (
          <SortableChartCard key={chartId} id={chartId}>
            {chartComponents[chartId]}
          </SortableChartCard>
        ))}
      </DashboardGrid>
    </div>
  );
}
