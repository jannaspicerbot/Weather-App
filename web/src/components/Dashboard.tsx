/**
 * Main Weather Dashboard Component
 *
 * Displays current conditions and historical charts for weather data
 */

import { useEffect, useState } from 'react';
import { DefaultService, type WeatherData, type DatabaseStats } from '../api';
import CurrentConditions from './CurrentConditions';
import TemperatureChart from './charts/TemperatureChart';
import HumidityChart from './charts/HumidityChart';
import WindChart from './charts/WindChart';
import PrecipitationChart from './charts/PrecipitationChart';
import DateRangeSelector from './DateRangeSelector';
import { DashboardGrid } from './dashboard/DashboardGrid';
import { SortableChartCard } from './dashboard/SortableChartCard';
import { useDashboardLayout } from '../hooks/useDashboardLayout';
import { useMetricsLayout } from '../hooks/useMetricsLayout';

export default function Dashboard() {
  const [latestWeather, setLatestWeather] = useState<WeatherData | null>(null);
  const [stats, setStats] = useState<DatabaseStats | null>(null);
  const [historicalData, setHistoricalData] = useState<WeatherData[]>([]);
  const [dateRange, setDateRange] = useState<{ start: Date; end: Date }>({
    start: new Date(Date.now() - 24 * 60 * 60 * 1000), // Last 24 hours
    end: new Date(),
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { chartOrder, setChartOrder, resetLayout } = useDashboardLayout();
  const { metricsOrder, setMetricsOrder, resetMetricsLayout } = useMetricsLayout();

  // Reset both chart and metrics layouts
  const handleResetAllLayouts = () => {
    resetLayout();
    resetMetricsLayout();
  };

  useEffect(() => {
    fetchLatestData();
    const interval = setInterval(fetchLatestData, 5 * 60 * 1000); // Refresh every 5 minutes
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    fetchHistoricalData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dateRange]);

  const fetchLatestData = async () => {
    try {
      const dbStats = await DefaultService.getDatabaseStatsWeatherStatsGet();
      setStats(dbStats);

      // Only fetch latest weather if database has records
      if (dbStats.total_records > 0) {
        const weather = await DefaultService.getLatestWeatherWeatherLatestGet();
        setLatestWeather(weather);
      } else {
        setLatestWeather(null);
      }

      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch latest data');
      console.error('Failed to fetch latest data:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchHistoricalData = async () => {
    try {
      const startDateStr = dateRange.start.toISOString().split('T')[0];
      const endDateStr = dateRange.end.toISOString().split('T')[0];

      // Calculate number of days in range
      const daysDiff = Math.ceil((dateRange.end.getTime() - dateRange.start.getTime()) / (1000 * 60 * 60 * 24));

      // Ambient Weather records every 5 minutes = ~288 records/day
      // Use pagination to fetch data in chunks and sample evenly
      const recordsPerDay = 288;
      const estimatedTotal = daysDiff * recordsPerDay;
      const targetPoints = 1000; // Target number of points for charts

      if (estimatedTotal <= targetPoints) {
        // Small range - fetch all data
        const data = await DefaultService.getWeatherDataWeatherGet(
          1000,
          undefined,
          startDateStr,
          endDateStr,
          'asc'
        );
        setHistoricalData(data);
      } else {
        // Large range - fetch data with strategic sampling
        // Fetch multiple pages with offsets to get evenly distributed samples
        const pages = Math.min(Math.ceil(targetPoints / 200), 5); // Max 5 API calls
        const recordsPerPage = Math.floor(targetPoints / pages);

        const allData: typeof historicalData = [];
        for (let i = 0; i < pages; i++) {
          const offset = Math.floor((estimatedTotal / pages) * i);
          const pageData = await DefaultService.getWeatherDataWeatherGet(
            recordsPerPage,
            offset,
            startDateStr,
            endDateStr,
            'asc'
          );
          allData.push(...pageData);
        }

        setHistoricalData(allData);
      }
    } catch (err) {
      console.error('Failed to fetch historical data:', err);
      setHistoricalData([]);
    }
  };

  const handleDateRangeChange = (start: Date, end: Date) => {
    setDateRange({ start, end });
  };

  const handleExportCSV = async () => {
    try {
      // Generate CSV from current historical data
      if (historicalData.length === 0) {
        alert('No data to export');
        return;
      }

      const headers = ['Date', 'Temperature (°F)', 'Feels Like (°F)', 'Humidity (%)', 'Wind Speed (mph)', 'Wind Gust (mph)', 'Hourly Rain (in)', 'Daily Rain (in)'];
      const csvRows = [headers.join(',')];

      historicalData.forEach(reading => {
        const row = [
          reading.date,
          reading.tempf ?? '',
          reading.feelsLike ?? '',
          reading.humidity ?? '',
          reading.windspeedmph ?? '',
          reading.windgustmph ?? '',
          reading.hourlyrainin ?? '',
          reading.dailyrainin ?? '',
        ];
        csvRows.push(row.join(','));
      });

      const csvContent = csvRows.join('\n');
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `weather_data_${dateRange.start.toISOString().split('T')[0]}_to_${dateRange.end.toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to export CSV:', err);
      alert('Failed to export CSV');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600 text-lg">Loading weather data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-red-600 text-lg">Error: {error}</div>
      </div>
    );
  }

  // Chart component mapping
  const chartComponents = {
    temperature: <TemperatureChart data={historicalData} />,
    humidity: <HumidityChart data={historicalData} />,
    wind: <WindChart data={historicalData} />,
    precipitation: <PrecipitationChart data={historicalData} />,
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Weather Dashboard</h1>
            {stats && (
              <p className="text-sm text-gray-600 mt-1">
                {stats.total_records.toLocaleString()} readings •
                {stats.date_range_days ? ` ${stats.date_range_days} days` : ' No data'}
              </p>
            )}
          </div>
          <button
            onClick={handleResetAllLayouts}
            className="px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 min-h-[44px] min-w-[44px]"
            aria-label="Reset dashboard layout to default order"
          >
            Reset Layout
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        {/* Empty State */}
        {stats && stats.total_records === 0 && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-6">
            <h2 className="text-lg font-semibold text-yellow-900 mb-2">No Weather Data Yet</h2>
            <p className="text-yellow-800 mb-4">
              The database is empty. To populate it with weather data, run one of these commands:
            </p>
            <div className="bg-yellow-100 rounded p-3 font-mono text-sm text-yellow-900">
              <div>weather-app fetch</div>
              <div className="text-xs text-yellow-700 mt-1">or</div>
              <div>weather-app backfill --start 2026-01-01 --end 2026-01-04</div>
            </div>
          </div>
        )}

        {/* Current Conditions */}
        {latestWeather && (
          <CurrentConditions
            weather={latestWeather}
            metricsOrder={metricsOrder}
            onMetricsReorder={setMetricsOrder}
          />
        )}

        {/* Date Range Selector */}
        <DateRangeSelector
          start={dateRange.start}
          end={dateRange.end}
          onChange={handleDateRangeChange}
          onExport={handleExportCSV}
        />

        {/* Charts Grid with Drag-and-Drop */}
        <DashboardGrid chartOrder={chartOrder} onReorder={setChartOrder}>
          {chartOrder.map((chartId) => (
            <SortableChartCard key={chartId} id={chartId}>
              {chartComponents[chartId]}
            </SortableChartCard>
          ))}
        </DashboardGrid>
      </main>
    </div>
  );
}
