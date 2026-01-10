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
  }, []);

  useEffect(() => {
    // Use IIFE to avoid direct setState in effect body
    void (async () => {
      await fetchProgress();
    })();

    // Poll for updates - more frequently at first, then every minute
    const quickInterval = setInterval(() => void fetchProgress(), 2000); // Every 2 seconds initially

    // After 30 seconds, switch to minute updates
    const switchToMinuteUpdates = setTimeout(() => {
      clearInterval(quickInterval);
      const minuteInterval = setInterval(() => void fetchProgress(), 60000);
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
    <div className="backfill-progress">
      {/* Device info */}
      {devices.length > 0 && (
        <div className="backfill-progress__device">
          <span className="backfill-progress__device-icon">
            <svg
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
          </span>
          <span className="backfill-progress__device-text">
            Connected to {devices[0]?.name || 'Weather Station'}
          </span>
        </div>
      )}

      {/* Error state */}
      {error && (
        <div className="backfill-progress__error">
          <p className="backfill-progress__error-text">{error}</p>
          <button
            onClick={fetchProgress}
            className="backfill-progress__error-retry"
          >
            Retry
          </button>
        </div>
      )}

      {/* Progress status */}
      {progress && (
        <div className="backfill-progress">
          {/* Status message */}
          <div className="backfill-progress__status">
            <p className="backfill-progress__message">{progress.message}</p>
            {progress.status === 'in_progress' &&
              progress.estimated_time_remaining_seconds !== null && (
                <p className="backfill-progress__time">
                  {formatTimeRemaining(progress.estimated_time_remaining_seconds)}
                </p>
              )}
          </div>

          {/* Progress bar */}
          <div className="backfill-progress__bar-container">
            <div className="backfill-progress__bar-header">
              <span
                className={`backfill-progress__bar-label ${
                  progress.status === 'completed'
                    ? 'backfill-progress__bar-label--complete'
                    : progress.status === 'failed'
                    ? 'backfill-progress__bar-label--failed'
                    : 'backfill-progress__bar-label--loading'
                }`}
              >
                {progress.status === 'completed'
                  ? 'Complete'
                  : progress.status === 'failed'
                  ? 'Failed'
                  : 'Loading Data'}
              </span>
              <span className="backfill-progress__bar-percent">
                {progressPct}%
              </span>
            </div>
            <div className="backfill-progress__bar">
              <div
                style={{ width: `${progressPct}%` }}
                className={`backfill-progress__bar-fill ${
                  progress.status === 'completed'
                    ? 'backfill-progress__bar-fill--complete'
                    : progress.status === 'failed'
                    ? 'backfill-progress__bar-fill--failed'
                    : 'backfill-progress__bar-fill--loading'
                }`}
              />
            </div>
          </div>

          {/* Stats */}
          <div className="backfill-progress__stats">
            <div className="backfill-progress__stat">
              <p className="backfill-progress__stat-value">
                {progress.inserted_records.toLocaleString()}
              </p>
              <p className="backfill-progress__stat-label">Records Added</p>
            </div>
            <div className="backfill-progress__stat">
              <p className="backfill-progress__stat-value">
                {progress.requests_made}
              </p>
              <p className="backfill-progress__stat-label">API Requests</p>
            </div>
          </div>

          {/* Date range being processed */}
          {progress.start_date && progress.end_date && (
            <div className="backfill-progress__dates">
              <p>
                Fetching data from {progress.start_date} to {progress.end_date}
              </p>
              {progress.current_date && (
                <p>
                  Currently processing: {progress.current_date}
                </p>
              )}
            </div>
          )}

          {/* Completed state */}
          {progress.status === 'completed' && (
            <div className="backfill-progress__complete">
              <div className="backfill-progress__complete-icon">
                <svg
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
              </div>
              <h3 className="backfill-progress__complete-title">
                All Set!
              </h3>
              <p className="backfill-progress__complete-message">
                Your weather data has been loaded successfully.
              </p>
              <button
                onClick={onComplete}
                className="backfill-progress__complete-button"
              >
                Go to Dashboard
              </button>
            </div>
          )}

          {/* Last update time */}
          <p className="backfill-progress__updated">
            Last updated: {lastUpdate.toLocaleTimeString()}
          </p>
        </div>
      )}

      {/* Loading state if no progress yet */}
      {!progress && !error && (
        <div className="backfill-progress__loading">
          <div className="backfill-progress__loading-spinner">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
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
          </div>
          <p className="backfill-progress__loading-text">Starting data sync...</p>
        </div>
      )}

      {/* Info note */}
      <div className="backfill-progress__info">
        <p className="backfill-progress__info-title">What's happening?</p>
        <ul className="backfill-progress__info-list">
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
          className="backfill-progress__continue"
        >
          Continue to Dashboard (backfill will continue in background)
        </button>
      )}
    </div>
  );
}
