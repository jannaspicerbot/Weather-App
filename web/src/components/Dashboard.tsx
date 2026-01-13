/**
 * Main Weather Dashboard Component
 *
 * Displays current conditions and historical charts for weather data.
 * Includes onboarding flow for new users without configured credentials.
 */

import { useEffect, useState, useCallback } from 'react';
import { DefaultService, type WeatherData, type DatabaseStats } from '../api';
import CurrentConditions from './CurrentConditions';
import HistoricalConditions from './HistoricalConditions';
import { useDashboardLayout } from '../hooks/useDashboardLayout';
import { useMetricsLayout } from '../hooks/useMetricsLayout';
import { InstallPrompt } from './InstallPrompt';
import { OnboardingFlow } from './onboarding';
import BackfillStatusBanner from './BackfillStatusBanner';
import DeviceManager from './DeviceManager';
import { getCredentialStatus, getBackfillProgress } from '../services/onboardingApi';

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

  // Onboarding state
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [checkingCredentials, setCheckingCredentials] = useState(true);
  const [isBackfilling, setIsBackfilling] = useState(false);

  // Reset both chart and metrics layouts
  const handleResetAllLayouts = () => {
    resetLayout();
    resetMetricsLayout();
  };

  // Check credentials and backfill status on mount
  useEffect(() => {
    const checkSetup = async () => {
      try {
        // Check if credentials are configured
        const credStatus = await getCredentialStatus();

        if (!credStatus.configured) {
          // No credentials - show onboarding
          setShowOnboarding(true);
          setCheckingCredentials(false);
          setLoading(false);
          return;
        }

        // Credentials exist - check if backfill is running
        const backfillStatus = await getBackfillProgress();
        if (backfillStatus.status === 'in_progress') {
          setIsBackfilling(true);
        }

        // Continue to load dashboard data
        setCheckingCredentials(false);
      } catch (err) {
        // If check fails, assume we need onboarding
        console.error('Failed to check setup status:', err);
        setCheckingCredentials(false);
      }
    };

    checkSetup();
  }, []);

  // Handle onboarding completion
  const handleOnboardingComplete = useCallback(() => {
    setShowOnboarding(false);
    setIsBackfilling(true);
    // Trigger data fetch
    fetchLatestData();
    fetchHistoricalData();
  }, []);

  useEffect(() => {
    if (!showOnboarding && !checkingCredentials) {
      fetchLatestData();
      const interval = setInterval(fetchLatestData, 5 * 60 * 1000); // Refresh every 5 minutes
      return () => clearInterval(interval);
    }
  }, [showOnboarding, checkingCredentials]);

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

  // Show loading while checking credentials
  if (checkingCredentials) {
    return (
      <div className="dashboard__loading">
        <div className="dashboard__loading-content">
          <svg
            className="dashboard__loading-spinner"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <circle
              opacity="0.25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              opacity="0.75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          <p className="dashboard__loading-text">Checking configuration...</p>
        </div>
      </div>
    );
  }

  // Show onboarding flow for new users
  if (showOnboarding) {
    return (
      <div className="dashboard__loading" style={{ padding: 'var(--spacing-4)' }}>
        <OnboardingFlow onComplete={handleOnboardingComplete} />
      </div>
    );
  }

  if (loading && !isBackfilling) {
    return (
      <div className="dashboard__loading">
        <p className="dashboard__loading-text">Loading weather data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard__error">
        <p className="dashboard__error-text">Error: {error}</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="dashboard__header">
        <div className="dashboard__header-content">
          <div>
            <h1 className="dashboard__title">Weather Dashboard</h1>
            {stats && (
              <p className="dashboard__subtitle">
                {stats.total_records.toLocaleString()} readings •
                {stats.date_range_days ? ` ${stats.date_range_days} days` : ' No data'}
              </p>
            )}
          </div>
          <div className="dashboard__actions">
            <DeviceManager />
            <InstallPrompt />
            <button
              onClick={handleResetAllLayouts}
              className="dashboard__button dashboard__button--secondary"
              aria-label="Reset dashboard layout to default order"
            >
              Reset Layout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content - Skip link target */}
      <main id="main-content" className="dashboard__main">
        {/* Backfill in progress indicator */}
        {isBackfilling && (
          <BackfillStatusBanner onComplete={() => setIsBackfilling(false)} />
        )}

        {/* Empty State - only show if not backfilling and no data */}
        {stats && stats.total_records === 0 && !isBackfilling && (
          <div className="dashboard__empty">
            <h2 className="dashboard__empty-title">No Weather Data Yet</h2>
            <p className="dashboard__empty-text">
              Your weather dashboard is ready, but there's no data to display yet.
            </p>
            <button
              onClick={() => setShowOnboarding(true)}
              className="dashboard__button dashboard__button--primary"
            >
              Connect Weather Station
            </button>
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

        {/* Historical Conditions (Date Range + Charts) */}
        <HistoricalConditions
          dateRange={dateRange}
          historicalData={historicalData}
          chartOrder={chartOrder}
          onDateRangeChange={handleDateRangeChange}
          onExportCSV={handleExportCSV}
          onChartReorder={setChartOrder}
        />
      </main>
    </div>
  );
}
