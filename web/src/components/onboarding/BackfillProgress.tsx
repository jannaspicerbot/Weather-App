/**
 * Backfill Progress Component
 *
 * Shows real-time progress of the data backfill process.
 * Updates every minute with estimated time remaining.
 */

import { useState, useEffect, useCallback } from 'react';
import {
  getBackfillProgress,
  formatTimeRemaining,
  type DeviceInfo,
  type BackfillProgress as BackfillProgressType,
} from '../../services/onboardingApi';

interface BackfillProgressProps {
  devices: DeviceInfo[];
  onComplete: () => void;
}

export default function BackfillProgress({
  devices,
  onComplete,
}: BackfillProgressProps) {
  const [progress, setProgress] = useState<BackfillProgressType | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  const fetchProgress = useCallback(async () => {
    try {
      const data = await getBackfillProgress();
      setProgress(data);
      setLastUpdate(new Date());
      setError(null);

      // Note: User must click the button to proceed to dashboard
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get progress');
    }
  }, [onComplete]);

  useEffect(() => {
    // Initial fetch
    fetchProgress();

    // Poll for updates - more frequently at first, then every minute
    const quickInterval = setInterval(fetchProgress, 2000); // Every 2 seconds initially

    // After 30 seconds, switch to minute updates
    const switchToMinuteUpdates = setTimeout(() => {
      clearInterval(quickInterval);
      const minuteInterval = setInterval(fetchProgress, 60000);
      return () => clearInterval(minuteInterval);
    }, 30000);

    return () => {
      clearInterval(quickInterval);
      clearTimeout(switchToMinuteUpdates);
    };
  }, [fetchProgress]);

  // Calculate progress percentage
  const getProgressPercentage = (): number => {
    if (!progress) return 0;
    if (progress.status === 'completed') return 100;

    // Estimate based on requests made vs estimated total
    // ~730 requests for 2 years of data (288 records/day)
    const estimatedTotalRequests = 730;
    const pct = Math.min(
      (progress.requests_made / estimatedTotalRequests) * 100,
      99
    );
    return Math.round(pct);
  };

  const progressPct = getProgressPercentage();

  return (
    <div className="space-y-6">
      {/* Device info */}
      {devices.length > 0 && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center">
            <svg
              className="w-5 h-5 text-green-500 mr-2"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
            <span className="text-green-800 font-medium">
              Connected to {devices[0]?.name || 'Weather Station'}
            </span>
          </div>
        </div>
      )}

      {/* Error state */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
          <button
            onClick={fetchProgress}
            className="mt-2 text-red-600 underline hover:text-red-800"
          >
            Retry
          </button>
        </div>
      )}

      {/* Progress status */}
      {progress && (
        <div className="space-y-4">
          {/* Status message */}
          <div className="text-center">
            <p className="text-gray-600 mb-2">{progress.message}</p>
            {progress.status === 'in_progress' &&
              progress.estimated_time_remaining_seconds !== null && (
                <p className="text-sm text-gray-500">
                  {formatTimeRemaining(progress.estimated_time_remaining_seconds)}
                </p>
              )}
          </div>

          {/* Progress bar */}
          <div className="relative pt-1">
            <div className="flex mb-2 items-center justify-between">
              <div>
                <span
                  className={`text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full ${
                    progress.status === 'completed'
                      ? 'text-green-600 bg-green-200'
                      : progress.status === 'failed'
                      ? 'text-red-600 bg-red-200'
                      : 'text-blue-600 bg-blue-200'
                  }`}
                >
                  {progress.status === 'completed'
                    ? 'Complete'
                    : progress.status === 'failed'
                    ? 'Failed'
                    : 'Loading Data'}
                </span>
              </div>
              <div className="text-right">
                <span className="text-xs font-semibold inline-block text-gray-600">
                  {progressPct}%
                </span>
              </div>
            </div>
            <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-gray-200">
              <div
                style={{ width: `${progressPct}%` }}
                className={`shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center transition-all duration-500 ${
                  progress.status === 'completed'
                    ? 'bg-green-500'
                    : progress.status === 'failed'
                    ? 'bg-red-500'
                    : 'bg-blue-500'
                }`}
              />
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 gap-4 text-center">
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-2xl font-bold text-gray-900">
                {progress.inserted_records.toLocaleString()}
              </p>
              <p className="text-sm text-gray-500">Records Added</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-2xl font-bold text-gray-900">
                {progress.requests_made}
              </p>
              <p className="text-sm text-gray-500">API Requests</p>
            </div>
          </div>

          {/* Date range being processed */}
          {progress.start_date && progress.end_date && (
            <div className="text-center text-sm text-gray-500">
              <p>
                Fetching data from {progress.start_date} to {progress.end_date}
              </p>
              {progress.current_date && (
                <p className="mt-1">
                  Currently processing: {progress.current_date}
                </p>
              )}
            </div>
          )}

          {/* Completed state */}
          {progress.status === 'completed' && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
              <svg
                className="w-12 h-12 text-green-500 mx-auto mb-3"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <h3 className="text-lg font-semibold text-green-800 mb-1">
                All Set!
              </h3>
              <p className="text-green-700 mb-4">
                Your weather data has been loaded successfully.
              </p>
              <button
                onClick={onComplete}
                className="w-full py-3 px-4 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors"
              >
                Go to Dashboard
              </button>
            </div>
          )}

          {/* Last update time */}
          <p className="text-xs text-gray-400 text-center">
            Last updated: {lastUpdate.toLocaleTimeString()}
          </p>
        </div>
      )}

      {/* Loading state if no progress yet */}
      {!progress && !error && (
        <div className="text-center py-8">
          <svg
            className="animate-spin h-8 w-8 text-blue-500 mx-auto mb-4"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          <p className="text-gray-600">Starting data sync...</p>
        </div>
      )}

      {/* Info note */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-sm text-gray-600">
        <p className="font-medium mb-1">What's happening?</p>
        <ul className="list-disc list-inside space-y-1 text-gray-500">
          <li>Fetching current weather data first</li>
          <li>Then loading up to 2 years of historical data</li>
          <li>You can start using the dashboard while this runs</li>
          <li>Data will appear as it's downloaded</li>
        </ul>
      </div>

      {/* Skip/Continue button */}
      {progress && progress.status === 'in_progress' && progress.inserted_records > 0 && (
        <button
          onClick={onComplete}
          className="w-full py-2 px-4 text-blue-600 border border-blue-300 rounded-lg hover:bg-blue-50 transition-colors"
        >
          Continue to Dashboard (backfill will continue in background)
        </button>
      )}
    </div>
  );
}
